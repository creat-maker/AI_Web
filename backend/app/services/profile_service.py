from __future__ import annotations

from copy import deepcopy
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
    dimension_scores = loads(getattr(profile, "dimension_scores", None), raw_json.get("dimension_scores", {}))
    evidence_items = loads(getattr(profile, "evidence_items", None), raw_json.get("evidence_items", []))
    cognitive_state = loads(getattr(profile, "cognitive_state", None), raw_json.get("cognitive_state", {}))
    profile_history = loads(getattr(profile, "profile_history", None), raw_json.get("profile_history", []))
    risk_level = getattr(profile, "risk_level", None) or raw_json.get("risk_level") or "medium"
    normalized = normalize_profile_schema(
        {
            **raw_json,
            "student_name": profile.student_name,
            "course_id": profile.course_id,
            "current_level": profile.current_level,
            "learning_goal": profile.learning_goal,
            "weak_points": loads(profile.weak_points, raw_json.get("weak_points", [])),
            "learning_preference": profile.learning_preference,
            "dimension_scores": dimension_scores,
            "evidence_items": evidence_items,
            "cognitive_state": cognitive_state,
            "profile_history": profile_history,
            "risk_level": risk_level,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else raw_json.get("updated_at"),
        },
        raw_json.get("user_id"),
    )
    return {
        "id": profile.id,
        **normalized,
        "dimension_scores": dimension_scores,
        "evidence_items": evidence_items,
        "cognitive_state": cognitive_state,
        "profile_history": profile_history,
        "risk_level": risk_level,
        "profile_json": normalized,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at or normalized["updated_at"],
    }


def merge_profile_evidence(old_evidence: list[dict] | None, new_evidence: list[dict] | None) -> list[dict]:
    merged: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for item in [*(old_evidence or []), *(new_evidence or [])]:
        if not isinstance(item, dict):
            continue
        key = (str(item.get("source_type", "")), str(item.get("description", "")))
        if key in seen:
            continue
        seen.add(key)
        merged.append({**item, "confidence": float(item.get("confidence", 0.7))})
    return merged[-50:]


def calculate_risk_level(dimension_scores: dict, quiz_results: list[dict] | dict | None = None) -> str:
    scores = []
    for value in (dimension_scores or {}).values():
        if isinstance(value, dict):
            scores.append(float(value.get("score", 0)))
        else:
            scores.append(float(value or 0))
    quiz_rows = quiz_results if isinstance(quiz_results, list) else [quiz_results] if quiz_results else []
    quiz_scores = [float(item.get("score", 0)) for item in quiz_rows if isinstance(item, dict)]
    average = sum(scores) / max(len(scores), 1) if scores else 65
    latest_quiz = quiz_scores[-1] if quiz_scores else average
    if average < 55 or latest_quiz < 60:
        return "high"
    if average < 75 or latest_quiz < 75:
        return "medium"
    return "low"


def build_profile_visualization(profile: StudentProfile | dict) -> dict:
    data = profile if isinstance(profile, dict) else profile_to_dict(profile)
    dimensions = data.get("dimension_scores") or {}
    history = data.get("profile_history") or []
    evidence = data.get("evidence_items") or []
    radar = [
        {"dimension": name, "score": value.get("score", value), "label": value.get("label", "") if isinstance(value, dict) else ""}
        for name, value in dimensions.items()
    ]
    if not radar:
        radar = [
            {"dimension": "知识基础", "score": 62, "label": "需补强"},
            {"dimension": "学习节奏", "score": 70, "label": "稳定"},
            {"dimension": "代码实操能力", "score": 58, "label": "需补强"},
        ]
    trend = [
        {
            "time": item.get("time") or item.get("created_at") or "",
            "mastery_average": item.get("mastery_average") or item.get("score") or 0,
            "trigger": item.get("trigger") or item.get("event_type") or "profile_update",
        }
        for item in history[-12:]
        if isinstance(item, dict)
    ]
    return {
        "radar_chart": radar,
        "trend_chart": trend,
        "evidence_chain": evidence[-20:],
        "cognitive_state_description": _cognitive_state_description(data.get("cognitive_state") or {}, data.get("risk_level", "medium")),
        "risk_level": data.get("risk_level", "medium"),
    }


def _cognitive_state_description(cognitive_state: dict, risk_level: str) -> str:
    weak = cognitive_state.get("weak_concepts") or []
    if weak:
        first = weak[0].get("name", weak[0]) if isinstance(weak[0], dict) else weak[0]
        return f"认知追踪显示 {first} 掌握度偏低，当前风险等级为 {risk_level}。"
    return f"认知追踪暂无明显薄弱聚类，当前风险等级为 {risk_level}。"


