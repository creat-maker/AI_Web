from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_admin, require_staff
from app.api.routers.auth import get_authenticated_user
from app.db.session import get_db
from app.models import Course, GeneratedResource, LearningPath, Quiz, QuizSubmission, StudentProfile, SystemLog
from app.services.business_event_service import EVENT_LOG_TYPE, event_to_dict, list_events, record_event
from app.services.json_utils import dumps, loads
from app.services.governance_service import current_user_label
from app.services.teacher_scope_service import get_course_for_write, get_profile_for_write


router = APIRouter(prefix="/events", tags=["events"])


RESOURCE_TYPES = ["知识讲义", "PPT 提纲", "分层练习题", "思维导图", "拓展阅读", "实验案例", "代码示例", "微课视频脚本"]


class EventPayload(BaseModel):
    event_type: str
    title: str
    description: str
    actor_id: str | None = None
    actor_role: str = "demo"
    actor_name: str = "EduMind demo user"
    target_type: str = "system"
    target_id: str | int | None = None
    related_student: str | None = None
    related_course: str | None = None
    status: str = "success"
    metadata: dict[str, Any] = {}


class ResourcePackagePayload(BaseModel):
    course_id: int | None = None
    student_profile_id: int | None = None
    actor_role: str = "student"
    actor_name: str = "demo_student"


class AddToPathPayload(BaseModel):
    package_id: str
    course_id: int | None = None
    student_profile_id: int | None = None
    actor_role: str = "student"
    actor_name: str = "demo_student"


class TaskAssignPayload(BaseModel):
    student_profile_id: int | None = None
    course_id: int | None = None
    weak_point: str = "while 循环终止条件"
    task_type: str = "完成练习"
    due_date: str | None = None
    actor_role: str = "teacher"
    actor_name: str = "demo_teacher"


class DemoQuizPayload(BaseModel):
    student_profile_id: int | None = None
    course_id: int | None = None
    actor_role: str = "student"
    actor_name: str = "demo_student"


@router.get("")
def list_business_events(
    event_type: str | None = None,
    actor_role: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return list_events(db, event_type=event_type, actor_role=actor_role, limit=limit)


@router.post("")
def create_event(
    payload: EventPayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin),
):
    actor_id, actor_name, actor_role = current_user_label(current_user)
    data = payload.model_dump(exclude={"actor_id", "actor_name", "actor_role"})
    item = record_event(db, **data, actor_id=actor_id, actor_name=actor_name, actor_role=actor_role)
    return event_to_dict(item)


def _target_course(db: Session, current_user: dict[str, Any], course_id: int | None) -> Course:
    if course_id is None:
        raise HTTPException(status_code=422, detail="必须指定课程")
    return get_course_for_write(db, current_user, course_id)


def _target_profile(
    db: Session,
    current_user: dict[str, Any],
    profile_id: int | None,
    course: Course,
) -> StudentProfile:
    if profile_id is None:
        raise HTTPException(status_code=422, detail="必须指定学生画像")
    return get_profile_for_write(db, current_user, profile_id, course=course)


