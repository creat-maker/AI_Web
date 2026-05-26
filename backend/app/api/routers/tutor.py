from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import TutorQuestionLog
from app.rag.retriever import retrieve_course_context
from app.services.json_utils import dumps, loads
from app.services.llm_service import llm_service


router = APIRouter(prefix="/tutor", tags=["tutor"])


class TutorPayload(BaseModel):
    course_id: int
    question: str
    top_k: int = 3


@router.post("/ask")
def ask(payload: TutorPayload, db: Session = Depends(get_db)):
    contexts = retrieve_course_context(payload.course_id, payload.question, payload.top_k)
    answer = llm_service.generate_json("tutor", {"question": payload.question, "contexts": contexts})
    mode = llm_service.runtime_mode
    db.add(
        TutorQuestionLog(
            course_id=payload.course_id,
            question=payload.question,
            answer_json=dumps(answer),
            contexts_json=dumps(contexts),
            mode=mode,
        )
    )
    db.commit()
    return {"answer": answer, "retrieved_context": contexts, "mode": mode}


@router.get("/history")
def history(course_id: int | None = None, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(TutorQuestionLog)
    if course_id:
        query = query.filter(TutorQuestionLog.course_id == course_id)
    items = query.order_by(TutorQuestionLog.created_at.desc()).limit(min(max(limit, 1), 100)).all()
    return [
        {
            "id": item.id,
            "course_id": item.course_id,
            "question": item.question,
            "answer": loads(item.answer_json, {}),
            "retrieved_context": loads(item.contexts_json, []),
            "mode": item.mode,
            "created_at": item.created_at,
        }
        for item in items
    ]
