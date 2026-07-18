from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models import AITaskRun, ContentVersion, ReviewItem
from app.services.governance_service import (
    DEFAULT_ITEM_KEY,
    approve_review_item,
    create_ai_task,
    create_review_item,
    ensure_governance_seed,
    reject_review_item,
    review_item_to_dict,
    task_to_dict,
    version_to_dict,
    write_audit_log,
)

router = APIRouter(tags=["governance"])


class ReviewActionPayload(BaseModel):
    comment: str = ""


class TaskCreatePayload(BaseModel):
    task_type: str = "resource_pack"
    title: str = "Python 循环结构个性化补弱资源包"
    fail: bool = False
    input_summary: dict[str, Any] | str | None = None


@router.get("/tasks")
def list_tasks(
    status: str | None = None,
    task_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin),
):
    ensure_governance_seed(db)
    query = db.query(AITaskRun)
    if status and status != "all":
        query = query.filter(AITaskRun.status == status)
    if task_type and task_type != "all":
        query = query.filter(AITaskRun.task_type == task_type)
    return [task_to_dict(item) for item in query.order_by(AITaskRun.created_at.desc()).limit(100).all()]


@router.post("/tasks")
def create_task(
    payload: TaskCreatePayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin),
):
    ensure_governance_seed(db)
    status = "failed" if payload.fail else "pending_review"
    task = create_ai_task(
        db,
        task_type=payload.task_type,
        title=payload.title,
        actor_id=str(current_user.get("user_id") or current_user.get("username")),
        actor_role=str(current_user.get("role") or "teacher"),
        input_summary=payload.input_summary
        or {"course": "Python 程序设计", "topic": "循环结构", "student": "李明", "profile": "基础薄弱 + 代码实操偏好型"},
        output_summary="生成内容已进入人工复核。" if not payload.fail else "生成失败，已保留上一版内容。",
        status=status,
        confidence=0.87 if not payload.fail else 0.0,
        error_message="课程知识库引用片段不足，已保留上一版内容。" if payload.fail else None,
        trace={"rollback": payload.fail, "nodes": ["input", "generation", "review_gate"]},
    )
    if not payload.fail:
        review = create_review_item(
            db,
            item_type=payload.task_type,
            item_title=payload.title,
            source_task_id=task.id,
            content={
                "item_key": DEFAULT_ITEM_KEY.get(payload.task_type, payload.task_type),
                "course": "Python 程序设计",
                "student": "李*",
                "confidence": 0.87,
                "risk_tip": "引用完整，建议教师复核示例代码输出。",
                "generation_basis": ["循环结构章节", "学习画像摘要", "最近测验错因"],
                "resources": ["while 循环讲义", "循环嵌套练习", "代码案例"],
            },
        )
        return {"task": task_to_dict(task), "review_item": review_item_to_dict(review)}
    write_audit_log(
        db,
        actor_id=str(current_user.get("user_id") or ""),
        actor_name=str(current_user.get("name") or ""),
        actor_role=str(current_user.get("role") or "teacher"),
        action="task_failed_rollback",
        target_type=payload.task_type,
        target_id=task.id,
        status="failed",
        detail=task.error_message,
    )
    return {"task": task_to_dict(task), "rollback_notice": "生成失败，可重试，当前仍使用上一版内容。"}


@router.get("/review-items")
def list_review_items(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin),
):
    ensure_governance_seed(db)
    query = db.query(ReviewItem)
    if status and status != "all":
        query = query.filter(ReviewItem.status == status)
    return [review_item_to_dict(item) for item in query.order_by(ReviewItem.created_at.desc()).limit(100).all()]


@router.post("/review-items/{item_id}/approve")
def approve_item(
    item_id: int,
    payload: ReviewActionPayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin),
):
    ensure_governance_seed(db)
    item = db.query(ReviewItem).filter(ReviewItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="审核项不存在")
    return review_item_to_dict(approve_review_item(db, item, current_user, payload.comment))


@router.post("/review-items/{item_id}/reject")
def reject_item(
    item_id: int,
    payload: ReviewActionPayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin),
):
    ensure_governance_seed(db)
    item = db.query(ReviewItem).filter(ReviewItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="审核项不存在")
    return review_item_to_dict(reject_review_item(db, item, current_user, payload.comment))


@router.get("/content-versions/active")
def active_content_version(
    item_type: str = "resource_pack",
    item_key: str | None = None,
    db: Session = Depends(get_db),
):
    ensure_governance_seed(db)
    key = item_key or DEFAULT_ITEM_KEY.get(item_type, item_type)
    active = (
        db.query(ContentVersion)
        .filter(
            ContentVersion.item_type == item_type,
            ContentVersion.item_key == key,
            ContentVersion.is_active.is_(True),
        )
        .order_by(ContentVersion.version_no.desc())
        .first()
    )
    latest_failed = (
        db.query(AITaskRun)
        .filter(AITaskRun.task_type == item_type, AITaskRun.status == "failed")
        .order_by(AITaskRun.created_at.desc())
        .first()
    )
    return {
        "active": version_to_dict(active),
        "latest_failed_task": task_to_dict(latest_failed) if latest_failed else None,
        "rollback_notice": "生成失败，可重试，当前仍使用上一版内容。" if latest_failed else "",
    }
