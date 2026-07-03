from app.agents.audit_agent import audit_agent
from app.agents.governance_agent import AUDIT_DIMENSIONS, compliance_agent, rule_engine_check, should_retry_or_arbitrate
from app.services.xfyun_safety_service import xfyun_safety_service


def test_rule_engine_has_seven_dimensions():
    result = rule_engine_check({"tutor_answer": {"answer": "while 循环条件更新"}, "retrieved_context": [{"id": 1}]})
    assert len(result["checks"]) == len(AUDIT_DIMENSIONS)
    assert result["risk_level"] in {"low", "medium", "high"}


def test_xfyun_fallback_and_high_risk_arbitration():
    assert xfyun_safety_service.status()["status"] in {"not_configured", "configured"}
    state = compliance_agent({"tutor_answer": {"answer": "手机号 身份证"}, "generated_resources": []})
    assert state["audit_result"]["risk_level"] == "high"


def test_audit_agent_returns_stable_result_shape():
    state = audit_agent(
        {
            "student_profile": {"student_name": "李明"},
            "learning_path": {"stages": []},
            "generated_resources": [{"content": "while 循环讲义"}],
            "tutor_answer": {"answer": "while 循环需要条件更新"},
            "retrieved_context": [{"citation_id": "c1"}],
            "knowledge_evidence": {"confidence": 0.8},
            "messages": [],
        }
    )
    assert isinstance(state["audit_result"], dict)
    assert state["messages"]


def test_rule_engine_fallback_when_xfyun_not_configured():
    state = compliance_agent(
        {
            "tutor_answer": {"answer": "while 循环条件更新"},
            "generated_resources": [{"content": "Python 循环结构"}],
            "retrieved_context": [{"citation_id": "c1"}],
        }
    )
    assert state["audit_result"]["xfyun_result"]["provider"] == "xfyun_safety"
    assert state["audit_result"]["review_status"] in {"passed", "needs_review", "blocked"}


def test_medium_risk_increases_retry_count_path():
    state = compliance_agent({"tutor_answer": {"answer": "没有引用的循环解释"}, "generated_resources": [], "retrieved_context": []})
    assert should_retry_or_arbitrate({**state, "retry_count": 0}) in {"retry", "teacher_arbitration"}
