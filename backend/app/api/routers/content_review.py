from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.business_event_service import record_event
from app.services.content_review_service import check_content, list_review_records


router = APIRouter(prefix="/content-review", tags=["content-review"])


class ContentReviewPayload(BaseModel):
    content: str
    courseId: str | int | None = "python-programming"
    citations: list[dict[str, Any]] = Field(default_factory=list)


@router.post("/check")
def check(payload: ContentReviewPayload, db: Session = Depends(get_db)):
    result = check_content(payload.model_dump())
    record_event(
        db,
        event_type="content_review_checked",
        title="AI 内容防幻觉审核已完成",
        description=f"内容审核结果：{result['reviewStatus']}，风险等级：{result['riskLevel']}。",
        actor_role="admin",
        actor_name="demo_admin",
        target_type="content_review",
        target_id=result["id"],
        related_course="Python 程序设计",
        metadata=result,
    )
    return result


@router.get("/records")
def records(limit: int = 20):
    return {"items": list_review_records(limit), "total": len(list_review_records(50))}
