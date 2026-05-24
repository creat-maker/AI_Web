from __future__ import annotations

from app.agents.state import AgentState
from app.services.llm_service import llm_service


def resource_agent(state: AgentState) -> AgentState:
    resources = llm_service.generate_json(
        "resources",
        {"profile": state.get("student_profile", {}), "learning_path": state.get("learning_path", {})},
    )
    quiz = llm_service.generate_json("quiz", {"course_title": state.get("course_title", "课程")})
    return {
        **state,
        "generated_resources": resources,
        "quiz": quiz,
        "messages": [*state.get("messages", []), "ResourceAgent 生成学习资源和测验"],
    }
