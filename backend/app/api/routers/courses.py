from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_staff
from app.db.session import get_db
from app.models import AgentRun, Course, GeneratedResource, LearningReport, Quiz, StudentProfile
from app.services.course_service import create_course, delete_course, get_course, list_courses, update_course
from app.services.teacher_scope_service import get_course_for_write, principal_name

router = APIRouter(prefix="/courses", tags=["courses"])


class CoursePayload(BaseModel):
    title: str
    description: str | None = None
    subject: str | None = None
    teacher_name: str | None = None
    course_code: str | None = None
    chapter_count: int | None = None
    status: str | None = None
    tags: list[str] | None = None


def _to_course_data(payload: CoursePayload) -> dict:
    data = payload.model_dump()
    tags = data.pop("tags", None) or []
    course_code = data.pop("course_code", None)
    chapter_count = data.pop("chapter_count", None)
    status = data.pop("status", None)

    notes: list[str] = []
    if course_code:
        notes.append(f"课程编号：{course_code}")
    if chapter_count is not None:
        notes.append(f"章节数：{chapter_count}")
    if status:
        notes.append(f"状态：{status}")
    if tags:
        notes.append(f"知识点：{'、'.join(tags)}")
    if notes:
        base = data.get("description") or ""
        data["description"] = f"{base}\n" + "\n".join(notes) if base else "\n".join(notes)
    return data


@router.get("")
def list_items(db: Session = Depends(get_db)):
    return list_courses(db)


@router.post("")
def create_item(
    payload: CoursePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_staff),
):
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="课程名称不能为空")
    data = _to_course_data(payload)
    if current_user.get("role") == "teacher":
        data["teacher_name"] = principal_name(current_user)
    return create_course(db, data)


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    return {
        "courses": db.query(Course).count(),
        "profiles": db.query(StudentProfile).count(),
        "resources": db.query(GeneratedResource).count(),
        "quizzes": db.query(Quiz).count(),
        "reports": db.query(LearningReport).count(),
        "agent_runs": db.query(AgentRun).count(),
        "data_note": "Dashboard 统计来自当前数据库记录，课程、资源、报告会随用户操作更新。",
    }


@router.get("/{course_id}")
def get_item(course_id: int, db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return course


@router.put("/{course_id}")
def update_item(
    course_id: int,
    payload: CoursePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_staff),
):
    get_course_for_write(db, current_user, course_id)
    data = _to_course_data(payload)
    if current_user.get("role") == "teacher":
        data["teacher_name"] = principal_name(current_user)
    course = update_course(db, course_id, data)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return course


@router.delete("/{course_id}")
def delete_item(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_staff),
):
    get_course_for_write(db, current_user, course_id)
    if not delete_course(db, course_id):
        raise HTTPException(status_code=404, detail="课程不存在")
    return {"ok": True}
