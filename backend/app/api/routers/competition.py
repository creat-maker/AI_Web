from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import require_admin
from app.services.competition_mock_service import (
    QUIZ,
    generate_teacher_workbench,
    get_knowledge_graph,
    get_learning_tasks,
    get_platform_quality,
    submit_quiz_answers,
)
from app.services.demo_learning_service import build_content_review_items
from app.services.demo_profile_chain import build_learning_tasks


router = APIRouter(tags=["competition-closed-loop"])


class QuizSubmitPayload(BaseModel):
    quiz_id: str = "python-chapter-1"
    student_id: str = "demo-student-zhangsan"
    answers: dict[str, str] = Field(default_factory=dict)


class TeacherWorkbenchPayload(BaseModel):
    type: str = "lesson_plan"
    course: str = "Python 程序设计"
    chapter: str = "循环结构"
    student_foundation: str = "基础差异较大"
    teaching_goal: str = "掌握核心语法并能完成小任务"


@router.get("/knowledge-graph")
def knowledge_graph():
    return get_knowledge_graph()


@router.get("/student/learning-tasks")
def student_learning_tasks(profile_type: str | None = None, user_id: str | None = None):
    if user_id:
        return build_learning_tasks(user_id=user_id, profile_type=profile_type)
    return get_learning_tasks(profile_type)


@router.get("/quiz/chapter")
def quiz_chapter():
    return QUIZ


@router.post("/quiz/submit")
def quiz_submit(payload: QuizSubmitPayload):
    return submit_quiz_answers(payload.answers)


@router.post("/teacher/ai-workbench/generate")
def teacher_ai_workbench_generate(payload: TeacherWorkbenchPayload):
    return generate_teacher_workbench(payload.model_dump())


@router.get("/admin/content-review")
def admin_content_review(current_user: dict[str, Any] = Depends(require_admin)):
    return build_content_review_items()


@router.get("/admin/platform-quality")
def admin_platform_quality(current_user: dict[str, Any] = Depends(require_admin)) -> dict[str, Any]:
    return get_platform_quality()
