from __future__ import annotations

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


def report_to_dict(item: LearningReport) -> dict:
    return {
        "id": item.id,
        "course_id": item.course_id,
        "student_profile_id": item.student_profile_id,
        "report_title": item.report_title,
        "report_path": item.report_path,
        "report_json": loads(item.report_json, {}),
        "created_at": item.created_at,
    }


@router.get("")
def list_items(course_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(LearningReport)
    if course_id:
        query = query.filter(LearningReport.course_id == course_id)
    return [report_to_dict(item) for item in query.order_by(LearningReport.id.desc()).all()]


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
    return report_to_dict(create_learning_report(db, profile, course, summary))


@router.get("/{report_id}/download")
def download(report_id: int, db: Session = Depends(get_db)):
    report = db.query(LearningReport).filter(LearningReport.id == report_id).first()
    if not report or not report_exists(report):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    return FileResponse(report.report_path, filename=f"learning-report-{report_id}.docx")
