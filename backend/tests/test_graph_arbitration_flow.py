from app.agents.governance_agent import audit_retry, compliance_agent, should_retry_or_arbitrate, teacher_arbitration_agent
from app.agents.graph import route_after_teacher_arbitration
from app.services.governance_service import resume_after_teacher_decision


def test_graph_audit_pass_to_reporter():
    state = compliance_agent({"tutor_answer": {"answer": "while 循环需要变量更新"}, "generated_resources": [{"content": "Python 循环"}], "retrieved_context": [{"citation_id": "c1"}], "knowledge_evidence": {"citation_count": 1}})
    assert should_retry_or_arbitrate(state) == "pass"


def test_graph_audit_fail_retry_then_pass_context():
    state = {"audit_result": {"review_status": "needs_review", "risk_level": "medium", "checks": [{"dimension": "课程对齐度", "status": "warning"}]}, "generated_resources": [{"title": "资源", "content": "原内容"}]}
    retried = audit_retry(state)
    assert retried["retry_context"]["failed_rules"] == ["课程对齐度"]
    assert retried["generated_resources"][0]["content_version"] == 2


def test_graph_max_retry_to_teacher_arbitration():
    state = {"audit_result": {"review_status": "needs_review", "risk_level": "medium"}, "retry_count": 3}
    assert should_retry_or_arbitrate(state) == "teacher_arbitration"
    pending = teacher_arbitration_agent(state)
    assert pending["teacher_arbitration_result"]["review_item"]
    assert route_after_teacher_arbitration(pending) == "end"


def test_teacher_decisions_route():
    state = teacher_arbitration_agent({"run_id": "run-test", "audit_result": {"review_status": "blocked"}, "retry_count": 3})
    assert resume_after_teacher_decision(state, "approve")["current_node"] == "ReporterAgent"
    revised = resume_after_teacher_decision(state, "revise", "请重写")
    assert revised["current_node"] == "ResourceAgent"
    assert revised["retry_context"]["teacher_comment"] == "请重写"
    rejected = resume_after_teacher_decision(state, "reject", "拒绝")
    assert rejected["publication_blocked"] is True
