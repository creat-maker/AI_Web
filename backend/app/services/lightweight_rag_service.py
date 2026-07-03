from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from app.services.curriculum_constraint import check_curriculum_alignment
from app.services.demo_learning_service import get_demo_student
from app.services.embedding_interface import TfidfEmbeddingProvider


ROOT_DIR = Path(__file__).resolve().parents[3]
COURSE_KB_PATH = ROOT_DIR / "docs" / "course_kb" / "python_programming.json"
INSUFFICIENT_EVIDENCE_MESSAGE = "当前课程知识库依据不足，建议先查看循环结构章节或请教师复核。"


def _load_kb() -> dict[str, Any]:
    if not COURSE_KB_PATH.exists():
        return {"courseId": "python-programming", "courseName": "Python 程序设计", "chapters": []}
    return json.loads(COURSE_KB_PATH.read_text(encoding="utf-8"))


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z_]+|\d+|[\u4e00-\u9fff]{2,}", text.lower())
    important_terms = [
        "for",
        "while",
        "break",
        "continue",
        "循环",
        "循环结构",
        "循环嵌套",
        "死循环",
        "变量更新",
        "条件更新",
        "终止条件",
        "输出结果",
    ]
    lowered = text.lower()
    for term in important_terms:
        if term.lower() in lowered:
            tokens.append(term.lower())
    return list(dict.fromkeys(tokens))


def _chunks() -> list[dict[str, Any]]:
    kb = _load_kb()
    rows: list[dict[str, Any]] = []
    for chapter in kb.get("chapters", []):
        for section in chapter.get("sections", []):
            knowledge_points = section.get("knowledgePoints", [])
            exercises = section.get("exercises", [])
            content = "\n".join(
                [
                    section.get("lecture", ""),
                    " ".join(knowledge_points),
                    " ".join(exercises),
                    section.get("labTask", ""),
                ]
            )
            rows.append(
                {
                    "courseId": kb.get("courseId", "python-programming"),
                    "courseName": kb.get("courseName", "Python 程序设计"),
                    "sourceFile": section.get("sourceFile", "python_programming.json"),
                    "chapter": chapter.get("chapter", "循环结构"),
                    "section": section.get("section", "循环结构"),
                    "knowledgePoints": knowledge_points,
                    "lecture": section.get("lecture", ""),
                    "exercises": exercises,
                    "labTask": section.get("labTask", ""),
                    "content": content,
                }
            )
    return rows


def _score_chunk(question_tokens: list[str], chunk: dict[str, Any]) -> float:
    haystack = " ".join(
        [
            chunk.get("chapter", ""),
            chunk.get("section", ""),
            chunk.get("lecture", ""),
            chunk.get("labTask", ""),
            " ".join(chunk.get("knowledgePoints", [])),
            " ".join(chunk.get("exercises", [])),
        ]
    ).lower()
    score = 0.0
    for token in question_tokens:
        if token and token in haystack:
            score += 2.0 if len(token) >= 2 else 1.0
    for point in chunk.get("knowledgePoints", []):
        point_text = str(point).lower()
        if any(token in point_text for token in question_tokens):
            score += 1.5
    return score


def _hybrid_score(question: str, question_tokens: list[str], chunk: dict[str, Any], provider: TfidfEmbeddingProvider) -> dict[str, float]:
    lexical = _score_chunk(question_tokens, chunk)
    vector = provider.similarity(question, chunk.get("content", ""))
    is_exercise = bool(chunk.get("exercises"))
    non_practice_query = not any(token in question for token in ["练习", "题", "作业", "测验"])
    penalty = 0.82 if is_exercise and non_practice_query else 1.0
    fused = (lexical * 0.65 + vector * 8 * 0.35) * penalty
    return {"lexical_score": round(lexical, 4), "vector_score": round(vector, 4), "fusion_score": round(fused, 4)}


def _risk_from_confidence(confidence: float) -> str:
    if confidence >= 0.8:
        return "低"
    if confidence >= 0.5:
        return "中"
    return "高"


def _next_step(related_points: list[str], confidence: float) -> str:
    if confidence < 0.5:
        return "先查看循环结构章节，重点复习 while 循环条件更新，再请教师确认当前问题是否需要补充资料。"
    if any("while" in point.lower() or "条件" in point for point in related_points):
        return "建议优先完成 while 循环条件更新专项练习，并写出前三轮变量变化。"
    if any("嵌套" in point for point in related_points):
        return "建议用变量变化表复盘循环嵌套，再完成一个九九乘法表补全练习。"
    if any("break" in point.lower() or "continue" in point.lower() for point in related_points):
        return "建议完成 break / continue 输出判断题，重点区分跳出循环和跳过本轮。"
    return "建议先完成循环结构基础讲解，再进入代码实操练习。"


