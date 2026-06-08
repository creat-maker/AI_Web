from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Course, LearningPath, StudentProfile
from app.services.json_utils import dumps, loads
from app.services.llm_service import llm_service


def create_learning_path(db: Session, profile: StudentProfile, course: Course) -> LearningPath:
    path_json = llm_service.generate_json(
        "learning_path",
        {"profile": loads(profile.profile_json, {}), "course_title": course.title},
    )
    item = LearningPath(
        student_profile_id=profile.id,
        course_id=course.id,
        path_json=dumps(path_json),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def adjust_learning_path(
    db: Session,
    path: LearningPath,
    profile: StudentProfile,
    course: Course,
    trigger: str = "quiz_submission",
    detected_new: list[str] | None = None,
    resolved: list[str] | None = None,
    reason: str = "",
) -> LearningPath:
    """根据薄弱点变化重新规划学习路径，保留调整历史。"""
    old_path_json = loads(path.path_json, {})
    old_stages = old_path_json.get("stages", [])

    # 更新 profile 的 weak_points
    profile_json = loads(profile.profile_json, {})
    old_weak = set(profile_json.get("weak_points", []) or [])
    if detected_new:
        old_weak.update(detected_new)
    if resolved:
        old_weak -= set(resolved)
    profile_json["weak_points"] = list(old_weak)
    profile.weak_points = dumps(list(old_weak))
    profile.profile_json = dumps(profile_json)

    # 重新生成路径
    new_path_json = llm_service.generate_json(
        "learning_path",
        {"profile": profile_json, "course_title": course.title},
    )

    # 构建调整记录
    adjustment_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "trigger": trigger,
        "reason": reason or f"薄弱点变化：新增 {detected_new or []}，已掌握 {resolved or []}",
        "old_stages_summary": [s.get("name", "") for s in old_stages],
        "new_stages_summary": [s.get("name", "") for s in new_path_json.get("stages", [])],
        "detected_new_weak_points": detected_new or [],
        "resolved_weak_points": resolved or [],
    }

    # 追加到 adjustment_log
    log = loads(path.adjustment_log, [])
    if not isinstance(log, list):
        log = []
    log.append(adjustment_entry)

    # 更新路径
    path.path_json = dumps(new_path_json)
    path.adjustment_log = dumps(log)

    db.commit()
    db.refresh(path)
    return path


def list_learning_paths(db: Session, course_id: int | None = None) -> list[LearningPath]:
    query = db.query(LearningPath)
    if course_id:
        query = query.filter(LearningPath.course_id == course_id)
    return query.order_by(LearningPath.id.desc()).all()
