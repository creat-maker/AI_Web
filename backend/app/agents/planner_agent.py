from __future__ import annotations

from app.agents.state import AgentState
from app.services.llm_service import llm_service


def planner_agent(state: AgentState) -> AgentState:
    path = llm_service.generate_json(
        "learning_path",
        {
            "profile": state.get("student_profile", {}),
            "course_title": state.get("course_title", "课程"),
            "contexts": state.get("retrieved_context", []),
            "knowledge_evidence": state.get("knowledge_evidence", {}),
        },
    )
    return {
        **state,
        "learning_path": path,
        "messages": [*state.get("messages", []), "PlannerAgent 生成学习路径"],
    }
