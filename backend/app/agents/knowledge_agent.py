from __future__ import annotations

from app.agents.state import AgentState
from app.rag.retriever import retrieve_course_context


def _query_from_state(state: AgentState) -> str:
    weak_points = "、".join(state.get("weak_points", [])[:4])
    parts = [
        state.get("question") or "",
        state.get("learning_goal") or "",
        weak_points,
        state.get("course_title") or "",
    ]
    return " ".join(part for part in parts if part).strip() or "课程学习重点"


def _confidence(contexts: list[dict]) -> float:
    if not contexts:
        return 0.0
    values = [float(item.get("confidence", item.get("score", 0)) or 0) for item in contexts]
    return round(sum(values) / max(len(values), 1), 2)


def knowledge_agent(state: AgentState) -> AgentState:
    query = _query_from_state(state)
    contexts = retrieve_course_context(state["course_id"], query, top_k=5)
    evidence_items = [
        {
            "source": item.get("source_file") or f"知识库文档 #{item.get('document_id', '-')}",
            "section": item.get("section_title"),
            "knowledge_point": item.get("knowledge_point"),
            "confidence": item.get("confidence", item.get("score", 0)),
            "citation_id": item.get("citation_id"),
            "reason": item.get("reason"),
        }
        for item in contexts
    ]
    evidence = {
        "query": query,
        "citation_count": len(contexts),
        "confidence": _confidence(contexts),
        "unsupported_answer_risk": not contexts or _confidence(contexts) < 0.25,
        "items": evidence_items,
        "agent": "KnowledgeAgent",
    }
    return {
        **state,
        "knowledge_query": query,
        "retrieved_context": contexts,
        "knowledge_evidence": evidence,
        "messages": [*state.get("messages", []), f"KnowledgeAgent 召回 {len(contexts)} 条课程证据"],
    }
