from __future__ import annotations

from app.agents.evaluator_agent import evaluator_agent
from app.agents.planner_agent import planner_agent
from app.agents.profile_agent import profile_agent
from app.agents.reporter_agent import reporter_agent
from app.agents.resource_agent import resource_agent
from app.agents.state import AgentState
from app.agents.tutor_agent import tutor_agent


def build_learning_graph():
    from langgraph.graph import END, StateGraph

    workflow = StateGraph(AgentState)
    workflow.add_node("ProfileAgent", profile_agent)
    workflow.add_node("PlannerAgent", planner_agent)
    workflow.add_node("ResourceAgent", resource_agent)
    workflow.add_node("TutorAgent", tutor_agent)
    workflow.add_node("EvaluatorAgent", evaluator_agent)
    workflow.add_node("ReporterAgent", reporter_agent)
    workflow.set_entry_point("ProfileAgent")
    workflow.add_edge("ProfileAgent", "PlannerAgent")
    workflow.add_edge("PlannerAgent", "ResourceAgent")
    workflow.add_edge("ResourceAgent", "TutorAgent")
    workflow.add_edge("TutorAgent", "EvaluatorAgent")
    workflow.add_edge("EvaluatorAgent", "ReporterAgent")
    workflow.add_edge("ReporterAgent", END)
    return workflow.compile()


def run_full_learning_graph(initial_state: AgentState) -> AgentState:
    try:
        graph = build_learning_graph()
        return graph.invoke(initial_state)
    except ModuleNotFoundError as exc:
        if exc.name != "langgraph":
            raise
        state = dict(initial_state)
        for node in (
            profile_agent,
            planner_agent,
            resource_agent,
            tutor_agent,
            evaluator_agent,
            reporter_agent,
        ):
            state = node(state)
        state["messages"] = [
            *state.get("messages", []),
            "当前环境未安装 langgraph，已使用顺序兜底；安装 requirements 后自动启用 LangGraph。",
        ]
        return state
