from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course
from app.services.business_event_service import record_event
from app.services.demo_learning_service import get_demo_student
from app.services.lightweight_rag_service import ask_rag


router = APIRouter(prefix="/rag", tags=["rag"])


class RagAskPayload(BaseModel):
    question: str
    courseId: str | int | None = "python-programming"
    studentId: str | int | None = "demo-basic"


def _resolve_course_id(db: Session, course_id: str | int | None) -> int | None:
    try:
        value = int(str(course_id))
    except (TypeError, ValueError):
        value = 0
    if value > 0 and db.query(Course).filter(Course.id == value).first():
        return value

    normalized = str(course_id or "").strip().lower().replace("_", "-")
    if normalized in {"python-programming", "python", "python程序设计", "python-程序设计"}:
        course = db.query(Course).filter(Course.title.like("%Python%")).order_by(Course.id.asc()).first()
        return course.id if course else None
    return None


@router.post("/ask")
def ask(payload: RagAskPayload, db: Session = Depends(get_db)):
    resolved_course_id = _resolve_course_id(db, payload.courseId)
    result = ask_rag(payload.question, resolved_course_id or payload.courseId, payload.studentId)
    result["requestedCourseId"] = payload.courseId
    result["resolvedCourseId"] = resolved_course_id
    student = get_demo_student(payload.studentId)
    record_event(
        db,
        event_type="rag_answered_with_citation",
        title="RAG 引用问答已完成",
        description=f"问题「{payload.question[:40]}」已完成课程资料检索，并返回 {len(result['citations'])} 条引用。",
        actor_role="student",
        actor_name=student["student_name"],
        target_type="rag_answer",
        target_id=payload.studentId,
        related_student=student["student_name"],
        related_course=student["course_name"],
        metadata={
            "confidence": result["confidence"],
            "low_evidence_risk": result["lowEvidenceRisk"],
            "citation_count": len(result["citations"]),
            "related_knowledge_points": result["relatedKnowledgePoints"],
            "profile_type": student["profile_type"],
            "next_step": result["nextStep"],
            "retrieval_mode": result["retrievalMode"],
            "fallback_used": result["fallbackUsed"],
        },
    )
    return result
