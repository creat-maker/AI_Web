from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Course, Quiz, QuizSubmission, StudentProfile
from app.services.json_utils import dumps, loads
from app.services.llm_service import llm_service


def create_quiz(db: Session, course: Course, profile: StudentProfile | None = None) -> Quiz:
    quiz_json = llm_service.generate_json("quiz", {"course_title": course.title})
    quiz = Quiz(
        course_id=course.id,
        student_profile_id=profile.id if profile else None,
        quiz_json=dumps(quiz_json),
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def submit_quiz(db: Session, quiz: Quiz, profile: StudentProfile, answers: dict) -> QuizSubmission:
    result = llm_service.generate_json(
        "evaluate",
        {
            "quiz": loads(quiz.quiz_json, {}),
            "answers": answers,
            "profile": loads(profile.profile_json, {}),
        },
    )
    submission = QuizSubmission(
        quiz_id=quiz.id,
        student_profile_id=profile.id,
        answers_json=dumps(answers),
        score=float(result.get("score", 0)),
        feedback_json=dumps(result),
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def list_quizzes(db: Session, course_id: int | None = None) -> list[Quiz]:
    query = db.query(Quiz)
    if course_id:
        query = query.filter(Quiz.course_id == course_id)
    return query.order_by(Quiz.id.desc()).all()
