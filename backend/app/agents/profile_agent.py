from __future__ import annotations

from app.agents.state import AgentState
from app.services.llm_service import llm_service


def profile_agent(state: AgentState) -> AgentState:
    # 如果 state 中已有对话式构建的画像，直接使用，不再调用 LLM 重新生成
    existing_profile = state.get("student_profile")
    if existing_profile and isinstance(existing_profile, dict) and existing_profile.get("source") == "dialog":
        return {
            **state,
            "messages": [*state.get("messages", []), "ProfileAgent 使用对话式画像结果"],
        }

    profile = llm_service.generate_json("profile", dict(state))
    return {
        **state,
        "student_profile": profile,
        "messages": [*state.get("messages", []), "ProfileAgent 生成学生画像"],
    }
