from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_teacher_arbitration_pending():
    result = client.get("/api/v1/teacher-arbitrations")
    assert result.status_code == 200
    data = result.json()
    assert len(data) >= 3
    assert {item["risk_level"] for item in data} >= {"low", "medium", "high"}


def test_teacher_arbitration_approve():
    result = client.post("/api/v1/teacher-arbitration/demo-arb-low/decision", json={"decision": "approve", "teacher_comment": "通过"})
    assert result.status_code == 200
    assert result.json()["status"] == "approved"


def test_teacher_arbitration_revise():
    result = client.post(
        "/api/v1/teacher-arbitration/demo-arb-medium/decision",
        json={"decision": "revise", "teacher_comment": "补充解释", "revised_content": "补充 continue 说明", "suggested_action": "regenerate"},
    )
    assert result.status_code == 200
    assert result.json()["status"] == "revised"
    assert result.json()["revised_content"]


def test_teacher_arbitration_reject():
    result = client.post("/api/v1/teacher-arbitration/demo-arb-high/decision", json={"decision": "reject", "teacher_comment": "超纲"})
    assert result.status_code == 200
    assert result.json()["status"] == "rejected"


def test_graph_after_arbitration_approve_to_reporter():
    result = client.post("/api/v1/teacher-arbitration/demo-arb-low/decision", json={"decision": "approve"})
    assert result.status_code == 200
    assert result.json()["next_node"] == "ReporterAgent"
