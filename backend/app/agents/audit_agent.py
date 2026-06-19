from __future__ import annotations

from app.agents.state import AgentState
from app.services.llm_service import llm_service


def audit_agent(state: AgentState) -> AgentState:
    audit = llm_service.generate_json(
        "audit",
        {
            "student_profile": state.get("student_profile", {}),
            "learning_path": state.get("learning_path", {}),
            "resource_plan": state.get("resource_plan", {}),
            "generated_resources": state.get("generated_resources", []),
            "tutor_answer": state.get("tutor_answer", {}),
            "retrieved_context": state.get("retrieved_context", []),
            "knowledge_evidence": state.get("knowledge_evidence", {}),
            "evaluation_result": state.get("evaluation_result", {}),
        },
    )
    return {
        **state,
        "audit_result": audit if isinstance(audit, dict) else {"items": audit},
        "messages": [*state.get("messages", []), "AuditAgent 完成引用、幻觉风险和内容安全审核"],
    }
