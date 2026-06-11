"""对话式画像构建 API：支持自由多轮对话抽取学生 6 维画像。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_demo_user_id
from app.db.session import get_db
from app.models import Course, StudentProfile
from app.services.demo_profile_chain import get_demo_student, normalize_profile_schema
from app.services.json_utils import dumps
from app.services.personalization_service import run_profile_dialog
from app.services.profile_dialog_service import continue_dialog, finish_dialog, start_dialog
from app.services.profile_service import latest_profile_by_user_id, profile_to_dict, update_profile_by_learning


router = APIRouter(prefix="/profile-dialog", tags=["profile-dialog"])


class DialogStartPayload(BaseModel):
    student_name: str
    course_id: int


class DialogContinuePayload(BaseModel):
    session_id: str
    message: str


class DialogFinishPayload(BaseModel):
    session_id: str


class DialogSavePayload(BaseModel):
    session_id: str
    user_id: str | None = None


class ProfileLearningUpdatePayload(BaseModel):
    user_id: str | None = None
    event_type: str = "quiz"
    weak_point: str | None = None
    score: float | None = None
    question: str | None = None
    resource_id: str | int | None = None


class DialogRunPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    studentId: str | int | None = None
    studentName: str | None = None
    courseId: str | int | None = None
    courseName: str | None = None
    answer: str | None = None
    message: str | None = None
    dialog: str | None = None
    profileAnswer: str | None = None
    answers: list[Any] | None = None
    dialogAnswers: list[Any] | None = None
    weakPoints: list[str] = Field(default_factory=list)
    weak_points: list[str] = Field(default_factory=list)


def _fallback_run_profile(payload: dict[str, Any], error: str = "") -> dict[str, Any]:
    student_name = payload.get("studentName") or payload.get("student_name") or "demo-student"
    course_name = payload.get("courseName") or payload.get("course_name") or "Python Programming"
    weak_points = (
        payload.get("weakPoints")
        or payload.get("weak_points")
        or ["Python file handling", "recursion boundary", "debugging"]
    )
    if isinstance(weak_points, str):
        weak_points = [weak_points]
    dimensions = [
        {"name": "learning_goal", "value": f"Improve weak knowledge points in {course_name}."},
        {"name": "foundation_level", "value": "needs targeted practice"},
        {"name": "weak_knowledge_points", "value": " / ".join(str(item) for item in weak_points)},
        {"name": "learning_preference", "value": "examples, short notes, and practice tasks"},
        {"name": "time_arrangement", "value": "20 to 30 minutes of focused practice per day"},
        {"name": "learning_risk", "value": "medium"},
        {"name": "recommended_strategy", "value": "review concepts, practice by level, then finish a small task"},
    ]
    return {
        "studentId": payload.get("studentId") or payload.get("student_id") or "demo-student",
        "studentName": student_name,
        "courseId": payload.get("courseId") or payload.get("course_id") or "demo-course",
        "courseName": course_name,
        "summary": f"{student_name} profile generated with compatible fallback data.",
        "dimensions": dimensions,
        "learningGoal": dimensions[0]["value"],
        "foundationLevel": dimensions[1]["value"],
        "weakKnowledgePoints": [str(item) for item in weak_points],
        "learningPreference": dimensions[3]["value"],
        "timeArrangement": dimensions[4]["value"],
        "learningRisk": dimensions[5]["value"],
        "recommendedStrategy": dimensions[6]["value"],
        "mode": "structured-fallback",
        "error": error,
    }


@router.post("/run")
def dialog_run(payload: DialogRunPayload, current_user_id: str = Depends(get_demo_user_id)):
    """Compatibility endpoint for the single-turn StudentAssistant profile flow."""
    data = payload.model_dump()
    data["studentId"] = data.get("studentId") or current_user_id
    if data.get("studentId"):
        student = get_demo_student(data.get("studentId"))
        data["studentName"] = student["student_name"]
        data["courseName"] = student["course_name"]
        data["weakPoints"] = student["weak_points"]
        data["answer"] = data.get("answer") or (
            f"我是{student['student_name']}，当前{student['current_level']}，目标是{student['learning_goal']}，"
            f"薄弱点包括{'、'.join(student['weak_points'])}，偏好{student['learning_preference']}。"
        )
    try:
        result = run_profile_dialog(data)
        if not isinstance(result, dict):
            return _fallback_run_profile(data, "profile service returned a non-object result")

        # Keep StudentAssistant's expected contract stable even if the service evolves.
        student_name = data.get("studentName") or data.get("student_name") or "demo-student"
        course_name = data.get("courseName") or data.get("course_name") or "Python Programming"
        result.setdefault("studentId", data.get("studentId") or data.get("student_id") or "demo-student")
        result.setdefault("studentName", student_name)
        result.setdefault("courseId", data.get("courseId") or data.get("course_id") or "demo-course")
        result.setdefault("courseName", course_name)
        result.setdefault("summary", f"{student_name} profile generated for {course_name}.")
        result.setdefault("weakKnowledgePoints", data.get("weakPoints") or data.get("weak_points") or [])
        if isinstance(result.get("weakKnowledgePoints"), str):
            result["weakKnowledgePoints"] = [result["weakKnowledgePoints"]]
        stable_profile = normalize_profile_schema(
            {
                "user_id": result.get("studentId"),
                "student_name": result.get("studentName"),
                "course_name": result.get("courseName"),
                "learning_goal": result.get("learningGoal"),
                "current_level": result.get("foundationLevel"),
                "weak_points": result.get("weakKnowledgePoints"),
                "learning_style": result.get("learningPreference"),
                "recommended_strategy": result.get("recommendedStrategy"),
            },
            result.get("studentId"),
        )
        result.update(stable_profile)
        result.setdefault("recommendedStrategy", "review concepts, practice by level, then finish a small task")
        result.setdefault("mode", "rule-compatible")
        if not result.get("dimensions"):
            return _fallback_run_profile({**data, **result}, "profile service returned no dimensions")
        return result
    except Exception as exc:  # noqa: BLE001
        return _fallback_run_profile(data, str(exc))


@router.post("/start")
def dialog_start(payload: DialogStartPayload, db: Session = Depends(get_db)):
    """开启对话式画像构建会话。"""
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return start_dialog(payload.student_name, payload.course_id)


@router.post("/continue")
def dialog_continue(payload: DialogContinuePayload):
    """继续对话，发送用户回复并获取 AI 回复。"""
    result = continue_dialog(payload.session_id, payload.message)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/finish")
def dialog_finish(payload: DialogFinishPayload):
    """用户主动确认完成画像构建。"""
    result = finish_dialog(payload.session_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/save")
def dialog_save(payload: DialogSavePayload, db: Session = Depends(get_db), current_user_id: str = Depends(get_demo_user_id)):
    """将对话完成的画像保存到数据库。"""
    from app.services.profile_dialog_service import get_session

    session = get_session(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if not session.get("completed"):
        raise HTTPException(status_code=400, detail="对话尚未完成，无法保存画像")

    user_id = payload.user_id or current_user_id
    profile_json = normalize_profile_schema(_build_profile_json(session), user_id)
    extracted = session.get("extracted", {})

    weak_points = extracted.get("weak_points") or profile_json["weak_points"]
    if isinstance(weak_points, list):
        weak_points_str = dumps(weak_points)
    else:
        weak_points_str = dumps([weak_points])

    profile = StudentProfile(
        student_name=profile_json["student_name"],
        course_id=session["course_id"],
        current_level=profile_json["current_level"],
        learning_goal=profile_json["learning_goal"],
        weak_points=weak_points_str,
        learning_preference=profile_json["learning_style"],
        profile_json=dumps(profile_json),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile_to_dict(profile)


@router.post("/update-by-learning")
def update_by_learning(
    payload: ProfileLearningUpdatePayload,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_demo_user_id),
):
    user_id = payload.user_id or current_user_id
    profile = latest_profile_by_user_id(db, user_id)
    if not profile:
        student = get_demo_student(user_id)
        profile_json = normalize_profile_schema(student, user_id)
        profile = StudentProfile(
            student_name=profile_json["student_name"],
            course_id=profile_json["course_id"],
            current_level=profile_json["current_level"],
            learning_goal=profile_json["learning_goal"],
            weak_points=dumps(profile_json["weak_points"]),
            learning_preference=profile_json["learning_style"],
            profile_json=dumps(profile_json),
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return update_profile_by_learning(
        db,
        profile,
        event_type=payload.event_type,
        weak_point=payload.weak_point,
        score=payload.score,
        question=payload.question,
        resource_id=payload.resource_id,
    )


def _build_profile_json(session: dict) -> dict:
    extracted = session.get("extracted", {})
    weak_points = extracted.get("weak_points", [])
    if isinstance(weak_points, str):
        weak_points = [weak_points]
    return {
        "student_name": session["student_name"],
        "current_level": extracted.get("current_level", "待评估"),
        "learning_goal": extracted.get("learning_goal", ""),
        "weak_points": weak_points,
        "learning_preference": extracted.get("learning_preference", "案例驱动"),
        "diagnosis": extracted.get("diagnosis", f"当前主要短板集中在{', '.join(weak_points) if weak_points else '基础概念'}。"),
        "strategy": extracted.get("strategy", "采用短讲义、可运行案例、即时测验和错因反馈的组合。"),
        "source": "dialog",
    }
