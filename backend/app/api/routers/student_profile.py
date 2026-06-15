from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.deps import get_demo_user_id
from app.db.session import get_db
from app.services.demo_profile_chain import get_demo_student, normalize_profile_schema
from app.services.profile_service import latest_profile_by_user_id, profile_to_dict


router = APIRouter(prefix="/student-profile", tags=["student-profile"])


class ProfileRefreshPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    user_id: str | None = None
    dialog: str | None = None
    weak_points: list[str] | None = None


def _profile_payload(user_id: str | int | None = None, stored: dict[str, Any] | None = None) -> dict[str, Any]:
    profile = normalize_profile_schema(stored, user_id)
    dimensions = [
        {"name": "知识基础", "value": profile["current_level"]},
        {"name": "认知风格", "value": profile["learning_style"]},
        {"name": "学习目标", "value": profile["learning_goal"]},
        {"name": "学习进度", "value": f"{profile.get('progress', 42)}%"},
        {"name": "易错偏好", "value": profile["mistake_pattern"]},
        {"name": "资源偏好", "value": profile["resource_preference"]},
        {"name": "学习能力", "value": "代码实操需要脚手架提示，能在示例带领下完成迁移。"},
        {"name": "学习状态", "value": profile["risk_level"]},
    ]
    return {
        "studentId": profile["user_id"],
        "studentName": profile["student_name"],
        "courseName": profile["course_name"],
        "chapter": "循环结构",
        "summary": f"{profile['student_name']}在循环结构上还需要加强，系统已生成个性化学习建议。",
        "profileType": profile["profile_type"],
        "riskLevel": profile["risk_level"],
        "learningStatus": profile["risk_level"],
        "riskReasons": ["while 循环死循环问题错误率较高", "循环嵌套变量变化跟踪不稳定", "break / continue 使用场景混淆"],
        "weakReasons": ["while 循环条件更新还不稳定", "循环嵌套变量变化跟踪不完整", "break / continue 使用场景容易混淆"],
        "weakKnowledgePoints": profile["weak_points"],
        "resourcePreference": profile["resource_preference"],
        "teacherIntervention": "建议推送代码案例和图解资源，课堂用变量变化表进行 1 对 1 点拨。",
        "sourceDescription": "自然语言对话 + 学习历史 + 测验结果 + AI 问答记录",
        "dimensions": dimensions,
        "mode": "profile-refresh",
    }


@router.get("/demo")
def demo_profile(user_id: str | None = None, db: Session = Depends(get_db), current_user_id: str = Depends(get_demo_user_id)):
    active_user_id = user_id or current_user_id
    stored = latest_profile_by_user_id(db, active_user_id)
    return _profile_payload(active_user_id, profile_to_dict(stored) if stored else None)


@router.post("/refresh")
def refresh_profile(payload: ProfileRefreshPayload, current_user_id: str = Depends(get_demo_user_id)):
    active_user_id = payload.user_id or current_user_id
    student = get_demo_student(active_user_id)
    profile = _profile_payload(active_user_id)
    if payload.weak_points:
        profile["weakKnowledgePoints"] = payload.weak_points
    profile["latestQuizSummary"] = {
        "score": 67,
        "accuracy": 67,
        "weakPoints": payload.weak_points or ["while 循环条件更新", "循环嵌套变量变化", "break / continue 区分"],
        "profileUpdateSummary": "已根据最近一次循环结构专项测验更新学习建议。",
    }
    profile["refreshReason"] = "根据最新对话、测验错因和 AI 学伴求助记录完成画像刷新。"
    profile["dialogInput"] = payload.dialog or student.get("dialog_extraction", {}).get("raw_answer")
    return profile
