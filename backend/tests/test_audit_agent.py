from app.agents.governance_agent import AUDIT_DIMENSIONS, compliance_agent, rule_engine_check
from app.services.xfyun_safety_service import xfyun_safety_service


def test_rule_engine_has_seven_dimensions():
    result = rule_engine_check({"tutor_answer": {"answer": "while 循环条件更新"}, "retrieved_context": [{"id": 1}]})
    assert len(result["checks"]) == len(AUDIT_DIMENSIONS)
    assert result["risk_level"] in {"low", "medium", "high"}


def test_xfyun_fallback_and_high_risk_arbitration():
    assert xfyun_safety_service.status()["status"] in {"not_configured", "configured"}
    state = compliance_agent({"tutor_answer": {"answer": "手机号 身份证"}, "generated_resources": []})
    assert state["audit_result"]["risk_level"] == "high"
