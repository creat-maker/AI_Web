from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models import StudentProfile
from app.services.demo_profile_chain import normalize_profile_schema, normalize_user_id
from app.services.json_utils import dumps, loads
from app.services.llm_service import llm_service


def create_profile(db: Session, data: dict) -> StudentProfile:
    generated = llm_service.generate_json("profile", data)
    profile_json = normalize_profile_schema({**generated, **data}, data.get("user_id"))
    profile = StudentProfile(
        student_name=profile_json["student_name"],
        course_id=data["course_id"],
        current_level=profile_json["current_level"],
        learning_goal=profile_json["learning_goal"],
        weak_points=dumps(profile_json["weak_points"]),
        learning_preference=profile_json["learning_style"],
        profile_json=dumps(profile_json),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def list_profiles(db: Session, course_id: int | None = None) -> list[StudentProfile]:
    query = db.query(StudentProfile)
    if course_id:
        query = query.filter(StudentProfile.course_id == course_id)
    return query.order_by(StudentProfile.id.desc()).all()


def _profile_json(profile: StudentProfile) -> dict:
    return loads(profile.profile_json, {})


def list_profiles_by_user_id(db: Session, user_id: str | int, course_id: int | None = None) -> list[StudentProfile]:
    normalized = normalize_user_id(user_id)
    items = list_profiles(db, course_id)
    return [
        item for item in items
        if _profile_json(item).get("user_id") and normalize_user_id(_profile_json(item).get("user_id")) == normalized
    ]


def latest_profile_by_user_id(db: Session, user_id: str | int, course_id: int | None = None) -> StudentProfile | None:
    items = list_profiles_by_user_id(db, user_id, course_id)
    return items[0] if items else None


def profile_to_dict(profile: StudentProfile) -> dict:
    raw_json = loads(profile.profile_json, {})
    normalized = normalize_profile_schema(
        {
            **raw_json,
            "student_name": profile.student_name,
            "course_id": profile.course_id,
            "current_level": profile.current_level,
            "learning_goal": profile.learning_goal,
            "weak_points": loads(profile.weak_points, raw_json.get("weak_points", [])),
            "learning_preference": profile.learning_preference,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else raw_json.get("updated_at"),
        },
        raw_json.get("user_id"),
    )
    return {
        "id": profile.id,
        **normalized,
        "profile_json": normalized,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at or normalized["updated_at"],
    }


def update_profile_by_learning(
    db: Session,
    profile: StudentProfile,
    event_type: str,
    weak_point: str | None = None,
    score: float | None = None,
    question: str | None = None,
    resource_id: str | int | None = None,
) -> dict:
    profile_json = normalize_profile_schema(loads(profile.profile_json, {}), loads(profile.profile_json, {}).get("user_id"))
    before_weak = list(profile_json["weak_points"])
    before_pattern = profile_json["mistake_pattern"]
    changes: list[str] = []

    if score is not None and score < 60 and weak_point and weak_point not in profile_json["weak_points"]:
        profile_json["weak_points"].append(weak_point)
        changes.append(f"测评分数 {score} 低于 60，新增薄弱点：{weak_point}")

    if event_type == "tutor" and question:
        keyword_map = {
            "SQL": "SQL 查询",
            "Python": "Python 函数",
            "RAG": "RAG",
            "接口": "接口基础",
            "部署": "系统部署",
        }
        matched = [point for keyword, point in keyword_map.items() if keyword.lower() in question.lower()]
        for point in matched:
            if point not in profile_json["weak_points"]:
                profile_json["weak_points"].append(point)
                changes.append(f"问答问题命中关键词，新增薄弱点：{point}")
        if matched:
            addition = "问答暴露出" + "、".join(matched) + "相关理解不稳"
            if addition not in profile_json["mistake_pattern"]:
                profile_json["mistake_pattern"] = f"{profile_json['mistake_pattern']}；{addition}"
                changes.append(addition)

    if not changes:
        changes.append("记录学习事件，画像字段暂无明显变化")

    profile_json["updated_at"] = datetime.utcnow().isoformat()
    profile_json["change_log"] = [
        *profile_json.get("change_log", []),
        {
            "time": profile_json["updated_at"],
            "event_type": event_type,
            "weak_point": weak_point,
            "score": score,
            "question": question,
            "resource_id": resource_id,
            "changes": changes,
            "before": {"weak_points": before_weak, "mistake_pattern": before_pattern},
            "after": {"weak_points": profile_json["weak_points"], "mistake_pattern": profile_json["mistake_pattern"]},
        },
    ]
    profile.weak_points = dumps(profile_json["weak_points"])
    profile.learning_preference = profile_json["learning_style"]
    profile.current_level = profile_json["current_level"]
    profile.learning_goal = profile_json["learning_goal"]
    profile.profile_json = dumps(profile_json)
    db.commit()
    db.refresh(profile)
    return profile_to_dict(profile)
