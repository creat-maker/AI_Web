from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import StudentProfile
from app.services.json_utils import dumps, loads
from app.services.llm_service import llm_service


def create_profile(db: Session, data: dict) -> StudentProfile:
    profile_json = llm_service.generate_json("profile", data)
    profile = StudentProfile(
        student_name=data["student_name"],
        course_id=data["course_id"],
        current_level=data.get("current_level"),
        learning_goal=data.get("learning_goal"),
        weak_points=dumps(data.get("weak_points", [])),
        learning_preference=data.get("learning_preference"),
        profile_json=dumps(profile_json),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def list_profiles(db: Session, course_id: int | None = None) -> list[StudentProfile]:
    query = db.query(StudentProfile)
    if course_id:
        query = query.filter(StudentProfile.course_id == course_id)
    return query.order_by(StudentProfile.id.desc()).all()


def profile_to_dict(profile: StudentProfile) -> dict:
    return {
        "id": profile.id,
        "student_name": profile.student_name,
        "course_id": profile.course_id,
        "current_level": profile.current_level,
        "learning_goal": profile.learning_goal,
        "weak_points": loads(profile.weak_points, []),
        "learning_preference": profile.learning_preference,
        "profile_json": loads(profile.profile_json, {}),
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }
