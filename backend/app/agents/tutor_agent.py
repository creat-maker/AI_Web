from __future__ import annotations

from typing import Any

from app.agents.state import AgentState
from app.rag.retriever import retrieve_course_context
from app.services.llm_service import llm_service


def _context_key(item: dict[str, Any]) -> str:
    return str(
        item.get("citation_id")
        or f"{item.get('document_id', '')}:{item.get('chunk_index', '')}:{item.get('source_file', '')}"
    )


def _merge_contexts(*groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    merged: list[dict[str, Any]] = []
    for group in groups:
        for item in group:
            key = _context_key(item)
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    return merged


def _confidence(contexts: list[dict[str, Any]]) -> float:
    if not contexts:
        return 0.0
    values = [float(item.get("confidence", item.get("score", 0)) or 0) for item in contexts]
    return round(sum(values) / max(len(values), 1), 2)


def _evidence_items(contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
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


def tutor_agent(state: AgentState) -> AgentState:
    question = state.get("question") or state.get("learning_goal") or "本课程如何学习？"
    existing_contexts = state.get("retrieved_context", []) or []
    answer_contexts = retrieve_course_context(state["course_id"], question, top_k=3)
    contexts = _merge_contexts(existing_contexts, answer_contexts)
    answer = llm_service.generate_json("tutor", {"question": question, "contexts": contexts})

    evidence = dict(state.get("knowledge_evidence", {}) or {})
    evidence.update(
        {
            "query": evidence.get("query") or question,
            "citation_count": len(contexts),
            "confidence": _confidence(contexts),
            "unsupported_answer_risk": not contexts or _confidence(contexts) < 0.25,
            "items": _evidence_items(contexts),
            "agent": "KnowledgeAgent + TutorAgent",
        }
    )
    return {
        **state,
        "retrieved_context": contexts,
        "knowledge_evidence": evidence,
        "tutor_answer": answer,
        "messages": [*state.get("messages", []), f"TutorAgent 基于 {len(contexts)} 条 RAG 证据生成答疑"],
    }
