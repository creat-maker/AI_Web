from app.agents.governance_agent import audit_retry, compliance_agent, should_retry_or_arbitrate, teacher_arbitration_agent
from app.agents import graph as graph_module
from app.agents.graph import continue_after_teacher_arbitration, route_after_teacher_arbitration
from app.agents.resource_agent import resource_agent
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
    approved = resume_after_teacher_decision(state, "approve")
    assert approved["current_node"] == "ReporterAgent"
    assert approved["audit_result"]["review_status"] == "teacher_approved"
    revised = resume_after_teacher_decision(state, "revise", "请重写")
    assert revised["current_node"] == "ResourceAgent"
    assert revised["retry_context"]["teacher_comment"] == "请重写"
    rejected = resume_after_teacher_decision(state, "reject", "拒绝")
    assert rejected["publication_blocked"] is True
    assert rejected["audit_result"]["review_status"] == "rejected"


def test_revise_resumes_resource_generation_and_reaudit(monkeypatch):
    calls: list[str] = []

    def node(name, updates):
        def run(state):
            calls.append(name)
            return {**state, **updates}

        return run

    monkeypatch.setattr(graph_module, "resource_agent", node("resource", {"generated_resources": [{"content": "重写后内容"}]}))
    monkeypatch.setattr(graph_module, "tutor_agent", node("tutor", {"tutor_answer": {"answer": "重写后答疑"}}))
    monkeypatch.setattr(graph_module, "evaluator_agent", node("evaluator", {"evaluation_result": {"score": 80}}))
    monkeypatch.setattr(graph_module, "audit_agent", node("audit", {}))
    monkeypatch.setattr(
        graph_module,
        "compliance_agent",
        node("compliance", {"audit_result": {"review_status": "passed", "risk_level": "low"}}),
    )
    monkeypatch.setattr(graph_module, "reporter_agent", node("reporter", {"report_path": "report.docx"}))

    pending = teacher_arbitration_agent(
        {
            "run_id": "run-resume",
            "course_id": 1,
            "generated_resources": [{"content": "原内容"}],
            "audit_result": {"review_status": "blocked", "risk_level": "high"},
            "retry_count": 3,
        }
    )
    resumed = resume_after_teacher_decision(pending, "revise", "请重新生成")
    completed = continue_after_teacher_arbitration(resumed)

    assert calls == ["resource", "tutor", "evaluator", "audit", "compliance", "reporter"]
    assert completed["status"] == "success"
    assert completed["generated_resources"][0]["content"] == "重写后内容"
    assert completed["report_path"] == "report.docx"


def test_resource_regeneration_consumes_teacher_revised_content():
    state = resource_agent(
        {
            "course_title": "Python 程序设计",
            "student_profile": {},
            "learning_path": {},
            "resource_plan": {},
            "retrieved_context": [],
            "knowledge_evidence": {},
            "retry_count": 2,
            "retry_context": {"teacher_comment": "补充 continue 解释"},
            "teacher_revised_content": "continue 只跳过当前一轮，不会终止整个循环。",
        }
    )

    assert state["generated_resources"]
    assert state["generated_resources"][0]["teacher_revision_reference"]
    assert state["generated_resources"][0]["content"].startswith("教师修订依据：continue")
