from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.routers.auth import get_authenticated_user
from app.db.session import get_db
from app.models import Course, StudentProfile
from app.services.business_event_service import record_event
from app.services.demo_profile_chain import get_demo_users
from app.services.dkvmn_tracker import dkvmn_tracker
from app.services.json_utils import dumps, loads
from app.services.profile_service import (
    create_profile,
    latest_profile_by_user_id,
    list_profiles,
    list_profiles_by_user_id,
    profile_to_dict,
)


router = APIRouter(prefix="/profiles", tags=["profiles"])

PROFILE_NOT_FOUND = "学生画像不存在或不可访问"
STAFF_ROLES = {"teacher", "admin"}

OWNER_ALIASES = {
    "1": "student_001",
    "student_001": "student_001",
    "student-li-ming": "student_001",
    "demo-basic": "student_001",
    "demo-student-liming": "student_001",
    "李明": "student_001",
    "2": "demo_student_chenhao",
    "demo-advanced": "demo_student_chenhao",
    "demo_student_chenhao": "demo_student_chenhao",
    "陈浩": "demo_student_chenhao",
    "3": "demo_student_wangyue",
    "demo-exam": "demo_student_wangyue",
    "demo_student_wangyue": "demo_student_wangyue",
    "王悦": "demo_student_wangyue",
    "demo_student_zhangsan": "demo_student_zhangsan",
    "张三": "demo_student_zhangsan",
    "demo_student_lisi": "demo_student_lisi",
    "李四": "demo_student_lisi",
    "demo_student_wangwu": "demo_student_wangwu",
    "王五": "demo_student_wangwu",
}

OWNER_NAMES = {
    "student_001": "李明",
    "demo_student_chenhao": "陈浩",
    "demo_student_wangyue": "王悦",
    "demo_student_zhangsan": "张三",
    "demo_student_lisi": "李四",
    "demo_student_wangwu": "王五",
}

OWNER_DEMO_KEYS = {
    "student_001": "demo-basic",
    "demo_student_chenhao": "demo-advanced",
    "demo_student_wangyue": "demo-exam",
    "demo_student_zhangsan": "demo-zhangsan",
    "demo_student_lisi": "demo-lisi",
    "demo_student_wangwu": "demo-wangwu",
}


class ProfilePayload(BaseModel):
    course_id: int
    student_name: str
    user_id: str | None = None
    current_level: str | None = None
    learning_goal: str | None = None
    weak_points: list[str] = Field(default_factory=list)
    learning_preference: str | None = None


class ProfileUpdatePayload(BaseModel):
    dimension_scores: dict | None = None
    evidence_items: list[dict] | None = None
    cognitive_state: dict | None = None
    risk_level: str | None = None
    learning_goal: str | None = None
    weak_points: list[str] | None = None


def _role(current_user: dict[str, Any]) -> str:
    return str(current_user.get("role") or "")


def _principal_id(current_user: dict[str, Any]) -> str:
    principal_id = str(current_user.get("user_id") or "").strip()
    if not principal_id:
        raise HTTPException(status_code=401, detail="登录凭证缺少用户主体")
    return principal_id


def _require_staff(current_user: dict[str, Any]) -> None:
    if _role(current_user) not in STAFF_ROLES:
        raise HTTPException(status_code=403, detail="当前角色无权访问画像集合")


def _resolve_owner(value: str | None, student_name: str | None = None) -> str:
    candidate = str(value or "").strip()
    if candidate in OWNER_ALIASES:
        return OWNER_ALIASES[candidate]
    name = str(student_name or "").strip()
    if name in OWNER_ALIASES:
        return OWNER_ALIASES[name]
    if candidate.startswith(("student_", "demo_student_")):
        return candidate
    raise HTTPException(status_code=422, detail="无法确定目标画像所有者")


def _get_authorized_profile(
    db: Session,
    profile_id: int,
    current_user: dict[str, Any],
) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=PROFILE_NOT_FOUND)
    role = _role(current_user)
    if role == "student" and profile.owner_user_id != _principal_id(current_user):
        raise HTTPException(status_code=404, detail=PROFILE_NOT_FOUND)
    if role not in {"student", *STAFF_ROLES}:
        raise HTTPException(status_code=403, detail="当前角色无权访问学生画像")
    return profile


def _student_profile_response(profile: StudentProfile) -> dict[str, Any]:
    data = profile_to_dict(profile)
    allowed_fields = {
        "id",
        "student_name",
        "course_id",
        "current_level",
        "knowledge_level",
        "learning_goal",
        "weak_points",
        "learning_preference",
        "learning_style",
        "risk_level",
        "recommended_strategy",
        "dimension_scores",
        "evidence_items",
        "created_at",
        "updated_at",
    }
    return {key: value for key, value in data.items() if key in allowed_fields}


def _response_for_role(profile: StudentProfile, current_user: dict[str, Any]) -> dict[str, Any]:
    if _role(current_user) == "student":
        return _student_profile_response(profile)
    return profile_to_dict(profile)


