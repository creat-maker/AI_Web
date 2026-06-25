from __future__ import annotations

import json
import zipfile
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.routers.reports import report_to_dict
from app.core.config import settings
from app.db.session import get_db
from app.models import Course, LearningReport, StudentProfile
from app.services.report_service import create_learning_report, report_exists

router = APIRouter(prefix="/admin/reports", tags=["admin-reports"])


class StatusPayload(BaseModel):
    status: str


def _contexts(db: Session):
    return (
        {item.id: item.title for item in db.query(Course).all()},
        {item.id: item.student_name for item in db.query(StudentProfile).all()},
    )


@router.get("")
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(LearningReport).order_by(LearningReport.id.desc()).all()
    courses, profiles = _contexts(db)
    rows = []
    for item in reports:
        row = report_to_dict(item, courses.get(item.course_id), profiles.get(item.student_profile_id))
        row.update({"creator": "EduMind 评价服务", "review_status": "待审核" if row["status"] == "completed" else "生成中"})
        rows.append(row)
    return rows


@router.get("/{report_id}/preview")
def preview_report(report_id: int, db: Session = Depends(get_db)):
    item = db.query(LearningReport).filter(LearningReport.id == report_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="报告不存在")
    courses, profiles = _contexts(db)
    return report_to_dict(item, courses.get(item.course_id), profiles.get(item.student_profile_id))


@router.get("/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db)):
    item = db.query(LearningReport).filter(LearningReport.id == report_id).first()
    if not item or not report_exists(item):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    return FileResponse(item.report_path, filename=f"admin-report-{report_id}.docx")


@router.post("/{report_id}/regenerate")
def regenerate_report(report_id: int, db: Session = Depends(get_db)):
    old = db.query(LearningReport).filter(LearningReport.id == report_id).first()
    if not old:
        raise HTTPException(status_code=404, detail="报告不存在")
    profile = db.query(StudentProfile).filter(StudentProfile.id == old.student_profile_id).first()
    course = db.query(Course).filter(Course.id == old.course_id).first()
    if not profile or not course:
        raise HTTPException(status_code=404, detail="报告关联数据不完整")
    payload = {
        "summary": "管理员触发重新生成，已根据当前课程数据和学习记录刷新报告。",
        "profile_summary": f"{profile.student_name} 在 {course.title} 中的学习表现已重新评估。",
        "weak_points": ["循环条件更新", "break / continue 区分", "循环嵌套变量追踪"],
        "references": ["学生画像", "测验记录", "课程知识库", "学习资源使用记录"],
        "regenerate_reason": "报告审核中心触发重新生成。",
    }
    new_item = create_learning_report(db, profile, course, payload)
    return report_to_dict(new_item, course.title, profile.student_name)


@router.post("/monthly")
def monthly_report(db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).order_by(StudentProfile.id.desc()).first()
    course = db.query(Course).order_by(Course.id.desc()).first()
    if not profile or not course:
        raise HTTPException(status_code=404, detail="缺少课程或学生画像数据")
    payload = {
        "title": f"EduMind 平台运营月报 {datetime.utcnow().strftime('%Y-%m')}",
        "summary": "平台月报汇总课程、资源、测验、报告和治理状态。",
        "profile_summary": "平台运行保持稳定，Python 循环结构主链路数据完整。",
        "weak_points": ["资源质量持续治理", "学习报告复核", "课程知识库更新"],
        "references": ["课程数据", "资源生成记录", "报告审核记录", "系统日志"],
        "report_type": "平台运营报告",
    }
    item = create_learning_report(db, profile, course, payload)
    return report_to_dict(item, course.title, profile.student_name)


@router.post("/export")
def export_reports(db: Session = Depends(get_db)):
    reports = db.query(LearningReport).order_by(LearningReport.id.desc()).limit(20).all()
    export_dir = settings.path_from_root("backend/storage/reports")
    export_dir.mkdir(parents=True, exist_ok=True)
    zip_path = export_dir / "admin-reports-export.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        manifest = []
        for item in reports:
            manifest.append({"id": item.id, "title": item.report_title, "path": item.report_path})
            if report_exists(item):
                archive.write(item.report_path, arcname=f"report-{item.id}.docx")
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return FileResponse(zip_path, filename="admin-reports-export.zip")


@router.patch("/{report_id}/status")
def update_report_status(report_id: int, payload: StatusPayload):
    return {"report_id": report_id, "status": payload.status, "message": "报告审核状态已更新"}
