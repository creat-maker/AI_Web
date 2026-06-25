from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_demo_user_id
from app.db.session import get_db
from app.models import Course, GeneratedResource, LearningPath, StudentProfile
from app.services.business_event_service import record_event
from app.services.demo_profile_chain import build_resource_pack, get_demo_student
from app.services.json_utils import loads
from app.services.llm_service import llm_service
from app.services.personalization_service import generate_resource_pack
from app.services.profile_service import latest_profile_by_user_id, profile_to_dict
from app.services.courseware_service import CoursewareRequest, build_courseware_outline
from app.services.multimodal_resource_service import RESOURCE_TYPE_CATALOG, ffmpeg_capability, xfyun_tts_capability


router = APIRouter(prefix="/resources", tags=["resources"])


class ResourceGeneratePayload(BaseModel):
    course_id: int
    student_profile_id: int | None = None


class ResourcePackPayload(BaseModel):
    studentId: str | int | None = None
    courseId: str | int | None = None
    courseName: str | None = None
    studentLevel: str | None = None
    learningGoal: str | None = None
    knowledgePoints: list[str] = []
    weakPoints: list[str] = []


class CoursewareOutlinePayload(BaseModel):
    course: str = "Python 程序设计"
    chapter: str = "循环结构"
    student: str = "李明"
    weakPoints: str = "while 循环和循环嵌套需要加强"


@router.get("")
def list_items(course_id: int | None = None, user_id: str | None = None, db: Session = Depends(get_db)):
    if user_id:
        profile = latest_profile_by_user_id(db, user_id, course_id)
        pack = build_resource_pack({"user_id": user_id, "profile": profile_to_dict(profile) if profile else None})
        return [
            {
                "id": f"{pack['studentId']}-{index}",
                "course_id": pack["courseId"],
                "student_profile_id": pack["studentId"],
                "resource_type": item["resource_type"],
                "title": item["title"],
                "content": item["content"],
                "difficulty": item["difficulty"],
                "source_agent": "ResourceAgent",
                "recommend_reason": item["recommendation_reason"],
                "recommendation_reason": item["recommendation_reason"],
                "relatedKnowledgePoints": item.get("relatedKnowledgePoints", []),
                "references": item.get("references", []),
                "reviewStatus": item.get("reviewStatus", "通过"),
                "libraryStatus": item.get("libraryStatus", "已入库"),
                "pushStatus": item.get("pushStatus", "可推送"),
                "estimatedMinutes": item.get("estimatedMinutes", 20),
                "created_at": pack["profile"]["updated_at"],
            }
            for index, item in enumerate(pack["resources"], start=1)
        ]
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


@router.get("/recommendations")
def recommendations(
    user_id: str | None = None,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_demo_user_id),
):
    active_user_id = user_id or current_user_id
    profile = latest_profile_by_user_id(db, active_user_id)
    return build_resource_pack({"user_id": active_user_id, "profile": profile_to_dict(profile) if profile else None})


@router.post("/generate-pack")
def generate_pack(payload: ResourcePackPayload, db: Session = Depends(get_db), current_user_id: str = Depends(get_demo_user_id)):
    data = payload.model_dump()
    active_user_id = payload.studentId or current_user_id
    profile = latest_profile_by_user_id(db, active_user_id)
    data["studentId"] = active_user_id
    if profile:
        data["profile"] = profile_to_dict(profile)
    pack = build_resource_pack(data) if active_user_id else generate_resource_pack(data)
    for item in pack.get("resources", []):
        item.setdefault("reviewStatus", "通过")
        item.setdefault("displayReviewStatus", item["reviewStatus"])
        item.setdefault("libraryStatus", "待加入")
        item.setdefault("pushStatus", "待推送")
        item.setdefault("suitableLearner", "李明：循环结构需巩固，偏好代码实操")
        item.setdefault("estimatedMinutes", 20)
        item.setdefault("references", ["Python 程序设计课程知识库 / 循环结构章节"])
    pack.setdefault("resourceTypes", [item["key"] for item in RESOURCE_TYPE_CATALOG])
    pack.setdefault("resource_types", pack["resourceTypes"])
    pack.setdefault("resourceTypeCount", len(pack["resourceTypes"]))
    pack.setdefault("resource_type_count", pack["resourceTypeCount"])
    pack.setdefault("runtimeCapabilities", {
        "ffmpeg": ffmpeg_capability(),
        "xfyun_tts": xfyun_tts_capability(),
    })
    pack.setdefault("runtime_capabilities", pack["runtimeCapabilities"])
    course_id = None
    try:
        course_id = int(payload.courseId) if payload.courseId else None
    except (TypeError, ValueError):
        course_id = None
    if not course_id and payload.courseName:
        course = db.query(Course).filter(Course.title == payload.courseName).first()
        course_id = course.id if course else None
    if not course_id:
        course = db.query(Course).order_by(Course.id.asc()).first()
        course_id = course.id if course else None

    if course_id:
        for item in pack.get("resources", []):
            resource_type = item.get("resource_type") or item.get("resourceType") or "resource"
            title = item.get("title") or f"{pack.get('courseName', '课程')}学习资源"
            existing = (
                db.query(GeneratedResource)
                .filter(GeneratedResource.course_id == course_id, GeneratedResource.title == title)
                .first()
            )
            if existing:
                continue
            db.add(
                GeneratedResource(
                    course_id=course_id,
                    student_profile_id=profile.id if profile else None,
                    resource_type=resource_type,
                    title=title,
                    content=item.get("content") or item.get("description") or title,
                    difficulty=item.get("difficulty") or item.get("level") or "基础",
                    source_agent="ResourceAgent",
                    recommend_reason=item.get("recommend_reason") or item.get("recommendation_reason") or item.get("reason"),
                )
            )
        db.commit()

    student = get_demo_student(active_user_id)
    record_event(
        db,
        event_type="resource_pack_generated",
        title=f"{pack.get('resourceTypeCount', len(pack.get('resources', [])))} 类个性化资源包已生成",
        description=f"{pack['courseName']} 已生成讲义、思维导图、练习题、HTML 动画、视频脚本、语音讲解任务、代码案例和项目任务。",
        actor_role="student",
        actor_name=student["student_name"],
        target_type="resource_pack",
        target_id=f"{pack['studentId']}-{pack['courseId']}",
        related_student=student["student_name"],
        related_course=pack["courseName"],
        metadata={
            "resource_count": pack["resourceCount"],
            "resource_types": [item.get("resource_type") or item.get("resourceType") for item in pack["resources"]],
            "runtime_capabilities": pack["runtimeCapabilities"],
            "weak_points": pack["weakPoints"],
            "mode": pack["mode"],
            "profile_type": pack.get("profileType"),
            "audit_flow": pack.get("auditFlow"),
        },
    )
    return pack


@router.post("/courseware-outline")
def generate_courseware_outline(payload: CoursewareOutlinePayload) -> dict:
    request = CoursewareRequest(
        course=payload.course,
        chapter=payload.chapter,
        student=payload.student,
        weak_points=payload.weakPoints,
    )
    return build_courseware_outline(request)
