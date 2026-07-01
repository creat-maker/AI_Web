from __future__ import annotations

from app.agents.audit_agent import audit_agent
from app.agents.evaluator_agent import evaluator_agent
from app.agents.governance_agent import audit_retry, compliance_agent, should_retry_or_arbitrate, teacher_arbitration_agent
from app.agents.knowledge_agent import knowledge_agent
from app.agents.planner_agent import planner_agent
from app.agents.profile_agent import profile_agent
from app.agents.reporter_agent import reporter_agent
from app.agents.resource_agent import resource_agent
from app.agents.resource_planner_agent import resource_planner_agent
from app.agents.state import AgentState
from app.agents.tutor_agent import tutor_agent


def build_learning_graph():
    from langgraph.graph import END, StateGraph

    workflow = StateGraph(AgentState)
    workflow.add_node("ProfileAgent", profile_agent)
    workflow.add_node("KnowledgeAgent", knowledge_agent)
    workflow.add_node("PlannerAgent", planner_agent)
    workflow.add_node("ResourcePlannerAgent", resource_planner_agent)
    workflow.add_node("ResourceAgent", resource_agent)
    workflow.add_node("TutorAgent", tutor_agent)
    workflow.add_node("EvaluatorAgent", evaluator_agent)
    workflow.add_node("AuditAgent", audit_agent)
    workflow.add_node("ComplianceAgent", compliance_agent)
    workflow.add_node("AuditRetry", audit_retry)
    workflow.add_node("TeacherArbitration", teacher_arbitration_agent)
    workflow.add_node("ReporterAgent", reporter_agent)
    workflow.set_entry_point("ProfileAgent")
    workflow.add_edge("ProfileAgent", "KnowledgeAgent")
    workflow.add_edge("KnowledgeAgent", "PlannerAgent")
    workflow.add_edge("PlannerAgent", "ResourcePlannerAgent")
    workflow.add_edge("ResourcePlannerAgent", "ResourceAgent")
    workflow.add_edge("ResourceAgent", "TutorAgent")
    workflow.add_edge("TutorAgent", "EvaluatorAgent")
    workflow.add_edge("EvaluatorAgent", "AuditAgent")
    workflow.add_edge("AuditAgent", "ComplianceAgent")
    workflow.add_conditional_edges(
        "ComplianceAgent",
        should_retry_or_arbitrate,
        {"retry": "AuditRetry", "teacher_arbitration": "TeacherArbitration", "pass": "ReporterAgent"},
    )
    workflow.add_edge("AuditRetry", "ResourceAgent")
    workflow.add_edge("TeacherArbitration", "ReporterAgent")
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
            knowledge_agent,
            planner_agent,
            resource_planner_agent,
            resource_agent,
            tutor_agent,
            evaluator_agent,
            audit_agent,
            compliance_agent,
            reporter_agent,
        ):
            state = node(state)
            if node is compliance_agent:
                branch = should_retry_or_arbitrate(state)
                while branch == "retry" and int(state.get("retry_count") or 0) < 3:
                    state = audit_retry(state)
                    state = resource_agent(state)
                    state = tutor_agent(state)
                    state = evaluator_agent(state)
                    state = audit_agent(state)
                    state = compliance_agent(state)
                    branch = should_retry_or_arbitrate(state)
                if branch == "teacher_arbitration":
                    state = teacher_arbitration_agent(state)
        state["messages"] = [
            *state.get("messages", []),
            "当前环境未安装 langgraph，已使用顺序兜底；安装 requirements 后自动启用 LangGraph。",
        ]
        return state
