from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, GeneratedResource, LearningPath, Quiz, QuizSubmission, StudentProfile
from app.services.business_event_service import event_to_dict, list_events, record_event
from app.services.json_utils import dumps, loads


router = APIRouter(prefix="/events", tags=["events"])


RESOURCE_TYPES = ["知识讲义", "PPT 提纲", "分层练习题", "思维导图", "拓展阅读", "实验案例", "代码示例", "微课视频脚本"]


class EventPayload(BaseModel):
    event_type: str
    title: str
    description: str
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
def create_event(payload: EventPayload, db: Session = Depends(get_db)):
    item = record_event(db, **payload.model_dump())
    return event_to_dict(item)


def _first_course(db: Session, course_id: int | None) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first() if course_id else db.query(Course).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在，请先运行演示数据脚本。")
    return course


def _first_profile(db: Session, profile_id: int | None) -> StudentProfile | None:
    if profile_id:
        return db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
    return db.query(StudentProfile).first()


@router.post("/resource-package")
def create_resource_package(payload: ResourcePackagePayload, db: Session = Depends(get_db)):
    course = _first_course(db, payload.course_id)
    profile = _first_profile(db, payload.student_profile_id)
    weak_points = loads(profile.weak_points, []) if profile else ["while 循环终止条件", "break / continue 区分"]
    package_id = f"pkg-{course.id}-{profile.id if profile else 0}-{date.today().isoformat()}"
    resources = []
    for index, resource_type in enumerate(RESOURCE_TYPES, start=1):
        resource = GeneratedResource(
            course_id=course.id,
            student_profile_id=profile.id if profile else None,
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
        description=f"已为 {profile.student_name if profile else '演示学生'} 生成 8 类资源包。",
        actor_role=payload.actor_role,
        actor_name=payload.actor_name,
        target_type="resource_package",
        target_id=package_id,
        related_student=profile.student_name if profile else "",
        related_course=course.title,
        metadata={"package_id": package_id, "resource_count": len(resources), "resource_types": RESOURCE_TYPES, "course_id": course.id},
        commit=False,
    )
    db.commit()
    for item in resources:
        db.refresh(item)
    return {
        "package_id": package_id,
        "course_id": course.id,
        "student_profile_id": profile.id if profile else None,
        "resources": resources,
        "demo_fallback_note": "资源包由 EduMind fallback API 生成，用于演示画像到资源生成闭环。",
    }


@router.post("/add-resource-to-path")
def add_resource_to_path(payload: AddToPathPayload, db: Session = Depends(get_db)):
    course = _first_course(db, payload.course_id)
    profile = _first_profile(db, payload.student_profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="学生画像不存在，请先生成画像。")
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
            "target": f"学习资源包 {payload.package_id} 中的 8 类资源，并完成一次复盘。",
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
            actor_role=payload.actor_role,
            actor_name=payload.actor_name,
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
def assign_task(payload: TaskAssignPayload, db: Session = Depends(get_db)):
    course = _first_course(db, payload.course_id)
    profile = _first_profile(db, payload.student_profile_id)
    due = payload.due_date or (date.today() + timedelta(days=3)).isoformat()
    task = {
        "task_id": f"task-{course.id}-{profile.id if profile else 0}-{date.today().isoformat()}",
        "weak_point": payload.weak_point,
        "task_type": payload.task_type,
        "due_date": due,
        "status": "assigned",
    }
    for event_type, title in [("teacher_intervention_created", "教师创建干预"), ("task_assigned", "教师布置补强任务")]:
        record_event(
            db,
            event_type=event_type,
            title=title,
            description=f"{payload.task_type}：{payload.weak_point}，截止 {due}。",
            actor_role=payload.actor_role,
            actor_name=payload.actor_name,
            target_type="student_task",
            target_id=task["task_id"],
            related_student=profile.student_name if profile else "",
            related_course=course.title,
            metadata={"task": task, "course_id": course.id, "student_profile_id": profile.id if profile else None},
            commit=False,
        )
    db.commit()
    return {"task": task, "status": "success", "demo_fallback_note": "任务通过业务事件写入 system_logs，学生端可读取展示。"}


@router.post("/demo-quiz")
def complete_demo_quiz(payload: DemoQuizPayload, db: Session = Depends(get_db)):
    course = _first_course(db, payload.course_id)
    profile = _first_profile(db, payload.student_profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="学生画像不存在，请先生成画像。")
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
        actor_role=payload.actor_role,
        actor_name=payload.actor_name,
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
def admin_review(payload: EventPayload, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["event_type"] = "admin_review_completed"
    data["title"] = data["title"] or "管理员审核完成"
    data["actor_role"] = "admin"
    item = record_event(db, **data)
    return {"event_id": item.id, "status": "success"}
