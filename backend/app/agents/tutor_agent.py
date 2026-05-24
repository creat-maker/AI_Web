from __future__ import annotations

from app.agents.state import AgentState
from app.rag.retriever import retrieve_course_context
from app.services.llm_service import llm_service


def tutor_agent(state: AgentState) -> AgentState:
    question = state.get("question") or state.get("learning_goal") or "本课程如何学习？"
    contexts = retrieve_course_context(state["course_id"], question, top_k=3)
    answer = llm_service.generate_json("tutor", {"question": question, "contexts": contexts})
    return {
        **state,
        "retrieved_context": contexts,
        "tutor_answer": answer,
        "messages": [*state.get("messages", []), "TutorAgent 基于 RAG 生成答疑"],
    }
