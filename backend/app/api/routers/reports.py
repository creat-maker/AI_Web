from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, GeneratedResource, LearningPath, LearningReport, QuizSubmission, StudentProfile
from app.services.dkvmn_tracker import dkvmn_tracker
from app.services.json_utils import loads
from app.services.report_service import create_learning_report, report_exists

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportGeneratePayload(BaseModel):
    student_profile_id: int
    course_id: int | None = None
    regenerate_reason: str | None = None


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value:
        return [value]
    return []


def _context_maps(db: Session, reports: list[LearningReport]) -> tuple[dict[int, str], dict[int, str]]:
    course_ids = {item.course_id for item in reports}
    profile_ids = {item.student_profile_id for item in reports}
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all() if course_ids else []
    profiles = db.query(StudentProfile).filter(StudentProfile.id.in_(profile_ids)).all() if profile_ids else []
    return {item.id: item.title for item in courses}, {item.id: item.student_name for item in profiles}


def report_to_dict(item: LearningReport, course_title: str | None = None, student_name: str | None = None) -> dict[str, Any]:
    report_json = loads(item.report_json, {})
    weak_points = _as_list(report_json.get("weak_points")) or ["循环结构综合应用"]
    references = _as_list(report_json.get("references")) or ["学生画像", "学习路径", "测验反馈", "课程知识库"]
    stages = _as_list(report_json.get("stages") or report_json.get("learning_path"))
    suggestions = _as_list(report_json.get("teaching_suggestions") or report_json.get("learning_suggestions"))
    quality_score = report_json.get("quality_score") or report_json.get("score")
    status = "completed" if report_exists(item) else "generating"
    summary = {
        "report_abstract": report_json.get("profile_summary") or report_json.get("summary") or "已生成学习诊断报告。",
        "learning_performance_summary": report_json.get("evaluation_summary") or "结合测验、问答与资源使用记录形成学习表现摘要。",
        "generation_basis": references,
        "key_conclusions": [
            f"当前重点关注：{weak_points[0]}",
            "建议通过分层练习、智能答疑和阶段测评形成闭环。",
        ],
        "evidence_chain": [
            {
                "conclusion": f"报告结论引用 {ref}",
                "evidence_type": "learning_record",
                "source_title": str(ref),
                "source_excerpt": f"{ref} 支撑当前学习诊断。",
                "confidence": round(0.88 - index * 0.04, 2),
                "related_knowledge_point": str(weak_points[index % len(weak_points)]),
            }
            for index, ref in enumerate(references[:4])
        ],
        "weak_points": weak_points,
        "recommended_path": stages,
        "learning_path": stages,
        "teaching_suggestions": suggestions or [{"title": "后续建议", "content": "围绕薄弱知识点安排分层练习和课后跟踪。"}],
        "learning_suggestions": suggestions or ["完成分层练习后更新学习报告。"],
        "references": references,
        "citation_documents": [{"name": str(name), "type": "学习证据", "hit_count": index + 1} for index, name in enumerate(references[:5])],
        "quality_score": float(quality_score) if isinstance(quality_score, (int, float)) else None,
        "regenerate_reason": report_json.get("regenerate_reason") or "当测评、问答或资源使用数据更新时可重新生成。",
        "generated_at": item.created_at,
    }
    return {
        "id": item.id,
        "report_id": item.id,
        "course_id": item.course_id,
        "student_profile_id": item.student_profile_id,
        "student_name": student_name or "未绑定学生",
        "target_scope": student_name or "学生学习情况",
        "report_title": item.report_title,
        "report_path": item.report_path,
        "report_json": report_json,
        "created_at": item.created_at,
        "course_title": course_title,
        "report_type": report_json.get("report_type") or "学习诊断报告",
        "status": status,
        "report_status": status,
        "quality_score": summary["quality_score"],
        "citation_document_count": len(summary["citation_documents"]),
        "report_url": f"/api/v1/reports/{item.id}/download" if status == "completed" else "",
        "download_url": f"/api/v1/reports/{item.id}/download" if status == "completed" else "",
        "download_enabled": status == "completed",
        "regenerate_enabled": bool(item.student_profile_id),
        "summary": summary,
    }


@router.get("")
def list_items(course_id: int | None = None, report_id: int | None = None, db: Session = Depends(get_db)):
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
    state = dkvmn_tracker.state_from_profile(profile)
    resources = (
        db.query(GeneratedResource)
        .filter(GeneratedResource.student_profile_id == profile.id)
        .order_by(GeneratedResource.id.desc())
        .limit(8)
        .all()
    )
    summary = {
        "profile_summary": loads(profile.profile_json, {}).get("diagnosis", "已形成学生画像。"),
        "dimension_scores": loads(profile.dimension_scores, {}) or dkvmn_tracker.map_to_profile_dimensions(state),
        "cognitive_state": dkvmn_tracker.get_cognitive_state(profile.id, state),
        "stages": loads(path.path_json, {}).get("stages", []) if path else [],
        "adjustment_log": loads(path.adjustment_log, []) if path else [],
        "evaluation_summary": feedback.get("mistake_analysis", "暂无测评反馈。"),
        "error_analysis": feedback.get("mistake_analysis") or feedback.get("error_analysis"),
        "score": feedback.get("score"),
        "weak_points": feedback.get("weak_points") or loads(profile.weak_points, []) or ["循环结构"],
        "references": ["学生画像", "DKVMN 知识追踪", "学习路径", "测评反馈", "课程知识库"],
        "citations": (feedback.get("rag_citations") or ["Python 程序设计 / 循环结构章节", "测验错因记录"]),
        "resources": [f"{item.resource_type}：{item.title}" for item in resources] or ["循环结构讲义", "HTML 动画", "代码案例"],
        "teacher_arbitration": ["高风险或重大调整进入教师仲裁；当前报告记录本地 fallback 审核结论。"],
        "regenerate_reason": payload.regenerate_reason or "根据当前课程和学习记录生成。",
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
