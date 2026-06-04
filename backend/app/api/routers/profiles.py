from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, StudentProfile
from app.services.business_event_service import record_event
from app.services.profile_service import create_profile, list_profiles, profile_to_dict


router = APIRouter(prefix="/profiles", tags=["profiles"])


class ProfilePayload(BaseModel):
    course_id: int
    student_name: str
    current_level: str | None = None
    learning_goal: str | None = None
    weak_points: list[str] = []
    learning_preference: str | None = None


@router.get("")
def list_items(course_id: int | None = None, db: Session = Depends(get_db)):
    return [profile_to_dict(item) for item in list_profiles(db, course_id)]


@router.post("")
def create_item(payload: ProfilePayload, db: Session = Depends(get_db)):
    profile = create_profile(db, payload.model_dump())
    course = db.query(Course).filter(Course.id == profile.course_id).first()
    record_event(
        db,
        event_type="profile_generated",
        title="学生画像已生成",
        description=f"{profile.student_name} 的学习画像已生成，包含目标、水平、偏好、薄弱点和风险等级 demo/fallback 字段。",
        actor_role="student",
        actor_name=profile.student_name,
        target_type="student_profile",
        target_id=profile.id,
        related_student=profile.student_name,
        related_course=course.title if course else "",
        metadata={
            "learning_goal": profile.learning_goal,
            "current_level": profile.current_level,
            "learning_preference": profile.learning_preference,
            "resource_preference": "知识讲义、分层练习题、代码示例",
            "weak_points": payload.weak_points,
            "risk_level": "需关注" if payload.weak_points else "稳定",
            "course_id": profile.course_id,
        },
    )
    return profile_to_dict(profile)


@router.post("/generate")
def generate_profile(payload: ProfilePayload, db: Session = Depends(get_db)):
    return create_item(payload, db)


@router.get("/{profile_id}")
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="学生画像不存在")
    return profile_to_dict(profile)
