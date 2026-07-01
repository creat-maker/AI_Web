from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, StudentProfile
from app.services.business_event_service import record_event
from app.api.deps import get_demo_user_id
from app.services.demo_profile_chain import get_demo_profiles, get_demo_users
from app.services.dkvmn_tracker import dkvmn_tracker
from app.services.json_utils import dumps, loads
from app.services.profile_service import create_profile, list_profiles, list_profiles_by_user_id, profile_to_dict


router = APIRouter(prefix="/profiles", tags=["profiles"])


class ProfilePayload(BaseModel):
    course_id: int
    student_name: str
    user_id: str | None = None
    current_level: str | None = None
    learning_goal: str | None = None
    weak_points: list[str] = []
    learning_preference: str | None = None


class ProfileUpdatePayload(BaseModel):
    dimension_scores: dict | None = None
    evidence_items: list[dict] | None = None
    cognitive_state: dict | None = None
    risk_level: str | None = None
    learning_goal: str | None = None
    weak_points: list[str] | None = None


@router.get("")
def list_items(course_id: int | None = None, user_id: str | None = None, db: Session = Depends(get_db)):
    if user_id:
        rows = [profile_to_dict(item) for item in list_profiles_by_user_id(db, user_id, course_id)]
        return rows or get_demo_profiles(user_id)
    return [profile_to_dict(item) for item in list_profiles(db, course_id)]


@router.get("/demo-users")
def demo_users():
    return {"items": get_demo_users()}


@router.post("")
def create_item(payload: ProfilePayload, db: Session = Depends(get_db), current_user_id: str = Depends(get_demo_user_id)):
    data = payload.model_dump()
    data["user_id"] = data.get("user_id") or current_user_id
    profile = create_profile(db, data)
    course = db.query(Course).filter(Course.id == profile.course_id).first()
    record_event(
        db,
        event_type="profile_generated",
        title="学生画像已生成",
        description=f"{profile.student_name} 的学习画像已生成，包含目标、水平、偏好、薄弱点和学习状态字段。",
        actor_role="student",
        actor_name=profile.student_name,
        target_type="student_profile",
        target_id=profile.id,
        related_student=profile.student_name,
        related_course=course.title if course else "",
        metadata={
            "learning_goal": profile.learning_goal,
            "current_level": profile.current_level,
            "learning_preference": profile.learning_preference,
            "resource_preference": "知识讲义、分层练习题、代码示例",
            "weak_points": payload.weak_points,
            "risk_level": "需关注" if payload.weak_points else "稳定",
            "course_id": profile.course_id,
        },
    )
    return profile_to_dict(profile)


@router.post("/generate")
def generate_profile(payload: ProfilePayload, db: Session = Depends(get_db), current_user_id: str = Depends(get_demo_user_id)):
    return create_item(payload, db, current_user_id)


@router.get("/{profile_id}")
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="学生画像不存在")
    return profile_to_dict(profile)


@router.put("/{profile_id}/update")
def update_profile(profile_id: int, payload: ProfileUpdatePayload, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="学生画像不存在")
    raw = loads(profile.profile_json, {})
    if payload.dimension_scores is not None:
        profile.dimension_scores = dumps(payload.dimension_scores)
        raw["dimension_scores"] = payload.dimension_scores
    if payload.evidence_items is not None:
        existing = loads(profile.evidence_items, [])
        profile.evidence_items = dumps([*(existing if isinstance(existing, list) else []), *payload.evidence_items][-30:])
        raw["evidence_items"] = loads(profile.evidence_items, [])
    if payload.cognitive_state is not None:
        profile.cognitive_state = dumps(payload.cognitive_state)
        raw["cognitive_state"] = payload.cognitive_state
    if payload.risk_level:
        profile.risk_level = payload.risk_level
        raw["risk_level"] = payload.risk_level
    if payload.learning_goal:
        profile.learning_goal = payload.learning_goal
        raw["learning_goal"] = payload.learning_goal
    if payload.weak_points is not None:
        profile.weak_points = dumps(payload.weak_points)
        raw["weak_points"] = payload.weak_points
    history = loads(profile.profile_history, [])
    if not isinstance(history, list):
        history = []
    history.append({"time": __import__("datetime").datetime.utcnow().isoformat(), "trigger": "manual_profile_update", "fields": list(payload.model_dump(exclude_none=True).keys())})
    profile.profile_history = dumps(history[-30:])
    raw["profile_history"] = history[-30:]
    profile.profile_json = dumps(raw)
    db.commit()
    db.refresh(profile)
    return profile_to_dict(profile)


@router.get("/{profile_id}/visualization")
def profile_visualization(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="学生画像不存在")
    state = dkvmn_tracker.state_from_profile(profile)
    dimensions = loads(profile.dimension_scores, None) or dkvmn_tracker.map_to_profile_dimensions(state)
    history = loads(profile.profile_history, [])
    if not isinstance(history, list):
        history = []
    radar = [
        {"dimension": name, "score": value.get("score", 0), "label": value.get("label", ""), "confidence": value.get("confidence", 0.6)}
        for name, value in dimensions.items()
    ]
    return {
        "profile_id": profile.id,
        "student_name": profile.student_name,
        "risk_level": profile.risk_level or "medium",
        "radar": radar,
        "trend": history[-8:] or [
            {"time": "初始画像", "mastery_average": 0.52, "trigger": "profile_dialog"},
            {"time": "测验后", "mastery_average": dkvmn_tracker.get_mastery_distribution(profile.id, state)["average_mastery"], "trigger": "quiz_submit"},
        ],
        "dimension_scores": dimensions,
        "cognitive_state": dkvmn_tracker.get_cognitive_state(profile.id, state),
        "evidence_items": loads(profile.evidence_items, []) or [
            {"source_type": "demo", "description": "本地轻量能力根据李明画像、测验和资源偏好生成解释证据。", "confidence": 0.72}
        ],
        "explainability": {
            "基础薄弱判断": "DKVMN 中 while 循环、break/continue、循环嵌套掌握度偏低，且画像对话中提到代码输出判断困难。",
            "代码实操推荐": "学习偏好和资源评分显示学生更愿意通过代码案例、小项目和动画理解循环结构。",
        },
    }
