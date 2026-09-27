import pytest

from app.services.governance_service import create_teacher_arbitration_state, resume_after_teacher_decision


@pytest.mark.parametrize("risk_level", ["low", "medium", "high"])
def test_teacher_arbitration_pending(risk_level: str):
    result = create_teacher_arbitration_state(
        {"run_id": f"run-{risk_level}", "retry_count": 1, "audit_result": {"risk_level": risk_level}}
    )
    assert result["status"] == "pending"
    assert result["review_item"]["risk_level"] == risk_level
    assert result["allowed_actions"] == ["approve", "revise", "reject"]


def test_teacher_arbitration_approve():
    result = resume_after_teacher_decision({"run_id": "run-approve", "messages": []}, "approve", "通过")
    assert result["teacher_arbitration_result"]["status"] == "approved"
    assert result["current_node"] == "ReporterAgent"


def test_teacher_arbitration_revise():
    result = resume_after_teacher_decision(
        {"run_id": "run-revise", "messages": [], "audit_result": {}},
        "revise",
        "补充解释",
        "补充 continue 说明",
    )
    assert result["teacher_arbitration_result"]["status"] == "revised"
    assert result["teacher_arbitration_result"]["revised_content"] == "补充 continue 说明"
    assert result["current_node"] == "ResourceAgent"


def test_teacher_arbitration_reject():
    result = resume_after_teacher_decision({"run_id": "run-reject", "messages": []}, "reject", "超纲")
    assert result["teacher_arbitration_result"]["status"] == "rejected"
    assert result["current_node"] == "END"


def test_graph_after_arbitration_approve_to_reporter():
    result = resume_after_teacher_decision({"run_id": "run-approve", "messages": []}, "approve")
    assert result["current_node"] == "ReporterAgent"
