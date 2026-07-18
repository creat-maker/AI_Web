from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import require_staff
from app.db.session import get_db
from app.services.business_event_service import record_event
from app.services.content_review_service import check_content, list_review_records
from app.services.governance_service import current_user_label
from app.services.teacher_scope_service import can_manage_course, resolve_course_reference


router = APIRouter(prefix="/content-review", tags=["content-review"])


class ContentReviewPayload(BaseModel):
    content: str
    courseId: str | int | None = "python-programming"
    citations: list[dict[str, Any]] = Field(default_factory=list)


@router.post("/check")
def check(
    payload: ContentReviewPayload,
    current_user: dict[str, Any] = Depends(require_staff),
    db: Session = Depends(get_db),
):
    course = resolve_course_reference(db, payload.courseId)
    if not course or not can_manage_course(db, current_user, course):
        raise HTTPException(status_code=404, detail="课程不存在或不可访问")
    result = check_content(payload.model_dump())
    actor_id, actor_name, actor_role = current_user_label(current_user)
    record_event(
        db,
        event_type="content_review_checked",
        title="AI 内容防幻觉审核已完成",
        description=f"内容审核结果：{result['reviewStatus']}，风险等级：{result['riskLevel']}。",
        actor_id=actor_id,
        actor_role=actor_role,
        actor_name=actor_name,
        target_type="content_review",
        target_id=result["id"],
        related_course=course.title,
        metadata=result,
    )
    return result


@router.get("/records")
def records(
    limit: int = 20,
    current_user: dict[str, Any] = Depends(require_staff),
):
    return {"items": list_review_records(limit), "total": len(list_review_records(50))}
