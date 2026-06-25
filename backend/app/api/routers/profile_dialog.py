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
from app.services.profile_dialog_service import PROFILE_DIMENSIONS, continue_dialog, finish_dialog, start_dialog
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


def _six_dimension_payload(values: dict[str, Any]) -> dict[str, Any]:
    weak_points = values.get("error_prone_points") or values.get("weak_points") or values.get("weakKnowledgePoints") or []
    if isinstance(weak_points, str):
        weak_points = [weak_points]
    dimension_values = {
        "knowledge_base": values.get("knowledge_base") or values.get("foundationLevel") or values.get("current_level") or "基础待评估",
        "cognitive_style": values.get("cognitive_style") or values.get("learning_style") or "步骤拆解 + 图解直观型",
        "learning_preference": values.get("learning_preference") or values.get("learningPreference") or "代码案例 + 分层练习",
        "error_prone_points": weak_points,
        "learning_progress": values.get("learning_progress") or values.get("diagnosis") or values.get("learningRisk") or "随学更新中",
        "emotional_motivation": values.get("emotional_motivation") or values.get("learningGoal") or values.get("strategy") or "目标驱动，需要阶段性正反馈",
    }
    dimensions = [
        {
            "key": item["key"],
            "label": item["label"],
            "description": item["description"],
            "value": dimension_values[item["key"]],
        }
        for item in PROFILE_DIMENSIONS
    ]
    return {
        **dimension_values,
        "profile_dimensions": PROFILE_DIMENSIONS,
        "dimension_scores": {
            "knowledge_base": 62,
            "cognitive_style": 78,
            "learning_preference": 82,
            "error_prone_points": 55,
            "learning_progress": 68,
            "emotional_motivation": 74,
        },
        "dimensions": dimensions,
        "current_level": dimension_values["knowledge_base"],
        "weak_points": weak_points,
        "diagnosis": dimension_values["learning_progress"],
        "strategy": f"优先围绕{ '、'.join(str(item) for item in weak_points[:3]) if weak_points else '当前薄弱点' }安排讲义、动画、练习和测评反馈。",
    }


def _fallback_run_profile(payload: dict[str, Any], error: str = "") -> dict[str, Any]:
    student_name = payload.get("studentName") or payload.get("student_name") or "李明"
    course_name = payload.get("courseName") or payload.get("course_name") or "Python Programming"
    weak_points = (
        payload.get("weakPoints")
        or payload.get("weak_points")
        or ["while 循环", "循环嵌套", "break / continue"]
    )
    if isinstance(weak_points, str):
        weak_points = [weak_points]
    dimensions = [
        {"key": "knowledge_base", "name": "知识基础", "value": "基础薄弱，已具备基础语法但循环结构不稳定。"},
        {"key": "cognitive_style", "name": "认知风格", "value": "步骤拆解 + 变量变化图解更有效。"},
        {"key": "learning_preference", "name": "学习偏好", "value": "代码实操案例、变量变化图解、分层练习题"},
        {"key": "error_prone_points", "name": "易错点", "value": " / ".join(str(item) for item in weak_points)},
        {"key": "learning_progress", "name": "学习进度", "value": "正在进行循环结构专项补弱。"},
        {"key": "emotional_motivation", "name": "情感动机", "value": f"目标是补齐 {course_name} 的循环结构薄弱点并完成课程任务。"},
    ]
    result = {
        "studentId": payload.get("studentId") or payload.get("student_id") or "demo-student",
        "studentName": student_name,
        "courseId": payload.get("courseId") or payload.get("course_id") or "demo-course",
        "courseName": course_name,
        "summary": f"系统已根据 {student_name} 的 Python 循环结构学习情况生成个性化建议。",
        "dimensions": dimensions,
        "learningGoal": dimensions[5]["value"],
        "foundationLevel": dimensions[0]["value"],
        "weakKnowledgePoints": [str(item) for item in weak_points],
        "learningPreference": dimensions[2]["value"],
        "timeArrangement": "每天 20 到 30 分钟循环结构专项练习",
        "learningRisk": "需巩固",
        "recommendedStrategy": "先修复 while 死循环，再区分 break / continue，最后完成循环嵌套实操",
        "mode": "structured-profile",
        "error": error,
    }
    result.update(_six_dimension_payload(result))
    return result


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
        result.setdefault("summary", f"{student_name} 的 {course_name} 循环结构画像已生成。")
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
        result.setdefault("recommendedStrategy", "先修复 while 死循环，再区分 break / continue，最后完成循环嵌套实操")
        result.setdefault("mode", "rule-compatible")
        if not result.get("dimensions"):
            return _fallback_run_profile({**data, **result}, "profile service returned no dimensions")
        standard_values = {
            "knowledge_base": stable_profile["knowledge_level"],
            "cognitive_style": stable_profile.get("learning_style") or "步骤拆解型",
            "learning_preference": stable_profile["learning_preference"],
            "error_prone_points": stable_profile["weak_points"],
            "learning_progress": stable_profile.get("risk_level") or "需巩固",
            "emotional_motivation": stable_profile["learning_goal"],
        }
        result["dimensions"] = [
            {
                "key": item["key"],
                "name": item["label"],
                "label": item["label"],
                "description": item["description"],
                "value": standard_values.get(item["key"], ""),
            }
            for item in PROFILE_DIMENSIONS
        ]
        result.update(_six_dimension_payload({**result, **stable_profile, **standard_values}))
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
    weak_points = extracted.get("error_prone_points") or extracted.get("weak_points", [])
    if isinstance(weak_points, str):
        weak_points = [weak_points]
    return {
        "student_name": session["student_name"],
        "knowledge_base": extracted.get("knowledge_base", "待评估"),
        "cognitive_style": extracted.get("cognitive_style", "步骤拆解型"),
        "error_prone_points": weak_points,
        "learning_progress": extracted.get("learning_progress", ""),
        "emotional_motivation": extracted.get("emotional_motivation", ""),
        "current_level": extracted.get("knowledge_base", extracted.get("current_level", "待评估")),
        "learning_goal": extracted.get("emotional_motivation", extracted.get("learning_goal", "")),
        "weak_points": weak_points,
        "learning_preference": extracted.get("learning_preference", "案例驱动"),
        "diagnosis": extracted.get("learning_progress", extracted.get("diagnosis", f"当前主要短板集中在{', '.join(weak_points) if weak_points else '基础概念'}。")),
        "strategy": extracted.get("strategy", "采用短讲义、可运行案例、即时测验和错因反馈的组合。"),
        "dimensions": [
            {"key": item["key"], "label": item["label"], "description": item["description"], "value": extracted.get(item["key"], "")}
            for item in PROFILE_DIMENSIONS
        ],
        "profile_dimensions": PROFILE_DIMENSIONS,
        "dimension_scores": {
            item["key"]: 80 if extracted.get(item["key"]) else 50
            for item in PROFILE_DIMENSIONS
        },
        "source": "dialog",
    }
