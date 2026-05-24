from __future__ import annotations

from app.agents.state import AgentState
from app.services.llm_service import llm_service


def profile_agent(state: AgentState) -> AgentState:
    profile = llm_service.generate_json("profile", dict(state))
    return {
        **state,
        "student_profile": profile,
        "messages": [*state.get("messages", []), "ProfileAgent 生成学生画像"],
    }
