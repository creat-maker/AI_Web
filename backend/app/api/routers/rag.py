from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.business_event_service import record_event
from app.services.lightweight_rag_service import ask_rag


router = APIRouter(prefix="/rag", tags=["rag"])


class RagAskPayload(BaseModel):
    question: str
    courseId: str | int | None = "python-programming"
    studentId: str | int | None = "demo-student-zhangsan"


@router.post("/ask")
def ask(payload: RagAskPayload, db: Session = Depends(get_db)):
    result = ask_rag(payload.question, payload.courseId, payload.studentId)
    record_event(
        db,
        event_type="rag_answered_with_citation",
        title="RAG 引用问答已完成",
        description=f"问题“{payload.question[:40]}”已完成轻量检索并返回 {len(result['citations'])} 条引用。",
        actor_role="student",
        actor_name="张三",
        target_type="rag_answer",
        target_id=payload.studentId,
        related_student="张三",
        related_course="Python 程序设计",
        metadata={
            "confidence": result["confidence"],
            "citation_count": len(result["citations"]),
            "related_knowledge_points": result["relatedKnowledgePoints"],
        },
    )
    return result
