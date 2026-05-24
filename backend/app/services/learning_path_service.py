from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Course, LearningPath, StudentProfile
from app.services.json_utils import dumps, loads
from app.services.llm_service import llm_service


def create_learning_path(db: Session, profile: StudentProfile, course: Course) -> LearningPath:
    path_json = llm_service.generate_json(
        "learning_path",
        {"profile": loads(profile.profile_json, {}), "course_title": course.title},
    )
    item = LearningPath(
        student_profile_id=profile.id,
        course_id=course.id,
        path_json=dumps(path_json),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_learning_paths(db: Session, course_id: int | None = None) -> list[LearningPath]:
    query = db.query(LearningPath)
    if course_id:
        query = query.filter(LearningPath.course_id == course_id)
    return query.order_by(LearningPath.id.desc()).all()
