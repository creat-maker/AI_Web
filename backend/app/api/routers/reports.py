from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, LearningPath, LearningReport, QuizSubmission, StudentProfile
from app.services.json_utils import loads
from app.services.report_service import create_learning_report, report_exists


router = APIRouter(prefix="/reports", tags=["reports"])


class ReportGeneratePayload(BaseModel):
    student_profile_id: int
    course_id: int | None = None
    regenerate_reason: str | None = None


def _short(value: Any, fallback: str = "暂无", limit: int = 180) -> str:
    if value is None:
        return fallback
    text = value if isinstance(value, str) else str(value)
    text = text.strip() or fallback
    return text if len(text) <= limit else f"{text[:limit]}..."


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value:
        return [value]
    return []


def _report_type(report_json: dict) -> str:
    if report_json.get("source") == "agent_workflow" or report_json.get("agent_run_id"):
        return "Agent 工作流报告"
    return "个性化学习报告"


def _quality_score(report_json: dict) -> float | None:
    score = report_json.get("score") or report_json.get("quality_score")
    if isinstance(score, (int, float)):
        return round(float(score), 1)
    return None


def _evidence_chain(report_json: dict, references: list[Any], weak_points: list[Any], contexts_confidence: list[float] | None = None) -> list[dict[str, Any]]:
    evidence_types = ["document", "quiz", "chat", "mastery", "agent_run"]
    # 如果有真实 confidence 数据，优先使用，否则使用降序假数据
    base_confidences = contexts_confidence or [0.88, 0.82, 0.76]
    conclusions = [
        {
            "conclusion": _short(report_json.get("profile_summary") or report_json.get("summary"), "学生当前学习表现需要结合测评和问答继续观察。"),
            "related_knowledge_point": str(weak_points[0]) if weak_points else "综合表现",
        },
        {
            "conclusion": f"薄弱知识点集中在 {', '.join(str(item) for item in weak_points[:3])}" if weak_points else "薄弱知识点待补充测评后确认。",
            "related_knowledge_point": str(weak_points[0]) if weak_points else "待诊断知识点",
        },
        {
            "conclusion": "建议通过分层练习、追问式答疑和阶段复盘形成学习闭环。",
            "related_knowledge_point": str(weak_points[1]) if len(weak_points) > 1 else "学习策略",
        },
    ]
    return [
        {
            "conclusion": item["conclusion"],
            "evidence_type": evidence_types[index % len(evidence_types)],
            "source_title": str(references[index % len(references)]) if references else "EduMind demo/fallback evidence",
            "source_excerpt": f"该证据用于支撑结论：{item['conclusion']}",
            "confidence": base_confidences[index] if index < len(base_confidences) else round(0.88 - index * 0.06, 2),
            "related_knowledge_point": item["related_knowledge_point"],
            "demo_fallback_note": "证据链为基于报告 JSON、测评和问答记录的轻量演示结构，后续可接真实引用追踪。",
        }
        for index, item in enumerate(conclusions)
    ]


def _summary(report_json: dict, item: LearningReport) -> dict[str, Any]:
    stages = _as_list(report_json.get("stages"))
    evaluation = report_json.get("evaluation_summary") or report_json.get("mistake_analysis")
    weak_points = _as_list(report_json.get("weak_points")) or [_short(evaluation, "暂无明确薄弱知识点。")]
    references = _as_list(report_json.get("references")) or [
        "学生画像",
        "学习路径",
        "测评反馈",
        "TutorChat 问答历史",
        "AgentWorkflow 运行结果" if report_json.get("agent_run_id") else "课程知识库",
    ]
    suggestions = _as_list(report_json.get("teaching_suggestions"))
    # 从 report_json 中提取 contexts confidence（如有）
    contexts_confidence: list[float] | None = None
    if "retrieved_contexts" in report_json:
        contexts_confidence = [float(item.get("confidence") or item.get("score") or 0.5) for item in report_json["retrieved_contexts"]]
    evidence_chain = _evidence_chain(report_json, references, weak_points, contexts_confidence)

    return {
        "report_abstract": _short(
            report_json.get("profile_summary") or report_json.get("summary"),
            "已生成学习报告，可继续结合测评和问答记录完善。",
            220,
        ),
        "learning_performance_summary": _short(
            report_json.get("profile_summary") or report_json.get("summary"),
            "已生成学习报告，可结合学习路径和测评反馈继续完善。",
            220,
        ),
        "generation_basis": ["学生画像", "课程知识库", "测评结果", "TutorChat 问答历史", "AgentWorkflow 运行记录"],
        "key_conclusions": [entry["conclusion"] for entry in evidence_chain],
        "evidence_chain": evidence_chain,
        "weak_points": weak_points,
        "recommended_path": [
            {
                "name": stage.get("name") or stage.get("title") or f"阶段 {index + 1}",
                "target": stage.get("target") or stage.get("content") or "继续完成当前学习目标。",
                "recommend_reason": stage.get("recommend_reason") or f"基于薄弱点分析，推荐进入「{stage.get('name') or stage.get('title') or f'阶段 {index + 1}'}」阶段。",
            }
            for index, stage in enumerate(stages[:4])
            if isinstance(stage, dict)
        ],
        "learning_path": [
            {
                "step": stage.get("name") or stage.get("title") or f"阶段 {index + 1}",
                "goal": stage.get("target") or stage.get("content") or "继续完成当前学习目标。",
                "recommend_reason": stage.get("recommend_reason") or f"基于薄弱点分析，推荐进入「{stage.get('name') or stage.get('title') or f'阶段 {index + 1}'}」阶段。",
            }
            for index, stage in enumerate(stages[:4])
            if isinstance(stage, dict)
        ],
        "teaching_suggestions": suggestions
        or [{"title": "下一步教学建议", "content": _short(evaluation, "围绕薄弱知识点安排分层练习。")}],
        "learning_suggestions": [
            entry.get("content", "") if isinstance(entry, dict) else str(entry)
            for entry in suggestions[:4]
        ]
        or ["围绕薄弱知识点安排分层练习，并在下一次问答或测评后更新报告。"],
        "references": references,
        "citation_documents": [
            {"name": str(name), "type": "demo/fallback", "hit_count": index + 1}
            for index, name in enumerate(references[:5])
        ],
        "citation_snippets": [
            {
                "document": str(name),
                "content": f"{name} 支撑了本报告中的诊断、建议或学习路径生成。",
                "confidence": round(0.86 - index * 0.04, 2),
            }
            for index, name in enumerate(references[:4])
        ],
        "quality_score": _quality_score(report_json),
        "regenerate_reason": report_json.get("regenerate_reason") or "当测评结果、问答历史或知识库资料更新时可重新生成。",
        "generated_at": item.created_at,
    }


def report_to_dict(item: LearningReport, course_title: str | None = None, student_name: str | None = None) -> dict[str, Any]:
    report_json = loads(item.report_json, {})
    exists = report_exists(item)
    status = "completed" if exists else "generating"
    summary = _summary(report_json, item)
    return {
        "id": item.id,
        "report_id": item.id,
        "course_id": item.course_id,
        "student_profile_id": item.student_profile_id,
        "student_name": student_name or "未绑定学生",
        "target_scope": student_name or "班级/学生未指定",
        "report_title": item.report_title,
        "report_path": item.report_path,
        "report_json": report_json,
        "created_at": item.created_at,
        "course_title": course_title,
        "report_type": _report_type(report_json),
        "status": status,
        "report_status": status,
        "quality_score": _quality_score(report_json),
        "citation_document_count": len(summary.get("citation_documents", [])),
        "report_url": f"/api/v1/reports/{item.id}/download" if exists else "",
        "download_url": f"/api/v1/reports/{item.id}/download" if exists else "",
        "download_enabled": exists,
        "regenerate_enabled": bool(item.student_profile_id),
        "summary": summary,
    }


def _context_maps(db: Session, reports: list[LearningReport]) -> tuple[dict[int, str], dict[int, str]]:
    course_ids = {item.course_id for item in reports}
    profile_ids = {item.student_profile_id for item in reports}
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all() if course_ids else []
    profiles = db.query(StudentProfile).filter(StudentProfile.id.in_(profile_ids)).all() if profile_ids else []
    return {item.id: item.title for item in courses}, {item.id: item.student_name for item in profiles}


@router.get("")
def list_items(
    course_id: int | None = None,
    report_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(LearningReport)
    if course_id:
        query = query.filter(LearningReport.course_id == course_id)
    if report_id:
        query = query.filter(LearningReport.id == report_id)
    items = query.order_by(LearningReport.id.desc()).all()
    course_titles, profile_names = _context_maps(db, items)
    return [report_to_dict(item, course_titles.get(item.course_id), profile_names.get(item.student_profile_id)) for item in items]


@router.get("/summary")
def report_summary(db: Session = Depends(get_db)):
    reports = db.query(LearningReport).all()
    since = datetime.utcnow() - timedelta(days=7)
    course_titles, profile_names = _context_maps(db, reports)
    rows = [report_to_dict(item, course_titles.get(item.course_id), profile_names.get(item.student_profile_id)) for item in reports]
    quality_scores = [item["quality_score"] for item in rows if item.get("quality_score") is not None]
    return {
        "report_count": len(rows),
        "weekly_new_count": sum(1 for item in reports if item.created_at >= since),
        "completed_count": sum(1 for item in rows if item.get("status") == "completed"),
        "average_quality_score": round(sum(quality_scores) / len(quality_scores), 1) if quality_scores else None,
    }


@router.post("/generate")
def generate_report(payload: ReportGeneratePayload, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.id == payload.student_profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="学生画像不存在")
    course_id = payload.course_id or profile.course_id
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    path = (
        db.query(LearningPath)
        .filter(LearningPath.student_profile_id == profile.id)
        .order_by(LearningPath.id.desc())
        .first()
    )
    submission = (
        db.query(QuizSubmission)
        .filter(QuizSubmission.student_profile_id == profile.id)
        .order_by(QuizSubmission.id.desc())
        .first()
    )
    feedback = loads(submission.feedback_json, {}) if submission else {}
    summary = {
        "profile_summary": loads(profile.profile_json, {}).get("diagnosis", "已生成学生画像。"),
        "stages": loads(path.path_json, {}).get("stages", []) if path else [],
        "evaluation_summary": feedback.get("mistake_analysis", "暂无测评反馈。"),
        "score": feedback.get("score"),
        "weak_points": feedback.get("weak_points") or loads(profile.weak_points, []),
        "references": ["学生画像", "学习路径", "测评反馈", "知识库引用"],
        "regenerate_reason": payload.regenerate_reason or "手动模拟重新生成。",
    }
    item = create_learning_report(db, profile, course, summary)
    return report_to_dict(item, course.title, profile.student_name)


@router.get("/{report_id}/download")
def download(report_id: int, db: Session = Depends(get_db)):
    report = db.query(LearningReport).filter(LearningReport.id == report_id).first()
    if not report or not report_exists(report):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    suffix = Path(report.report_path).suffix or ".docx"
    return FileResponse(report.report_path, filename=f"learning-report-{report_id}{suffix}")
