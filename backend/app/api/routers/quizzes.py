from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, Quiz, StudentProfile
from app.services.json_utils import loads
from app.services.quiz_service import create_quiz, list_quizzes, submit_quiz


router = APIRouter(prefix="/quizzes", tags=["quizzes"])


class QuizGeneratePayload(BaseModel):
    course_id: int
    student_profile_id: int | None = None


class SubmitPayload(BaseModel):
    quiz_id: int
    student_profile_id: int
    answers: dict


def quiz_to_dict(item: Quiz) -> dict:
    return {
        "id": item.id,
        "course_id": item.course_id,
        "student_profile_id": item.student_profile_id,
        "quiz_json": loads(item.quiz_json, {}),
        "created_at": item.created_at,
    }


@router.get("")
def list_items(course_id: int | None = None, db: Session = Depends(get_db)):
    return [quiz_to_dict(item) for item in list_quizzes(db, course_id)]


@router.post("/generate")
def generate_quiz(payload: QuizGeneratePayload, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    profile = None
    if payload.student_profile_id:
        profile = db.query(StudentProfile).filter(StudentProfile.id == payload.student_profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="学生画像不存在")
    return quiz_to_dict(create_quiz(db, course, profile))


@router.post("/submit")
def submit(payload: SubmitPayload, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == payload.quiz_id).first()
    profile = db.query(StudentProfile).filter(StudentProfile.id == payload.student_profile_id).first()
    if not quiz or not profile:
        raise HTTPException(status_code=404, detail="测验或学生画像不存在")
    submission = submit_quiz(db, quiz, profile, payload.answers)
    return {
        "id": submission.id,
        "score": submission.score,
        "feedback_json": loads(submission.feedback_json, {}),
        "created_at": submission.created_at,
    }


@router.get("/analysis")
def analysis(db: Session = Depends(get_db)):
    quiz_count = db.query(Quiz).count()
    return {
        "real": {"quiz_count": quiz_count},
        "demo": {
            "source": "内置演示样例，仅用于第一版 TeacherAnalysis 图表占位，不计入真实统计。",
            "weak_point_distribution": [
                {"name": "函数", "value": 32},
                {"name": "文件操作", "value": 24},
                {"name": "HTTP 请求", "value": 44},
            ],
        },
    }
