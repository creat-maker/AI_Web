from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Course


def list_courses(db: Session) -> list[Course]:
    return db.query(Course).order_by(Course.id.desc()).all()


def get_course(db: Session, course_id: int) -> Course | None:
    return db.query(Course).filter(Course.id == course_id).first()


def create_course(db: Session, data: dict) -> Course:
    course = Course(**data)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, course_id: int, data: dict) -> Course | None:
    course = get_course(db, course_id)
    if not course:
        return None
    for key, value in data.items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: int) -> bool:
    course = get_course(db, course_id)
    if not course:
        return False
    db.delete(course)
    db.commit()
    return True
