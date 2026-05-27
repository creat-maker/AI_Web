from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, LearningPath, LearningReport, QuizSubmission, StudentProfile
from app.services.json_utils import loads
from app.services.report_service import create_learning_report, report_exists


router = APIRouter(prefix="/reports", tags=["reports"])


class ReportGeneratePayload(BaseModel):
    student_profile_id: int
    course_id: int | None = None


def _short(value: Any, fallback: str = "暂无", limit: int = 120) -> str:
    if value is None:
        return fallback
    text = value if isinstance(value, str) else str(value)
    text = text.strip() or fallback
    return text if len(text) <= limit else f"{text[:limit]}..."


def _report_type(report_json: dict) -> str:
    if report_json.get("source") == "agent_workflow":
        return "智能体工作流报告"
    return "个性化学习报告"


def _quality_score(report_json: dict) -> float | None:
    score = report_json.get("score") or report_json.get("quality_score")
    if isinstance(score, (int, float)):
        return round(float(score), 1)
    return None


def _summary(report_json: dict, item: LearningReport) -> dict:
    stages = report_json.get("stages", []) or []
    evaluation = report_json.get("evaluation_summary") or report_json.get("mistake_analysis")
    return {
        "learning_performance_summary": _short(
            report_json.get("profile_summary") or report_json.get("summary"),
            "已生成学习报告，可结合学习路径和测评反馈继续完善。",
            180,
        ),
        "weak_points": report_json.get("weak_points") or _short(evaluation, "暂无明确薄弱点。", 160),
        "recommended_path": [
            {
                "name": stage.get("name") or stage.get("title") or f"阶段 {index + 1}",
                "target": stage.get("target") or stage.get("content") or "继续完成当前学习目标。",
            }
            for index, stage in enumerate(stages[:4])
            if isinstance(stage, dict)
        ],
        "teaching_suggestions": report_json.get("teaching_suggestions")
        or [
            {
                "title": "下一步教学建议",
                "content": _short(evaluation, "建议围绕薄弱知识点安排案例讲解和随堂练习。", 180),
            }
        ],
        "references": report_json.get("references")
        or [
            "学生画像",
            "学习路径",
            "测评反馈",
            "AgentWorkflow 运行结果" if report_json.get("agent_run_id") else "课程学习记录",
        ],
        "generated_at": item.created_at,
    }


def report_to_dict(item: LearningReport, course_title: str | None = None) -> dict:
    report_json = loads(item.report_json, {})
    exists = report_exists(item)
    status = "completed" if exists else "generating"
    quality_score = _quality_score(report_json)
    return {
        "id": item.id,
        "report_id": item.id,
        "course_id": item.course_id,
        "student_profile_id": item.student_profile_id,
        "report_title": item.report_title,
        "report_path": item.report_path,
        "report_json": report_json,
        "created_at": item.created_at,
        "course_title": course_title,
        "report_type": _report_type(report_json),
        "status": status,
        "report_status": status,
        "quality_score": quality_score,
        "report_url": f"/api/v1/reports/{item.id}/download" if exists else "",
        "download_url": f"/api/v1/reports/{item.id}/download" if exists else "",
        "summary": _summary(report_json, item),
    }


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
    course_ids = {item.course_id for item in items}
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all() if course_ids else []
    course_titles = {item.id: item.title for item in courses}
    return [report_to_dict(item, course_titles.get(item.course_id)) for item in items]


@router.get("/summary")
def report_summary(db: Session = Depends(get_db)):
    reports = db.query(LearningReport).all()
    since = datetime.utcnow() - timedelta(days=7)
    course_ids = {item.course_id for item in reports}
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all() if course_ids else []
    course_titles = {item.id: item.title for item in courses}
    rows = [report_to_dict(item, course_titles.get(item.course_id)) for item in reports]
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
    }
    return report_to_dict(create_learning_report(db, profile, course, summary), course.title)


@router.get("/{report_id}/download")
def download(report_id: int, db: Session = Depends(get_db)):
    report = db.query(LearningReport).filter(LearningReport.id == report_id).first()
    if not report or not report_exists(report):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    return FileResponse(report.report_path, filename=f"learning-report-{report_id}.docx")
