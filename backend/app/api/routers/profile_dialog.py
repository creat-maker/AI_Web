"""对话式画像构建 API：支持自由多轮对话抽取学生 6 维画像。"""

from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, StudentProfile
from app.services.json_utils import dumps
from app.services.profile_dialog_service import continue_dialog, finish_dialog, start_dialog
from app.services.profile_service import profile_to_dict


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
def dialog_save(payload: DialogSavePayload, db: Session = Depends(get_db)):
    """将对话完成的画像保存到数据库。"""
    from app.services.profile_dialog_service import get_session

    session = get_session(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if not session.get("completed"):
        raise HTTPException(status_code=400, detail="对话尚未完成，无法保存画像")

    profile_json = _build_profile_json(session)
    extracted = session.get("extracted", {})

    weak_points = extracted.get("weak_points", [])
    if isinstance(weak_points, list):
        weak_points_str = dumps(weak_points)
    else:
        weak_points_str = dumps([weak_points])

    profile = StudentProfile(
        student_name=session["student_name"],
        course_id=session["course_id"],
        current_level=extracted.get("current_level"),
        learning_goal=extracted.get("learning_goal"),
        weak_points=weak_points_str,
        learning_preference=extracted.get("learning_preference"),
        profile_json=dumps(profile_json),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile_to_dict(profile)


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
