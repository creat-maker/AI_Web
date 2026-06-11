from __future__ import annotations

from app.agents.state import AgentState
from app.services.llm_service import llm_service


def resource_agent(state: AgentState) -> AgentState:
    resources = llm_service.generate_json(
        "resources",
        {
            "profile": state.get("student_profile", {}),
            "learning_path": state.get("learning_path", {}),
            "resource_plan": state.get("resource_plan", {}),
            "contexts": state.get("retrieved_context", []),
            "knowledge_evidence": state.get("knowledge_evidence", {}),
        },
    )
    resource_items = resources if isinstance(resources, list) else resources.get("items", [])
    quiz = llm_service.generate_json("quiz", {"course_title": state.get("course_title", "课程")})
    return {
        **state,
        "generated_resources": resource_items,
        "quiz": quiz,
        "messages": [*state.get("messages", []), f"ResourceAgent 生成 {len(resource_items)} 个个性化学习资源"],
    }