def append_profile_history(profile: StudentProfile | dict, event: dict) -> list[dict]:
    data = profile if isinstance(profile, dict) else profile_to_dict(profile)
    history = list(data.get("profile_history") or [])
    row = {"time": datetime.utcnow().isoformat(), **(event or {})}
    history.append(row)
    if not isinstance(profile, dict):
        profile.profile_history = dumps(history[-50:])
        raw = loads(profile.profile_json, {})
        raw["profile_history"] = history[-50:]
        profile.profile_json = dumps(raw)
    return history[-50:]


def update_profile_dimensions(
    profile: StudentProfile | dict,
    new_scores: dict,
    evidence_items: list[dict] | None = None,
) -> dict:
    data = profile if isinstance(profile, dict) else profile_to_dict(profile)
    dimensions = deepcopy(data.get("dimension_scores") or {})
    for name, value in (new_scores or {}).items():
        score = float(value.get("score", value)) if isinstance(value, dict) else float(value)
        dimensions[name] = {
            **(dimensions.get(name, {}) if isinstance(dimensions.get(name), dict) else {}),
            "score": round(max(0, min(100, score))),
            "label": "优势" if score >= 82 else "稳定" if score >= 62 else "需补强",
            "updated_at": datetime.utcnow().isoformat(),
        }
    evidence = merge_profile_evidence(data.get("evidence_items") or [], evidence_items or [])
    risk = calculate_risk_level(dimensions)
    history = append_profile_history(
        profile,
        {"trigger": "dimension_update", "changed_dimensions": list((new_scores or {}).keys()), "risk_level": risk},
    )
    if not isinstance(profile, dict):
        profile.dimension_scores = dumps(dimensions)
        profile.evidence_items = dumps(evidence)
        profile.risk_level = risk
        raw = loads(profile.profile_json, {})
        raw.update({"dimension_scores": dimensions, "evidence_items": evidence, "risk_level": risk, "profile_history": history})
        profile.profile_json = dumps(raw)
    return {
        "dimension_scores": dimensions,
        "evidence_items": evidence,
        "risk_level": risk,
        "profile_history": history,
        "visualization": build_profile_visualization({**data, "dimension_scores": dimensions, "evidence_items": evidence, "risk_level": risk, "profile_history": history}),
    }


class ProfileService:
    profile_to_dict = staticmethod(profile_to_dict)
    build_profile_visualization = staticmethod(build_profile_visualization)
    update_profile_dimensions = staticmethod(update_profile_dimensions)
    append_profile_history = staticmethod(append_profile_history)
    calculate_risk_level = staticmethod(calculate_risk_level)
    merge_profile_evidence = staticmethod(merge_profile_evidence)


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
    before_profile = deepcopy(profile_json)
    before_weak = list(profile_json["weak_points"])
    before_pattern = profile_json["mistake_pattern"]
    changes: list[str] = []

    if score is not None and score < 60 and weak_point and weak_point not in profile_json["weak_points"]:
        profile_json["weak_points"].append(weak_point)
        changes.append(f"测评分数 {score} 低于 60，新增薄弱点：{weak_point}")
        profile_json.setdefault("evidence_items", []).append({
            "source_type": "quiz",
            "description": f"模拟测评分数 {score} 低于 60，系统将 {weak_point} 追加为薄弱点。",
            "related_field": "weak_points",
            "confidence": 0.86,
        })

    if event_type == "tutor" and question:
        keyword_map = {
            "SQL": "循环条件判断",
            "Python": "Python 循环结构",
            "RAG": "RAG",
            "接口": "接口基础",
            "部署": "系统部署",
        }
        matched = [point for keyword, point in keyword_map.items() if keyword.lower() in question.lower()]
        for point in matched:
            if point not in profile_json["weak_points"]:
                profile_json["weak_points"].append(point)
                changes.append(f"问答问题命中关键词，新增薄弱点：{point}")
                profile_json.setdefault("evidence_items", []).append({
                    "source_type": "tutor",
                    "description": f"问答问题“{question}”命中关键词，追加 {point} 作为画像证据。",
                    "related_field": "weak_points",
                    "confidence": 0.8,
                })
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
    after_profile = profile_to_dict(profile)
    return {
        **after_profile,
        "before_profile": before_profile,
        "after_profile": after_profile,
        "change_log": after_profile.get("change_log", profile_json["change_log"]),
    }