def ask_rag(question: str, course_id: str | int | None = None, student_id: str | int | None = None) -> dict[str, Any]:
    student = get_demo_student(student_id)
    profile_hint = " ".join(student.get("weak_points", [])[:3])
    tokens = _tokenize(f"{question} {profile_hint}")
    all_chunks = _chunks()
    provider = TfidfEmbeddingProvider()
    scored: list[tuple[float, dict[str, Any], dict[str, float]]] = []
    for chunk in all_chunks:
        scores = _hybrid_score(question, tokens, chunk, provider)
        if scores["fusion_score"] > 0:
            scored.append((scores["fusion_score"], chunk, scores))

    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[:5]
    total_score = sum(score for score, _, _ in top)
    confidence = round(min(0.95, 0.35 + math.log1p(total_score) / 3), 2) if top else 0.32
    low_evidence_risk = _risk_from_confidence(confidence)

    if not top and all_chunks:
        top = [(0.1, item, {"lexical_score": 0.1, "vector_score": 0.0, "fusion_score": 0.1}) for item in all_chunks[:2]]

    max_score = max((score for score, _, _ in top), default=1)
    matched = [
        {
            "score": round(score / max(max_score, 1), 3),
            "confidence": round(score / max(max_score, 1), 3),
            **scores,
            "sourceFile": chunk["sourceFile"],
            "source_file": chunk["sourceFile"],
            "chapter": chunk["chapter"],
            "section": chunk["section"],
            "section_title": chunk["section"],
            "page_number": None,
            "citation_id": f"{chunk['sourceFile']}-{index + 1:03d}",
            "snippet": chunk["lecture"][:180],
            "content": chunk["content"][:500],
            "knowledgePoints": chunk["knowledgePoints"],
        }
        for index, (score, chunk, scores) in enumerate(top)
    ]

    related_points: list[str] = []
    exercises: list[str] = []
    for _, chunk, _ in top:
        for point in chunk.get("knowledgePoints", []):
            if point not in related_points:
                related_points.append(point)
        for exercise in chunk.get("exercises", []):
            if exercise not in exercises:
                exercises.append(exercise)
        if chunk.get("labTask") and chunk["labTask"] not in exercises:
            exercises.append(chunk["labTask"])

    primary = top[0][1] if top else {
        "chapter": "循环结构",
        "section": "循环结构",
        "lecture": INSUFFICIENT_EVIDENCE_MESSAGE,
    }
    citations = [
        {
            "citation_id": item["citation_id"],
            "sourceFile": item["sourceFile"],
            "source_file": item["sourceFile"],
            "chapter": item["chapter"],
            "section": item["section"],
            "section_title": item["section"],
            "page_number": item["page_number"],
            "confidence": item["confidence"],
            "snippet": item["snippet"],
        }
        for item in matched
    ]
    evidence_summary = (
        f"已匹配 {len(citations)} 条课程资料，主要来自《Python 程序设计》{primary['chapter']} / {primary['section']}。"
        if confidence >= 0.5 and citations
        else INSUFFICIENT_EVIDENCE_MESSAGE
    )
    answer = (
        f"根据《Python 程序设计》{primary['chapter']}「{primary['section']}」的资料，"
        f"建议先理解 {related_points[0] if related_points else '循环结构'}。{primary['lecture']} "
        f"结合{student['student_name']}当前学习情况，下一步可以围绕{'、'.join(student['weak_points'][:2])}进行专项巩固。"
        if confidence >= 0.5
        else INSUFFICIENT_EVIDENCE_MESSAGE
    )

    curriculum_check = check_curriculum_alignment(
        f"{question} {answer}",
        evidence_items=citations,
        target_level=student.get("current_level") or "基础补弱",
    )
    suggested_actions = [
        _next_step(related_points, confidence),
        "查看引用片段并完成 2 道循环结构巩固题。",
    ]
    if curriculum_check["is_out_of_curriculum"]:
        suggested_actions.insert(0, "问题可能超出本课程范围，请先回到 Python 循环结构章节。")
    return {
        "question": question,
        "courseId": course_id or "python-programming",
        "studentId": student_id or "demo-basic",
        "studentName": student["student_name"],
        "profileType": student["profile_type"],
        "answer": answer,
        "citations": citations,
        "matchedChunks": matched,
        "confidence": confidence,
        "curriculum_alignment_score": curriculum_check["curriculum_alignment_score"],
        "alignment_breakdown": curriculum_check["alignment_breakdown"],
        "matched_objectives": curriculum_check["matched_objectives"],
        "out_of_scope_terms": curriculum_check["out_of_scope_terms"],
        "evidence_coverage_score": curriculum_check["evidence_coverage_score"],
        "retrieved_evidence_coverage": curriculum_check["retrieved_evidence_coverage"],
        "is_out_of_curriculum": curriculum_check["is_out_of_curriculum"],
        "boundary_warning": curriculum_check["boundary_warning"],
        "suggested_actions": list(dict.fromkeys([*suggested_actions, *curriculum_check.get("suggested_actions", [])])),
        "retrieval_debug": {
            "top_k": 5,
            "retrieval_mode": "hybrid-tfidf-json-fallback",
            "chroma_status": "fallback_json_keyword",
            "scores": [
                {
                    "citation_id": item["citation_id"],
                    "vector_score": item["vector_score"],
                    "lexical_score": item["lexical_score"],
                    "fusion_score": item["fusion_score"],
                }
                for item in matched
            ],
            "curriculum_check": curriculum_check,
            "json_fallback": True,
        },
        "lowEvidenceRisk": low_evidence_risk,
        "evidenceSummary": evidence_summary,
        "reviewSuggestion": "依据不足，建议教师补充循环结构章节资料或复核回答。" if low_evidence_risk == "高" else "依据相对充分，可结合课堂要求复核后使用。",
        "recommendedExercises": exercises[:5],
        "relatedKnowledgePoints": related_points[:8] or ["while 循环条件更新", "循环嵌套变量变化", "break / continue 区分"],
        "nextStep": _next_step(related_points, confidence),
        "retrievalMode": "hybrid-tfidf-json-fallback",
        "dataset": str(COURSE_KB_PATH.relative_to(ROOT_DIR)),
    }
