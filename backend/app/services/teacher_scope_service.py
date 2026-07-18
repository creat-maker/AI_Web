from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Query, Session

from app.models import AgentRun, Course, StudentProfile
from app.services.json_utils import loads


# Q014 immediate containment only. These server-side mappings bind the current
# demo teacher identity to seeded course titles. They are not a production
# class-roster or organization authorization model.
DEMO_TEACHER_COURSE_TITLES: dict[str, frozenset[str]] = {
    "teacher_001": frozenset({"Python 程序设计", "Python 爬虫基础与实践"}),
    "teacher_002": frozenset({"人工智能导论", "数据结构与算法"}),
}


def principal_id(current_user: dict[str, Any]) -> str:
    return str(current_user.get("user_id") or current_user.get("username") or "").strip()


def principal_name(current_user: dict[str, Any]) -> str:
    return str(current_user.get("name") or current_user.get("display_name") or current_user.get("username") or "").strip()


def get_authorized_course_ids(db: Session, current_user: dict[str, Any]) -> set[int] | None:
    role = str(current_user.get("role") or "guest")
    if role == "admin":
        return None
    if role != "teacher":
        return set()
    titles = DEMO_TEACHER_COURSE_TITLES.get(principal_id(current_user), frozenset())
    if not titles:
        return set()
    return {int(row[0]) for row in db.query(Course.id).filter(Course.title.in_(titles)).all()}


def can_manage_course(db: Session, current_user: dict[str, Any], course: Course) -> bool:
    role = str(current_user.get("role") or "guest")
    if role == "admin":
        return True
    if role != "teacher":
        return False
    course_ids = get_authorized_course_ids(db, current_user) or set()
    if int(course.id) in course_ids:
        return True
    teacher_name = str(course.teacher_name or "").strip()
    return bool(teacher_name and teacher_name == principal_name(current_user))


def get_course_for_write(db: Session, current_user: dict[str, Any], course_id: int) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course or not can_manage_course(db, current_user, course):
        raise HTTPException(status_code=404, detail="课程不存在或不可访问")
    return course


def resolve_course_reference(db: Session, reference: str | int | None) -> Course | None:
    if reference is None or str(reference).strip() == "":
        return None
    raw = str(reference).strip()
    try:
        course = db.query(Course).filter(Course.id == int(raw)).first()
        if course:
            return course
    except (TypeError, ValueError):
        pass
    aliases = {
        "python-programming": "Python 程序设计",
        "demo-course-python": "Python 程序设计",
    }
    title = aliases.get(raw.lower(), raw)
    return db.query(Course).filter(Course.title == title).first()


def get_profile_for_write(
    db: Session,
    current_user: dict[str, Any],
    profile_id: int,
    *,
    course: Course | None = None,
) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="学生对象不存在或不可访问")
    if course is not None and int(profile.course_id) != int(course.id):
        raise HTTPException(status_code=404, detail="学生对象不存在或不可访问")
    role = str(current_user.get("role") or "guest")
    if role == "student":
        if str(profile.owner_user_id or "") != principal_id(current_user):
            raise HTTPException(status_code=404, detail="学生对象不存在或不可访问")
        return profile
    if role == "teacher":
        profile_course = course or db.query(Course).filter(Course.id == profile.course_id).first()
        if not profile_course or not can_manage_course(db, current_user, profile_course):
            raise HTTPException(status_code=404, detail="学生对象不存在或不可访问")
        return profile
    if role == "admin":
        return profile
    raise HTTPException(status_code=403, detail="当前角色无权写入学生对象")


def scope_agent_run_query(query: Query, db: Session, current_user: dict[str, Any]) -> Query:
    role = str(current_user.get("role") or "guest")
    if role == "student":
        owned_profile_ids = db.query(StudentProfile.id).filter(
            StudentProfile.owner_user_id == principal_id(current_user)
        )
        return query.filter(AgentRun.student_profile_id.in_(owned_profile_ids))
    course_ids = get_authorized_course_ids(db, current_user)
    if course_ids is None:
        return query
    if not course_ids:
        return query.filter(AgentRun.id == -1)
    return query.filter(AgentRun.course_id.in_(course_ids))


def can_access_agent_run(db: Session, current_user: dict[str, Any], item: AgentRun) -> bool:
    role = str(current_user.get("role") or "guest")
    if role == "student":
        if not item.student_profile_id:
            return False
        profile = db.query(StudentProfile).filter(StudentProfile.id == item.student_profile_id).first()
        return bool(
            profile
            and int(profile.course_id) == int(item.course_id)
            and str(profile.owner_user_id or "") == principal_id(current_user)
        )
    course_ids = get_authorized_course_ids(db, current_user)
    return course_ids is None or int(item.course_id) in course_ids


def agent_run_student_matches_course(db: Session, item: AgentRun) -> bool:
    if not item.student_profile_id:
        return True
    profile = db.query(StudentProfile).filter(StudentProfile.id == item.student_profile_id).first()
    return bool(profile and int(profile.course_id) == int(item.course_id))


def is_pending_teacher_arbitration(item: AgentRun) -> bool:
    if item.status != "pending_review" or item.current_node != "TeacherArbitration":
        return False
    arbitration = loads(item.teacher_arbitration_result, {})
    if not arbitration:
        arbitration = loads(item.state, {}).get("teacher_arbitration_result") or {}
    return not arbitration or arbitration.get("status") == "pending"