def _profile_create_data(payload: ProfilePayload, current_user: dict[str, Any]) -> dict[str, Any]:
    data = payload.model_dump()
    role = _role(current_user)
    if role == "student":
        owner_user_id = _principal_id(current_user)
        student_name = str(current_user.get("name") or current_user.get("display_name") or "").strip()
        if not student_name:
            raise HTTPException(status_code=422, detail="登录主体缺少学生姓名")
    elif role in STAFF_ROLES:
        owner_user_id = _resolve_owner(payload.user_id, payload.student_name)
        student_name = OWNER_NAMES.get(owner_user_id, payload.student_name.strip())
    else:
        raise HTTPException(status_code=403, detail="当前角色无权创建学生画像")

    data.update(
        {
            "owner_user_id": owner_user_id,
            "demo_profile_key": OWNER_DEMO_KEYS.get(owner_user_id, owner_user_id),
            "user_id": owner_user_id,
            "student_name": student_name,
        }
    )
    return data


def _create_item(
    payload: ProfilePayload,
    db: Session,
    current_user: dict[str, Any],
) -> dict[str, Any]:
    data = _profile_create_data(payload, current_user)
    try:
        profile = create_profile(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    course = db.query(Course).filter(Course.id == profile.course_id).first()
    record_event(
        db,
        event_type="profile_generated",
        title="学生画像已生成",
        description=f"{profile.student_name} 的学习画像已生成。",
        actor_role=_role(current_user),
        actor_name=str(current_user.get("name") or ""),
        target_type="student_profile",
        target_id=profile.id,
        related_student=profile.student_name,
        related_course=course.title if course else "",
        metadata={
            "course_id": profile.course_id,
            "weak_point_count": len(payload.weak_points),
        },
    )
    return _response_for_role(profile, current_user)


@router.get("")
def list_items(
    course_id: int | None = None,
    user_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_authenticated_user),
):
    _require_staff(current_user)
    if user_id:
        owner_user_id = _resolve_owner(user_id)
        rows = list_profiles_by_user_id(db, owner_user_id, course_id)
    else:
        rows = list_profiles(db, course_id)
    return [profile_to_dict(item) for item in rows]


@router.get("/demo-users")
def demo_users(current_user: dict[str, Any] = Depends(get_authenticated_user)):
    _require_staff(current_user)
    return {"items": get_demo_users()}


@router.get("/me")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_authenticated_user),
):
    if _role(current_user) != "student":
        raise HTTPException(status_code=403, detail="仅学生可读取本人画像")
    profile = latest_profile_by_user_id(db, _principal_id(current_user))
    if not profile:
        raise HTTPException(status_code=404, detail=PROFILE_NOT_FOUND)
    return _student_profile_response(profile)


@router.post("")
def create_item(
    payload: ProfilePayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_authenticated_user),
):
    return _create_item(payload, db, current_user)


@router.post("/generate")
def generate_profile(
    payload: ProfilePayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_authenticated_user),
):
    return _create_item(payload, db, current_user)


@router.get("/{profile_id}")
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_authenticated_user),
):
    profile = _get_authorized_profile(db, profile_id, current_user)
    return _response_for_role(profile, current_user)


@router.put("/{profile_id}/update")
def update_profile(
    profile_id: int,
    payload: ProfileUpdatePayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_authenticated_user),
):
    profile = _get_authorized_profile(db, profile_id, current_user)
    if _role(current_user) == "student":
        raise HTTPException(status_code=403, detail="学生无权修改画像高级字段")

    raw = loads(profile.profile_json, {})
    if payload.dimension_scores is not None:
        profile.dimension_scores = dumps(payload.dimension_scores)
        raw["dimension_scores"] = payload.dimension_scores
    if payload.evidence_items is not None:
        existing = loads(profile.evidence_items, [])
        profile.evidence_items = dumps(
            [*(existing if isinstance(existing, list) else []), *payload.evidence_items][-30:]
        )
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
    history.append(
        {
            "time": __import__("datetime").datetime.utcnow().isoformat(),
            "trigger": "manual_profile_update",
            "fields": list(payload.model_dump(exclude_none=True).keys()),
        }
    )
    profile.profile_history = dumps(history[-30:])
    raw["profile_history"] = history[-30:]
    raw["user_id"] = profile.owner_user_id
    raw["student_name"] = profile.student_name
    raw["display_name"] = profile.student_name
    profile.profile_json = dumps(raw)
    db.commit()
    db.refresh(profile)
    return profile_to_dict(profile)


@router.get("/{profile_id}/visualization")
def profile_visualization(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_authenticated_user),
):
    profile = _get_authorized_profile(db, profile_id, current_user)
    state = dkvmn_tracker.state_from_profile(profile)
    dimensions = loads(profile.dimension_scores, None) or dkvmn_tracker.map_to_profile_dimensions(state)
    history = loads(profile.profile_history, [])
    if not isinstance(history, list):
        history = []
    radar = [
        {
            "dimension": name,
            "score": value.get("score", 0),
            "label": value.get("label", ""),
            "confidence": value.get("confidence", 0.6),
        }
        for name, value in dimensions.items()
    ]
    return {
        "profile_id": profile.id,
        "student_name": profile.student_name,
        "risk_level": profile.risk_level or "medium",
        "radar": radar,
        "trend": history[-8:]
        or [
            {"time": "初始画像", "mastery_average": 0.52, "trigger": "profile_dialog"},
            {
                "time": "测验后",
                "mastery_average": dkvmn_tracker.get_mastery_distribution(profile.id, state)[
                    "average_mastery"
                ],
                "trigger": "quiz_submit",
            },
        ],
        "dimension_scores": dimensions,
        "cognitive_state": dkvmn_tracker.get_cognitive_state(profile.id, state),
        "evidence_items": loads(profile.evidence_items, []),
    }