@router.post("/resource-package")
def create_resource_package(
    payload: ResourcePackagePayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_staff),
):
    course = _target_course(db, current_user, payload.course_id)
    profile = _target_profile(db, current_user, payload.student_profile_id, course)
    actor_id, actor_name, actor_role = current_user_label(current_user)
    weak_points = loads(profile.weak_points, [])
    package_id = f"pkg-{course.id}-{profile.id}-{date.today().isoformat()}"
    if db.query(SystemLog).filter(SystemLog.type == EVENT_LOG_TYPE, SystemLog.related_id == package_id).first():
        raise HTTPException(status_code=409, detail="该资源包请求已处理")
    resources = []
    for index, resource_type in enumerate(RESOURCE_TYPES, start=1):
        resource = GeneratedResource(
            course_id=course.id,
            student_profile_id=profile.id,
            resource_type=resource_type,
            title=f"{course.title} · {resource_type}",
            content=f"{resource_type}：围绕 {', '.join(str(item) for item in weak_points[:3])} 生成，用于个性化多模态资源包。",
            difficulty="分层",
            source_agent="ResourcePackageAgent",
        )
        db.add(resource)
        resources.append(resource)
    db.flush()
    record_event(
        db,
        event_type="resource_generated",
        title="生成个性化资源包",
        description=f"已为 {profile.student_name} 生成 9 类资源包。",
        actor_id=actor_id,
        actor_role=actor_role,
        actor_name=actor_name,
        target_type="resource_package",
        target_id=package_id,
        related_student=profile.student_name,
        related_course=course.title,
        metadata={
            "package_id": package_id,
            "resource_count": len(resources),
            "resource_types": RESOURCE_TYPES,
            "course_id": course.id,
            "student_profile_id": profile.id,
        },
        commit=False,
    )
    db.commit()
    for item in resources:
        db.refresh(item)
    return {
        "package_id": package_id,
        "course_id": course.id,
        "student_profile_id": profile.id,
        "resources": resources,
        "demo_fallback_note": "资源包由 EduMind fallback API 生成，用于演示画像到资源生成闭环。",
    }


@router.post("/add-resource-to-path")
def add_resource_to_path(
    payload: AddToPathPayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_authenticated_user),
):
    if payload.course_id is None:
        raise HTTPException(status_code=422, detail="必须指定课程")
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在或不可访问")
    profile = _target_profile(db, current_user, payload.student_profile_id, course)
    if current_user.get("role") in {"teacher", "admin"}:
        course = _target_course(db, current_user, payload.course_id)
    actor_id, actor_name, actor_role = current_user_label(current_user)
    package_event = (
        db.query(SystemLog)
        .filter(SystemLog.type == EVENT_LOG_TYPE, SystemLog.related_id == payload.package_id)
        .order_by(SystemLog.id.desc())
        .first()
    )
    if not package_event:
        raise HTTPException(status_code=404, detail="资源包不存在或不可访问")
    package_data = event_to_dict(package_event).get("metadata", {})
    if int(package_data.get("course_id") or -1) != int(course.id) or int(package_data.get("student_profile_id") or -1) != int(profile.id):
        raise HTTPException(status_code=404, detail="资源包不存在或不可访问")
    item = (
        db.query(LearningPath)
        .filter(LearningPath.student_profile_id == profile.id)
        .order_by(LearningPath.id.desc())
        .first()
    )
    path_data = loads(item.path_json, {}) if item else {"course_title": course.title, "stages": []}
    stages = path_data.get("stages") or path_data.get("steps") or []
    stages.append(
        {
            "name": "个性化资源包学习",
            "target": f"学习资源包 {payload.package_id} 中的 9 类资源，并完成一次复盘。",
            "resource_package_id": payload.package_id,
            "source": "resource_added_to_path",
            "demo_fallback": True,
        }
    )
    path_data["stages"] = stages
    path_data["latest_adjustment_reason"] = "根据画像和资源生成结果自动加入学习路径。"
    if item:
        item.path_json = dumps(path_data)
    else:
        item = LearningPath(student_profile_id=profile.id, course_id=course.id, path_json=dumps(path_data))
        db.add(item)
    db.flush()
    for event_type, title in [("resource_added_to_path", "资源包加入学习路径"), ("path_updated", "学习路径已更新")]:
        record_event(
            db,
            event_type=event_type,
            title=title,
            description=f"{payload.package_id} 已绑定到 {profile.student_name} 的学习路径。",
            actor_id=actor_id,
            actor_role=actor_role,
            actor_name=actor_name,
            target_type="learning_path",
            target_id=item.id,
            related_student=profile.student_name,
            related_course=course.title,
            metadata={"package_id": payload.package_id, "course_id": course.id, "path_id": item.id},
            commit=False,
        )
    db.commit()
    db.refresh(item)
    return {"path_id": item.id, "path_json": loads(item.path_json, {}), "status": "success"}


