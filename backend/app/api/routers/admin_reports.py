from __future__ import annotations

import json
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.api.routers.reports import report_to_dict
from app.core.config import settings
from app.db.session import get_db
from app.models import Course, LearningReport, StudentProfile
from app.services.governance_service import current_user_label, write_audit_log
from app.services.json_utils import dumps, loads
from app.services.report_service import create_learning_report, report_exists

router = APIRouter(prefix="/admin/reports", tags=["admin-reports"])


class StatusPayload(BaseModel):
    status: str


REVIEW_STATUSES = {"待审核", "已通过", "已驳回"}


def _contexts(db: Session):
    return (
        {item.id: item.title for item in db.query(Course).all()},
        {item.id: item.student_name for item in db.query(StudentProfile).all()},
    )


def _admin_report_to_dict(
    item: LearningReport,
    course_title: str | None = None,
    student_name: str | None = None,
) -> dict[str, Any]:
    row = report_to_dict(item, course_title, student_name)
    report_json = loads(item.report_json, {})
    row.pop("report_path", None)
    row.pop("report_json", None)
    row["creator"] = "EduMind 评价服务"
    row["review_status"] = report_json.get("review_status") or ("待审核" if row["status"] == "completed" else "生成中")
    row["download_url"] = f"/api/v1/admin/reports/{item.id}/download" if row.get("download_enabled") else ""
    row["report_url"] = row["download_url"]
    return row


def _audit(
    db: Session,
    current_user: dict[str, Any],
    *,
    action: str,
    target_id: str | int,
    detail: str,
    commit: bool = True,
) -> None:
    actor_id, actor_name, actor_role = current_user_label(current_user)
    write_audit_log(
        db,
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action=action,
        target_type="admin_report",
        target_id=target_id,
        detail=detail,
        commit=commit,
    )


def _safe_report_path(item: LearningReport) -> Path:
    path = Path(item.report_path).resolve()
    report_root = settings.path_from_root(settings.report_dir).resolve()
    if not path.is_relative_to(report_root) or not path.is_file():
        raise HTTPException(status_code=404, detail="报告文件不存在")
    return path


@router.get("")
def list_reports(
    current_user: dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db),
):
    reports = db.query(LearningReport).order_by(LearningReport.id.desc()).all()
    courses, profiles = _contexts(db)
    rows = []
    for item in reports:
        rows.append(_admin_report_to_dict(item, courses.get(item.course_id), profiles.get(item.student_profile_id)))
    return rows


@router.get("/{report_id}/preview")
def preview_report(
    report_id: int,
    current_user: dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db),
):
    item = db.query(LearningReport).filter(LearningReport.id == report_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="报告不存在")
    courses, profiles = _contexts(db)
    return _admin_report_to_dict(item, courses.get(item.course_id), profiles.get(item.student_profile_id))


@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    current_user: dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db),
):
    item = db.query(LearningReport).filter(LearningReport.id == report_id).first()
    if not item or not report_exists(item):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    path = _safe_report_path(item)
    return FileResponse(path, filename=f"admin-report-{report_id}{path.suffix or '.docx'}")


@router.post("/{report_id}/regenerate")
def regenerate_report(
    report_id: int,
    current_user: dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db),
):
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
    _audit(db, current_user, action="admin_report_regenerated", target_id=report_id, detail=f"重新生成报告，新报告ID={new_item.id}")
    return _admin_report_to_dict(new_item, course.title, profile.student_name)


@router.post("/monthly")
def monthly_report(
    current_user: dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db),
):
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
    _audit(db, current_user, action="admin_monthly_report_created", target_id=item.id, detail="已生成平台运营月报")
    return _admin_report_to_dict(item, course.title, profile.student_name)


@router.post("/export")
def export_reports(
    current_user: dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db),
):
    reports = db.query(LearningReport).order_by(LearningReport.id.desc()).limit(20).all()
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        manifest = []
        for item in reports:
            manifest.append({"id": item.id, "title": item.report_title})
            try:
                path = _safe_report_path(item)
            except HTTPException:
                continue
            archive.write(path, arcname=f"report-{item.id}{path.suffix or '.docx'}")
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    buffer.seek(0)
    _audit(db, current_user, action="admin_reports_exported", target_id="batch", detail=f"批量导出报告数量={len(reports)}")
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="admin-reports-export.zip"'},
    )


@router.patch("/{report_id}/status")
def update_report_status(
    report_id: int,
    payload: StatusPayload,
    current_user: dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if payload.status not in REVIEW_STATUSES:
        raise HTTPException(status_code=422, detail="报告审核状态不在允许范围内")
    item = db.query(LearningReport).filter(LearningReport.id == report_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="报告不存在")
    report_json = loads(item.report_json, {})
    previous = report_json.get("review_status") or "待审核"
    report_json["review_status"] = payload.status
    item.report_json = dumps(report_json)
    _audit(
        db,
        current_user,
        action="admin_report_status_updated",
        target_id=report_id,
        detail=f"报告审核状态由 {previous} 更新为 {payload.status}",
        commit=False,
    )
    db.commit()
    return {"report_id": report_id, "status": payload.status, "message": "报告审核状态已更新"}
