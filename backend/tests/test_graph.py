from app.agents.governance_agent import audit_retry, compliance_agent, should_retry_or_arbitrate, teacher_arbitration_agent


def test_audit_retry_and_teacher_arbitration_branch():
    state = compliance_agent({"tutor_answer": {"answer": "身份证 和 暴力 内容"}, "generated_resources": [], "retrieved_context": []})
    assert should_retry_or_arbitrate(state) == "teacher_arbitration"
    arbitrated = teacher_arbitration_agent(state)
    assert arbitrated["teacher_arbitration_result"]["status"] == "pending"


def test_retry_count_records_modified_fields():
    state = {"audit_result": {"review_status": "needs_review", "risk_level": "medium"}, "generated_resources": [{"title": "资源"}]}
    retried = audit_retry(state)
    assert retried["retry_count"] == 1
    assert retried["audit_retry_log"][0]["modified_fields"]
