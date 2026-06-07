from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, GeneratedResource, LearningPath, StudentProfile
from app.services.business_event_service import record_event
from app.services.json_utils import loads
from app.services.llm_service import llm_service
from app.services.personalization_service import generate_resource_pack


router = APIRouter(prefix="/resources", tags=["resources"])


class ResourceGeneratePayload(BaseModel):
    course_id: int
    student_profile_id: int | None = None


class ResourcePackPayload(BaseModel):
    studentId: str | int | None = None
    courseId: str | int | None = None
    courseName: str | None = None
    weakPoints: list[str] = []


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
            recommend_reason=item.get("recommend_reason"),
        )
        db.add(resource)
        resources.append(resource)
    db.commit()
    for resource in resources:
        db.refresh(resource)
    return resources


@router.post("/generate-pack")
def generate_pack(payload: ResourcePackPayload, db: Session = Depends(get_db)):
    pack = generate_resource_pack(payload.model_dump())
    record_event(
        db,
        event_type="resource_pack_generated",
        title="5 类个性化资源包已生成",
        description=f"{pack['courseName']} 已生成个性化讲义、练习题、实验任务、思维导图和视频脚本/任务书。",
        actor_role="student",
        actor_name="张三",
        target_type="resource_pack",
        target_id=f"{pack['studentId']}-{pack['courseId']}",
        related_student="张三",
        related_course=pack["courseName"],
        metadata={
            "resource_count": pack["resourceCount"],
            "resource_types": [item["resourceType"] for item in pack["resources"]],
            "weak_points": pack["weakPoints"],
            "mode": pack["mode"],
        },
    )
    return pack
