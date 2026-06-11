from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_demo_user_id
from app.db.session import get_db
from app.models import Course, TutorQuestionLog
from app.services.business_event_service import record_event
from app.services.demo_profile_chain import normalize_profile_schema
from app.rag.retriever import retrieve_course_context
from app.services.json_utils import dumps, loads
from app.services.llm_service import llm_service
from app.services.profile_service import latest_profile_by_user_id, profile_to_dict


router = APIRouter(prefix="/tutor", tags=["tutor"])


class TutorPayload(BaseModel):
    course_id: int
    question: str
    user_id: str | None = None
    top_k: int = 3
    heuristic_mode: bool = True
    no_direct_answer: bool = False
    hint_level: str = "medium"


def _citation_cards(contexts: list[dict]) -> list[dict]:
    return [
        {
            "document_name": item.get("source_file") or f"知识库文档 #{item.get('document_id', '-')}",
            "snippet": item.get("content", ""),
            "relevance": item.get("score", 0),
            "confidence": item.get("confidence", round(float(item.get("score") or 0.5), 4)),
            "document_id": item.get("document_id"),
        }
        for item in contexts
    ]


def _follow_up_suggestions(question: str) -> list[str]:
    return [
        "这道题涉及的前置概念是什么？",
        "能不能给我一个相似但更简单的例题？",
        "我应该如何检查自己的解题步骤？",
    ] if question else []


def _compute_confidence(contexts: list[dict]) -> tuple[float, str, dict]:
    """计算整体 confidence 统计"""
    scores = [float(item.get("score") or 0) for item in contexts]
    if not scores:
        return 0, "low", {"avg": 0, "max": 0, "min": 0, "count": 0}
    avg = round(sum(scores) / len(scores), 4)
    max_s = round(max(scores), 4)
    min_s = round(min(scores), 4)
    if avg >= 0.7:
        level = "high"
    elif avg >= 0.4:
        level = "medium"
    else:
        level = "low"
    return avg, level, {"avg": avg, "max": max_s, "min": min_s, "count": len(scores)}


def _teaching_profile(question: str, contexts: list[dict], hint_level: str, no_direct_answer: bool) -> dict:
    text = question.lower()
    if any(token in text for token in ["为什么", "区别", "概念", "理解", "difference"]):
        misconception = "概念混淆"
        strategy = "先辨析概念边界，再用一个反例或对比例题确认理解。"
    elif any(token in text for token in ["计算", "公式", "复杂度", "score", "复杂"]):
        misconception = "计算错误"
        strategy = "先拆出公式和步骤，再检查每一步的输入输出。"
    elif any(token in text for token in ["题目", "审题", "要求", "条件"]):
        misconception = "审题错误"
        strategy = "先圈出已知条件、目标和限制，再选择知识点。"
    else:
        misconception = "知识缺漏" if not contexts else "概念混淆"
        strategy = "先补齐前置知识，再通过小例题迁移到原问题。"

    hint_map = {
        "light": "轻提示：先说出你认为要用到的核心概念。",
        "medium": "中提示：把问题拆成已知条件、目标、可用知识点三步。",
        "detailed": "详细解释：先复述概念，再给出步骤化示例，最后让学生复盘关键点。",
    }
    normalized_hint = hint_level if hint_level in hint_map else "medium"
    mastery_delta = 0.04 + min(len(contexts), 5) * 0.015
    if no_direct_answer:
        mastery_delta += 0.02
    return {
        "teaching_strategy": strategy,
        "hint_level": normalized_hint,
        "hint_text": hint_map[normalized_hint],
        "detected_misconception": misconception,
        "mastery_delta": round(mastery_delta, 2),
        "guiding_questions": [
            "你能先指出题目中的已知条件吗？",
            "这个问题最可能对应哪个知识点？",
            "如果换一个相似例子，你会先做哪一步？",
        ],
        "demo_fallback_note": "教学策略、错因识别和掌握度变化为规则估计，未伪装为真实大模型诊断。",
    }


