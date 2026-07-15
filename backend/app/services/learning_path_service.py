from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Course, LearningPath, StudentProfile
from app.services.dkvmn_tracker import dkvmn_tracker
from app.services.json_utils import dumps, loads
from app.services.llm_service import llm_service


def create_learning_path(db: Session, profile: StudentProfile, course: Course) -> LearningPath:
    path_json = llm_service.generate_json(
        "learning_path",
        {"profile": loads(profile.profile_json, {}), "course_title": course.title},
    )
    cognitive_state = dkvmn_tracker.state_from_profile(profile)
    weak_concepts = dkvmn_tracker.get_weak_concepts(profile.id, cognitive_state)
    strong_concepts = dkvmn_tracker.get_strong_concepts(profile.id, cognitive_state)
    stages = path_json.setdefault("stages", [])
    for item in weak_concepts:
        stages.insert(
            0,
            {
                "name": f"{item['name']}补弱任务",
                "target": f"掌握度 {round(item['mastery'] * 100)}%，先完成讲义、动画和 3 道专项练习。",
                "status": "todo",
                "reason": "DKVMN 掌握度低于 0.5 或连续错误触发。",
            },
        )
    if strong_concepts:
        stages.append(
            {
                "name": "进阶挑战",
                "target": f"基于优势知识点 {strong_concepts[0]['name']} 完成综合小项目。",
                "status": "todo",
                "reason": "DKVMN 掌握度高于 0.9 或连续正确触发。",
            }
        )
    item = LearningPath(
        student_profile_id=profile.id,
        course_id=course.id,
        path_json=dumps(path_json),
        current_difficulty="基础补弱" if weak_concepts else "巩固练习",
        inserted_tasks=dumps([stage.get("name") for stage in stages if "补弱" in str(stage.get("name"))]),
        teacher_arbitration_required=profile.risk_level == "high",
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

    state = dkvmn_tracker.state_from_profile(profile)
    weak_concepts = dkvmn_tracker.get_weak_concepts(profile.id, state)
    strong_concepts = dkvmn_tracker.get_strong_concepts(profile.id, state)
    old_level = path.current_difficulty or "巩固练习"
    inserted_tasks = [f"{point}专项练习" for point in (detected_new or [])]
    for item in weak_concepts:
        task_name = f"{item['name']}补弱任务"
        if task_name not in inserted_tasks:
            inserted_tasks.append(task_name)
        new_path_json.setdefault("stages", []).insert(
            0,
            {
                "name": task_name,
                "target": f"掌握度 {round(item['mastery'] * 100)}%，插入分步讲义、HTML 动画和专项练习。",
                "status": "todo",
                "reason": "DKVMN 掌握度低于阈值。",
            },
        )
    if strong_concepts:
        new_path_json.setdefault("stages", []).append(
            {
                "name": "综合挑战项目",
                "target": f"使用 {strong_concepts[0]['name']} 完成循环结构小项目。",
                "status": "todo",
                "reason": "DKVMN 识别为优势知识点，路径难度上调。",
            }
        )
    if weak_concepts:
        new_level = "基础补弱"
    elif strong_concepts:
        new_level = "进阶挑战"
    else:
        new_level = "巩固练习"

    # 构建调整记录
    adjustment_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "time": datetime.utcnow().isoformat(),
        "trigger": trigger,
        "old_level": old_level,
        "new_level": new_level,
        "reason": reason or f"薄弱点变化：新增 {detected_new or []}，已掌握 {resolved or []}",
        "inserted_tasks": inserted_tasks,
        "related_concepts": detected_new or [item["name"] for item in weak_concepts],
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
    path.current_difficulty = new_level
    path.inserted_tasks = dumps(inserted_tasks)
    path.teacher_arbitration_required = bool(profile.risk_level == "high" or len(weak_concepts) >= 3)

    db.commit()
    db.refresh(path)
    return path


def list_learning_paths(db: Session, course_id: int | None = None) -> list[LearningPath]:
    query = db.query(LearningPath)
    if course_id:
        query = query.filter(LearningPath.course_id == course_id)
    return query.order_by(LearningPath.id.desc()).all()
