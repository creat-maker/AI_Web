from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.db.session import get_db
from app.models import AgentRun, Course, GeneratedResource, LearningReport, Quiz, StudentProfile
from app.services.course_service import create_course, delete_course, get_course, list_courses, update_course


router = APIRouter(prefix="/courses", tags=["courses"])


class CoursePayload(BaseModel):
    title: str
    description: str | None = None
    subject: str | None = None
    teacher_name: str | None = None


@router.get("")
def list_items(db: Session = Depends(get_db)):
    return list_courses(db)


@router.post("")
def create_item(payload: CoursePayload, db: Session = Depends(get_db)):
    return create_course(db, payload.model_dump())


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    return {
        "courses": db.query(Course).count(),
        "profiles": db.query(StudentProfile).count(),
        "resources": db.query(GeneratedResource).count(),
        "quizzes": db.query(Quiz).count(),
        "reports": db.query(LearningReport).count(),
        "agent_runs": db.query(AgentRun).count(),
        "demo_data_note": "TeacherAnalysis 可展示少量 demo 样例，Dashboard 统计来自数据库真实记录。",
    }


@router.get("/{course_id}")
def get_item(course_id: int, db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return course


@router.put("/{course_id}")
def update_item(course_id: int, payload: CoursePayload, db: Session = Depends(get_db)):
    course = update_course(db, course_id, payload.model_dump())
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return course


@router.delete("/{course_id}")
def delete_item(course_id: int, db: Session = Depends(get_db)):
    if not delete_course(db, course_id):
        raise HTTPException(status_code=404, detail="课程不存在")
    return {"ok": True}