@router.post("/ask")
def ask(payload: TutorPayload, db: Session = Depends(get_db), current_user_id: str = Depends(get_demo_user_id)):
    active_user_id = payload.user_id or current_user_id
    stored_profile = latest_profile_by_user_id(db, active_user_id, payload.course_id)
    profile = normalize_profile_schema(profile_to_dict(stored_profile) if stored_profile else None, active_user_id)
    contexts = retrieve_course_context(payload.course_id, payload.question, payload.top_k)

    # 为每个 context 增加 confidence
    enriched_contexts = [
        {**item, "confidence": round(float(item.get("score") or 0.5), 4)} for item in contexts
    ]

    answer = llm_service.generate_json("tutor", {"question": payload.question, "contexts": enriched_contexts})
    teaching_profile = _teaching_profile(payload.question, enriched_contexts, payload.hint_level, payload.no_direct_answer)
    if payload.no_direct_answer:
        raw_answer = answer.get("answer") if isinstance(answer, dict) else ""
        answer = {
            **(answer if isinstance(answer, dict) else {}),
            "answer": f"先不直接给最终答案。{teaching_profile['hint_text']} 你可以先回答：{teaching_profile['guiding_questions'][0]} 参考提示：{raw_answer}",
            "guidance_mode": "heuristic_no_direct_answer",
        }
    elif payload.heuristic_mode and isinstance(answer, dict):
        answer.setdefault("guidance_mode", "heuristic")
    if isinstance(answer, dict):
        answer.update(teaching_profile)
        answer["related_weak_points"] = profile["weak_points"]
        answer["recommended_resources"] = profile["resource_preference"].split("、")
        answer["profile_used"] = True

    # 计算整体 confidence
    confidence, confidence_level, confidence_breakdown = _compute_confidence(enriched_contexts)

    mode = llm_service.runtime_mode
    stored_mode = f"{mode}-guided" if payload.heuristic_mode else mode
    log = TutorQuestionLog(
            course_id=payload.course_id,
            question=payload.question,
            answer_json=dumps(answer),
            contexts_json=dumps(enriched_contexts),
            mode=stored_mode,
        )
    db.add(log)
    db.flush()
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    record_event(
        db,
        event_type="question_answered",
        title="智能答疑完成",
        description=f"问题已回答并记录 {len(enriched_contexts)} 条引用来源。",
        actor_role="student",
        actor_name="demo_student",
        target_type="tutor_question",
        target_id=log.id,
        related_course=course.title if course else "",
        status="answered",
        metadata={
            "question": payload.question,
            "citation_count": len(enriched_contexts),
            "confidence": confidence,
            "confidence_level": confidence_level,
            "weak_point_impact": teaching_profile.get("detected_misconception"),
            "user_id": active_user_id,
            "related_weak_points": profile["weak_points"],
            "recommended_resource": "分层练习题",
            "path_suggestion": "将本次答疑知识点加入下一阶段复盘。",
        },
        commit=False,
    )
    db.commit()
    return {
        "answer": answer,
        "retrieved_context": enriched_contexts,
        "citation_sources": _citation_cards(enriched_contexts),
        "follow_up_suggestions": _follow_up_suggestions(payload.question),
        **teaching_profile,
        "based_on_material": bool(enriched_contexts),
        "confidence": confidence,
        "confidence_level": confidence_level,
        "confidence_breakdown": confidence_breakdown,
        "related_weak_points": profile["weak_points"],
        "recommended_resources": profile["resource_preference"].split("、"),
        "profile_used": True,
        "profile": profile,
        "mode": stored_mode,
    }


@router.get("/history")
def history(course_id: int | None = None, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(TutorQuestionLog)
    if course_id:
        query = query.filter(TutorQuestionLog.course_id == course_id)
    items = query.order_by(TutorQuestionLog.created_at.desc()).limit(min(max(limit, 1), 100)).all()
    rows = []
    for item in items:
        answer = loads(item.answer_json, {})
        contexts = loads(item.contexts_json, [])
        confidence, confidence_level, confidence_breakdown = _compute_confidence(contexts)
        rows.append(
            {
                "id": item.id,
                "course_id": item.course_id,
                "question": item.question,
                "answer": answer,
                "retrieved_context": contexts,
                "citation_sources": _citation_cards(contexts),
                "follow_up_suggestions": _follow_up_suggestions(item.question),
                "teaching_strategy": answer.get("teaching_strategy"),
                "hint_level": answer.get("hint_level"),
                "detected_misconception": answer.get("detected_misconception"),
                "mastery_delta": answer.get("mastery_delta"),
                "based_on_material": bool(contexts),
                "confidence": confidence,
                "confidence_level": confidence_level,
                "confidence_breakdown": confidence_breakdown,
                "mode": item.mode,
                "created_at": item.created_at,
            }
        )
    return rows
