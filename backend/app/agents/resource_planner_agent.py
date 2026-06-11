from __future__ import annotations

from app.agents.state import AgentState
from app.services.llm_service import llm_service


def resource_planner_agent(state: AgentState) -> AgentState:
    plan = llm_service.generate_json(
        "resource_plan",
        {
            "profile": state.get("student_profile", {}),
            "learning_path": state.get("learning_path", {}),
            "contexts": state.get("retrieved_context", []),
            "knowledge_evidence": state.get("knowledge_evidence", {}),
            "course_title": state.get("course_title", "课程"),
        },
    )
    return {
        **state,
        "resource_plan": plan if isinstance(plan, dict) else {"items": plan},
        "messages": [*state.get("messages", []), "ResourcePlannerAgent 制定多模态资源生成计划"],
    }
