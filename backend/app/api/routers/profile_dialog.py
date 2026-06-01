from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.business_event_service import record_event
from app.services.personalization_service import run_profile_dialog


router = APIRouter(prefix="/profile-dialog", tags=["profile-dialog"])


class ProfileDialogPayload(BaseModel):
    studentId: str | int | None = None
    studentName: str | None = "张三"
    courseId: str | int | None = None
    courseName: str | None = "Python 程序设计"
    answer: str | None = None
    answers: list[Any] = Field(default_factory=list)
    weakPoints: list[str] = Field(default_factory=list)


@router.post("/run")
def run_dialog(payload: ProfileDialogPayload, db: Session = Depends(get_db)):
    result = run_profile_dialog(payload.model_dump())
    record_event(
        db,
        event_type="profile_dialog_completed",
        title="对话式学习画像已生成",
        description=f"{result['studentName']} 的对话式学习画像已生成，包含目标、基础、薄弱点、偏好、时间、风险和策略。",
        actor_role="student",
        actor_name=result["studentName"],
        target_type="profile_dialog",
        target_id=result["studentId"],
        related_student=result["studentName"],
        related_course=result["courseName"],
        metadata={
            "dimension_count": len(result["dimensions"]),
            "weak_points": result["weakKnowledgePoints"],
            "mode": result["mode"],
        },
    )
    return result
