from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.models import Course, LearningPath, Quiz, QuizSubmission, StudentProfile
from app.services.json_utils import dumps, loads
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


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

    # 测评后自动检测是否需要调整学习路径
    _try_adjust_path_after_quiz(db, profile, result)

    return submission


def _try_adjust_path_after_quiz(db: Session, profile: StudentProfile, evaluation_result: dict) -> None:
    """测评提交后，若薄弱点发生变化，自动触发路径调整。"""
    if not evaluation_result.get("path_adjustment_needed"):
        return

    course = db.query(Course).filter(Course.id == profile.course_id).first()
    if not course:
        return

    path = (
        db.query(LearningPath)
        .filter(LearningPath.student_profile_id == profile.id)
        .order_by(LearningPath.id.desc())
        .first()
    )
    if not path:
        logger.info("学生 %s 尚无学习路径，跳过自动调整", profile.student_name)
        return

    from app.services.learning_path_service import adjust_learning_path

    detected_new = evaluation_result.get("detected_new_weak_points", [])
    resolved = evaluation_result.get("resolved_weak_points", [])
    reason = evaluation_result.get("adjustment_reason", "测验后自动调整")

    try:
        adjust_learning_path(
            db,
            path,
            profile,
            course,
            trigger="quiz_submission",
            detected_new=detected_new,
            resolved=resolved,
            reason=reason,
        )
        logger.info(
            "学生 %s 测评后自动调整路径：新增薄弱点 %s，已掌握 %s",
            profile.student_name,
            detected_new,
            resolved,
        )
    except Exception:
        logger.exception("自动调整学习路径失败，学生 %s", profile.student_name)


def list_quizzes(db: Session, course_id: int | None = None) -> list[Quiz]:
    query = db.query(Quiz)
    if course_id:
        query = query.filter(Quiz.course_id == course_id)
    return query.order_by(Quiz.id.desc()).all()
