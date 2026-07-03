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


def test_compliance_pass_branch():
    state = compliance_agent(
        {
            "tutor_answer": {"answer": "while 循环需要条件更新，并引用课程资料。"},
            "generated_resources": [{"content": "Python 循环结构练习"}],
            "retrieved_context": [{"citation_id": "c1"}],
            "knowledge_evidence": {"citation_count": 1},
        }
    )
    assert should_retry_or_arbitrate(state) == "pass"


def test_compliance_retry_branch_before_max_retry():
    state = {"audit_result": {"review_status": "needs_review", "risk_level": "medium"}, "retry_count": 1}
    assert should_retry_or_arbitrate(state) == "retry"


def test_compliance_arbitration_after_retry_limit():
    state = {"audit_result": {"review_status": "needs_review", "risk_level": "medium"}, "retry_count": 3}
    assert should_retry_or_arbitrate(state) == "teacher_arbitration"


def test_audit_retry_regenerates_resource_content():
    state = {
        "audit_result": {"review_status": "needs_review", "risk_level": "medium", "failure_reasons": ["引用不足"]},
        "generated_resources": [{"title": "资源", "content": "原内容"}],
        "messages": [],
    }
    retried = audit_retry(state)
    assert retried["retry_count"] == 1
    assert retried["generated_resources"][0]["audit_revision"]
    assert retried["generated_resources"][0]["before_content_summary"] == "原内容"
    assert retried["generated_resources"][0]["after_content_summary"]
    assert "Audit retry" in retried["messages"][-1]
