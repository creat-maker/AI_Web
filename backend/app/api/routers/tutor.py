from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter

from app.rag.retriever import retrieve_course_context
from app.services.llm_service import llm_service


router = APIRouter(prefix="/tutor", tags=["tutor"])


class TutorPayload(BaseModel):
    course_id: int
    question: str
    top_k: int = 3


@router.post("/ask")
def ask(payload: TutorPayload):
    contexts = retrieve_course_context(payload.course_id, payload.question, payload.top_k)
    answer = llm_service.generate_json("tutor", {"question": payload.question, "contexts": contexts})
    return {"answer": answer, "retrieved_context": contexts, "mode": llm_service.runtime_mode}