@router.post("/assign-task")
def assign_task(
    payload: TaskAssignPayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_staff),
):
    course = _target_course(db, current_user, payload.course_id)
    profile = _target_profile(db, current_user, payload.student_profile_id, course)
    actor_id, actor_name, actor_role = current_user_label(current_user)
    due = payload.due_date or (date.today() + timedelta(days=3)).isoformat()
    task = {
        "task_id": f"task-{course.id}-{profile.id}-{date.today().isoformat()}",
        "weak_point": payload.weak_point,
        "task_type": payload.task_type,
        "due_date": due,
        "status": "assigned",
    }
    if db.query(SystemLog).filter(SystemLog.type == EVENT_LOG_TYPE, SystemLog.related_id == task["task_id"]).first():
        raise HTTPException(status_code=409, detail="该任务已分配")
    for event_type, title in [("teacher_intervention_created", "教师创建干预"), ("task_assigned", "教师布置补强任务")]:
        record_event(
            db,
            event_type=event_type,
            title=title,
            description=f"{payload.task_type}：{payload.weak_point}，截止 {due}。",
            actor_id=actor_id,
            actor_role=actor_role,
            actor_name=actor_name,
            target_type="student_task",
            target_id=task["task_id"],
            related_student=profile.student_name,
            related_course=course.title,
            metadata={"task": task, "course_id": course.id, "student_profile_id": profile.id},
            commit=False,
        )
    db.commit()
    return {"task": task, "status": "success", "demo_fallback_note": "任务通过业务事件写入 system_logs，学生端可读取展示。"}


@router.post("/demo-quiz")
def complete_demo_quiz(
    payload: DemoQuizPayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_authenticated_user),
):
    if payload.course_id is None:
        raise HTTPException(status_code=422, detail="必须指定课程")
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在或不可访问")
    profile = _target_profile(db, current_user, payload.student_profile_id, course)
    if current_user.get("role") in {"teacher", "admin"}:
        course = _target_course(db, current_user, payload.course_id)
    actor_id, actor_name, actor_role = current_user_label(current_user)
    quiz = db.query(Quiz).filter(Quiz.course_id == course.id).first()
    if not quiz:
        quiz = Quiz(course_id=course.id, student_profile_id=profile.id, quiz_json=dumps({"title": "demo 测验"}))
        db.add(quiz)
        db.flush()
    result = {
        "score": 78,
        "weak_points": ["while 循环终止条件", "循环嵌套变量变化", "break / continue 区分"],
        "mastery_delta": 0.08,
        "suggested_resources": ["分层练习题", "代码示例", "实验案例"],
    }
    submission = QuizSubmission(
        quiz_id=quiz.id,
        student_profile_id=profile.id,
        answers_json=dumps({"demo": True}),
        score=result["score"],
        feedback_json=dumps(result),
    )
    db.add(submission)
    db.flush()
    record_event(
        db,
        event_type="quiz_completed",
        title="完成一次 demo 测验",
        description=f"{profile.student_name} 完成测验，得分 {result['score']}，薄弱点已反馈到画像和资源推荐。",
        actor_id=actor_id,
        actor_role=actor_role,
        actor_name=actor_name,
        target_type="quiz_submission",
        target_id=submission.id,
        related_student=profile.student_name,
        related_course=course.title,
        metadata={"quiz_result": result, "course_id": course.id, "student_profile_id": profile.id},
        commit=False,
    )
    db.commit()
    return {"id": submission.id, "quiz_result": result, "created_at": submission.created_at}


@router.post("/admin-review")
def admin_review(
    payload: EventPayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin),
):
    actor_id, actor_name, actor_role = current_user_label(current_user)
    data = payload.model_dump(exclude={"actor_id", "actor_name", "actor_role"})
    data["event_type"] = "admin_review_completed"
    data["title"] = data["title"] or "管理员审核完成"
    item = record_event(db, **data, actor_id=actor_id, actor_name=actor_name, actor_role=actor_role)
    return {"event_id": item.id, "status": "success"}
