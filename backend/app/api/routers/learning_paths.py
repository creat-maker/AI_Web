from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, LearningPath, StudentProfile
from app.services.json_utils import loads
from app.services.learning_path_service import adjust_learning_path, create_learning_path


router = APIRouter(prefix="/learning-paths", tags=["learning-paths"])


class LearningPathGeneratePayload(BaseModel):
    profile_id: int


class LearningPathAdjustPayload(BaseModel):
    profile_id: int
    trigger: str = "manual"
    detected_new_weak_points: list[str] | None = None
    resolved_weak_points: list[str] | None = None
    reason: str = ""


def path_to_dict(item: LearningPath) -> dict:
    return {
        "id": item.id,
        "course_id": item.course_id,
        "student_profile_id": item.student_profile_id,
        "path_json": loads(item.path_json, {}),
        "adjustment_log": loads(item.adjustment_log, []),
        "created_at": item.created_at,
    }


@router.get("")
def list_items(course_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(LearningPath)
    if course_id:
        query = query.filter(LearningPath.course_id == course_id)
    return [path_to_dict(item) for item in query.order_by(LearningPath.id.desc()).all()]


@router.post("/generate")
def generate_learning_path(payload: LearningPathGeneratePayload, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.id == payload.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="学生画像不存在")
    course = db.query(Course).filter(Course.id == profile.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return path_to_dict(create_learning_path(db, profile, course))


@router.post("/adjust")
def adjust_path(payload: LearningPathAdjustPayload, db: Session = Depends(get_db)):
    """根据薄弱点变化动态调整学习路径。"""
    profile = db.query(StudentProfile).filter(StudentProfile.id == payload.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="学生画像不存在")
    course = db.query(Course).filter(Course.id == profile.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    path = (
        db.query(LearningPath)
        .filter(LearningPath.student_profile_id == payload.profile_id)
        .order_by(LearningPath.id.desc())
        .first()
    )
    if not path:
        raise HTTPException(status_code=404, detail="学习路径不存在，请先生成路径")
    adjusted = adjust_learning_path(
        db,
        path,
        profile,
        course,
        trigger=payload.trigger,
        detected_new=payload.detected_new_weak_points,
        resolved=payload.resolved_weak_points,
        reason=payload.reason,
    )
    return path_to_dict(adjusted)


@router.get("/{profile_id}")
def get_learning_path(profile_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(LearningPath)
        .filter(LearningPath.student_profile_id == profile_id)
        .order_by(LearningPath.id.desc())
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="学习路径不存在")
    return path_to_dict(item)
