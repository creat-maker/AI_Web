from __future__ import annotations

from app.agents.state import AgentState
from app.services.llm_service import llm_service


def evaluator_agent(state: AgentState) -> AgentState:
    quiz = state.get("quiz", {})
    answers = {
        question.get("id"): "演示作答：能够说明基本概念并给出一个简单应用。"
        for question in quiz.get("questions", [])
    }
    result = llm_service.generate_json(
        "evaluate",
        {"quiz": quiz, "answers": answers, "profile": state.get("student_profile", {})},
    )
    return {
        **state,
        "quiz_submission": {"answers": answers},
        "evaluation_result": result,
        "messages": [*state.get("messages", []), "EvaluatorAgent 完成测评反馈"],
    }
