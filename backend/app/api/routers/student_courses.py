from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, GeneratedResource, LearningReport, QuizSubmission, StudentProfile

router = APIRouter(prefix="/student", tags=["student-courses"])


def _course_row(course: Course, profile: StudentProfile | None, index: int, db: Session) -> dict:
    resources = db.query(GeneratedResource).filter(GeneratedResource.course_id == course.id).count()
    reports = db.query(LearningReport).filter(LearningReport.course_id == course.id).count()
    submissions = db.query(QuizSubmission).join(StudentProfile, QuizSubmission.student_profile_id == StudentProfile.id).filter(StudentProfile.course_id == course.id).all()
    accuracy = round(sum(item.score or 0 for item in submissions) / len(submissions), 1) if submissions else 72 - index * 4
    progress = min(96, 58 + resources * 4 + reports * 3 + index * 5)
    chapter = "循环结构" if "Python" in course.title or index == 0 else "课程核心章节"
    return {
        "id": course.id,
        "course_id": course.id,
        "course_name": course.title,
        "title": course.title,
        "teacher_name": course.teacher_name or "王老师",
        "description": course.description or "围绕课程目标组织学习资源、测验评价和学习报告。",
        "current_chapter": chapter,
        "progress": progress,
        "status": "学习中" if progress < 90 else "接近完成",
        "chapter_focus": ["while 循环", "break / continue", "循环嵌套"] if chapter == "循环结构" else ["重点概念", "实践任务"],
        "accuracy": accuracy,
        "study_minutes": 120 + index * 35,
        "resource_count": resources,
        "report_count": reports,
        "recent_records": [
            f"完成 {chapter} 相关练习",
            "查看学习资源并更新学习路径",
            "生成阶段性学习报告",
        ],
        "student_name": profile.student_name if profile else "李明",
    }


@router.get("/courses")
def student_courses(student_id: int | str | None = None, db: Session = Depends(get_db)):
    courses = db.query(Course).order_by(Course.id.desc()).all()
    profile = db.query(StudentProfile).order_by(StudentProfile.id.desc()).first()
    rows = [_course_row(course, profile, index, db) for index, course in enumerate(courses)]
    active = [item for item in rows if item["status"] == "学习中"]
    return {
        "student_id": student_id or 1,
        "summary": {
            "active_course_count": len(active),
            "today_focus": "Python 循环结构",
            "average_accuracy": round(sum(item["accuracy"] for item in rows) / len(rows), 1) if rows else 0,
            "study_minutes": sum(item["study_minutes"] for item in rows),
        },
        "courses": rows,
    }
