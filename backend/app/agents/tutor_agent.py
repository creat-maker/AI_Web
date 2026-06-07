from __future__ import annotations

from app.agents.state import AgentState
from app.rag.retriever import retrieve_course_context
from app.services.llm_service import llm_service


def tutor_agent(state: AgentState) -> AgentState:
    question = state.get("question") or state.get("learning_goal") or "本课程如何学习？"
    contexts = retrieve_course_context(state["course_id"], question, top_k=3)

    # 计算 confidence 统计
    scores = [float(item.get("score") or 0) for item in contexts]
    avg_score = sum(scores) / max(len(scores), 1) if scores else 0
    max_score = max(scores) if scores else 0
    if avg_score >= 0.7:
        confidence_level = "high"
    elif avg_score >= 0.4:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    # 每个 context 增加 confidence
    enriched_contexts = [
        {**item, "confidence": round(float(item.get("score") or 0.5), 4)} for item in contexts
    ]

    answer = llm_service.generate_json("tutor", {"question": question, "contexts": enriched_contexts})

    # 合并 LLM 返回的 confidence（如有）
    if isinstance(answer, dict):
        answer.setdefault("confidence", round(avg_score, 4))
        answer.setdefault("confidence_level", confidence_level)
        if "confidence_breakdown" not in answer:
            answer["confidence_breakdown"] = {
                "avg": round(avg_score, 4),
                "max": round(max_score, 4),
                "min": round(min(scores) if scores else 0, 4),
                "count": len(scores),
            }

    return {
        **state,
        "retrieved_context": enriched_contexts,
        "tutor_answer": answer,
        "confidence": round(avg_score, 4),
        "confidence_level": confidence_level,
        "messages": [*state.get("messages", []), f"TutorAgent 基于 RAG 生成答疑 (confidence: {confidence_level})"],
    }
