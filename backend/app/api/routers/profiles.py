from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import StudentProfile
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
    return profile_to_dict(create_profile(db, payload.model_dump()))


@router.post("/generate")
def generate_profile(payload: ProfilePayload, db: Session = Depends(get_db)):
    return profile_to_dict(create_profile(db, payload.model_dump()))


@router.get("/{profile_id}")
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="学生画像不存在")
    return profile_to_dict(profile)
