from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, GeneratedResource, LearningPath, StudentProfile
from app.services.json_utils import loads
from app.services.llm_service import llm_service


router = APIRouter(prefix="/resources", tags=["resources"])


class ResourceGeneratePayload(BaseModel):
    course_id: int
    student_profile_id: int | None = None


@router.get("")
def list_items(course_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(GeneratedResource)
    if course_id:
        query = query.filter(GeneratedResource.course_id == course_id)
    return query.order_by(GeneratedResource.id.desc()).all()


@router.post("/generate")
def generate_resources(payload: ResourceGeneratePayload, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    profile = None
    profile_json = {}
    if payload.student_profile_id:
        profile = db.query(StudentProfile).filter(StudentProfile.id == payload.student_profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="学生画像不存在")
        profile_json = loads(profile.profile_json, {})

    path = None
    if profile:
        path = (
            db.query(LearningPath)
            .filter(LearningPath.student_profile_id == profile.id)
            .order_by(LearningPath.id.desc())
            .first()
        )
    learning_path = loads(path.path_json, {}) if path else {"course_title": course.title, "goal": course.description or course.title}
    generated = llm_service.generate_json("resources", {"profile": profile_json, "learning_path": learning_path})

    resources = []
    for item in generated:
        resource = GeneratedResource(
            course_id=course.id,
            student_profile_id=profile.id if profile else None,
            resource_type=item.get("resource_type", "resource"),
            title=item.get("title", "学习资源"),
            content=item.get("content", ""),
            difficulty=item.get("difficulty"),
            source_agent="ResourceAgent",
        )
        db.add(resource)
        resources.append(resource)
    db.commit()
    for resource in resources:
        db.refresh(resource)
    return resources
