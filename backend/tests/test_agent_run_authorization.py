from __future__ import annotations

import time
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routers import agent_workflow
from app.api.routers.auth import _sign_jwt
from app.db.session import Base, get_db
from app.main import app
from app.models import AgentRun, AuditLog, Course, StudentProfile, SystemLog
from app.services.business_event_service import event_to_dict
from app.services.json_utils import dumps, loads


@dataclass
class AgentRunContext:
    client: TestClient
    session_factory: sessionmaker
    own_course_id: int
    foreign_course_id: int
    own_run_id: int
    peer_run_id: int
    foreign_run_id: int
    pending_run_id: int
    rejected_run_id: int


def _auth_headers(role: str, *, user_id: str | None = None, name: str | None = None) -> dict[str, str]:
    now = int(time.time())
    defaults = {
        "student": ("student_001", "李明"),
        "teacher": ("teacher_001", "王老师"),
        "admin": ("admin_001", "管理员"),
    }
    principal, display_name = defaults[role]
    principal = user_id or principal
    token = _sign_jwt(
        {
            "username": principal,
            "user_id": principal,
            "role": role,
            "name": name or display_name,
            "display_name": name or display_name,
            "iat": now,
            "exp": now + 3600,
        }
    )
    return {"Authorization": f"Bearer {token}"}


def _run(course_id: int, profile_id: int, run_id: str, status: str = "success") -> AgentRun:
    return AgentRun(
        course_id=course_id,
        student_profile_id=profile_id,
        workflow_name="q015-test",
        input_json=dumps({"learning_goal": run_id, "student_name": run_id}),
        output_json=dumps(
            {
                "steps": [{"key": "trace", "status": status}],
                "artifacts": {},
                "workflow_summary": {"status": status, "artifact_count": 0},
            }
        ),
        state=dumps({"run_id": run_id, "status": status}),
        messages=dumps(["q015"]),
        audit_result=dumps({"review_status": "passed"}),
        teacher_arbitration_result=dumps(
            {"status": "rejected", "decision": "reject"} if status == "rejected" else {}
        ),
        status=status,
        current_node="END" if status == "rejected" else "ReporterAgent",
        run_id=run_id,
        retry_count=0,
    )


@pytest.fixture()
def agent_run_context(monkeypatch: pytest.MonkeyPatch) -> AgentRunContext:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = testing_session()
    own_course = Course(title="Python 程序设计", teacher_name="王老师")
    foreign_course = Course(title="人工智能导论", teacher_name="张老师")
    db.add_all([own_course, foreign_course])
    db.flush()
    own_profile = StudentProfile(
        owner_user_id="student_001",
        demo_profile_key="demo-basic",
        student_name="李明",
        course_id=own_course.id,
        profile_json=dumps({"user_id": "student_001"}),
    )
    peer_profile = StudentProfile(
        owner_user_id="student_peer",
        demo_profile_key="demo-peer",
        student_name="同课学生",
        course_id=own_course.id,
        profile_json=dumps({"user_id": "student_peer"}),
    )
    foreign_profile = StudentProfile(
        owner_user_id="student_foreign",
        demo_profile_key="demo-foreign",
        student_name="跨课学生",
        course_id=foreign_course.id,
        profile_json=dumps({"user_id": "student_foreign"}),
    )
    db.add_all([own_profile, peer_profile, foreign_profile])
    db.flush()
    own_run = _run(own_course.id, own_profile.id, "q015-own")
    peer_run = _run(own_course.id, peer_profile.id, "q015-peer")
    foreign_run = _run(foreign_course.id, foreign_profile.id, "q015-foreign")
    pending_run = _run(own_course.id, own_profile.id, "q015-pending", "pending_review")
    rejected_run = _run(own_course.id, own_profile.id, "q015-rejected", "rejected")
    db.add_all([own_run, peer_run, foreign_run, pending_run, rejected_run])
    db.commit()
    ids = (
        own_course.id,
        foreign_course.id,
        own_run.id,
        peer_run.id,
        foreign_run.id,
        pending_run.id,
        rejected_run.id,
    )
    db.close()

    monkeypatch.setattr(
        agent_workflow,
        "run_full_learning_graph",
        lambda state: {
            **state,
            "student_profile": {"student_name": state.get("student_name")},
            "learning_path": {},
            "generated_resources": [],
            "quiz": {},
            "retrieved_context": [],
            "knowledge_evidence": {},
            "resource_plan": {},
            "evaluation_result": {},
            "audit_result": {"review_status": "passed", "risk_level": "low"},
            "messages": [],
            "status": "success",
        },
    )

    def override_get_db():
        test_db = testing_session()
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield AgentRunContext(client, testing_session, *ids)
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def student_headers() -> dict[str, str]:
    return _auth_headers("student")


@pytest.fixture()
def teacher_headers() -> dict[str, str]:
    return _auth_headers("teacher")


@pytest.fixture()
def other_teacher_headers() -> dict[str, str]:
    return _auth_headers("teacher", user_id="teacher_002", name="张老师")


@pytest.fixture()
def admin_headers() -> dict[str, str]:
    return _auth_headers("admin")


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/v1/agent-workflow"),
        ("GET", "/api/v1/agent-workflow/runs"),
        ("GET", "/api/v1/agent-workflow/runs/1"),
        ("POST", "/api/v1/agent-workflow/runs/1/rerun"),
        ("POST", "/api/v1/agent-workflow/run-full-learning-flow"),
        ("POST", "/api/v1/agent-workflow/run-full-learning-flow/stream"),
        ("GET", "/api/v1/agent-runs"),
        ("GET", "/api/v1/agent-runs/q015-own"),
    ],
)
def test_q015_all_agent_run_operations_require_authentication(
    agent_run_context: AgentRunContext, method: str, path: str
):
    payload = {
        "course_id": agent_run_context.own_course_id,
        "student_name": "Q015学生",
        "current_level": "基础",
        "learning_goal": "循环结构",
        "weak_points": ["while"],
        "learning_preference": "案例",
    }
    response = agent_run_context.client.request(method, path, json=payload if method == "POST" else None)
    assert response.status_code == 401, f"{method} {path}: {response.status_code}"


@pytest.mark.parametrize("path", ["/api/v1/agent-workflow", "/api/v1/agent-workflow/runs", "/api/v1/agent-runs"])
def test_q015_student_lists_only_owned_runs(
    agent_run_context: AgentRunContext, student_headers: dict[str, str], path: str
):
    response = agent_run_context.client.get(path, headers=student_headers)
    assert response.status_code == 200
    body = response.json()
    rows = body.get("records", []) if isinstance(body, dict) else body
    returned_ids = {row.get("id") for row in rows}
    assert agent_run_context.own_run_id in returned_ids
    assert agent_run_context.peer_run_id not in returned_ids
    assert agent_run_context.foreign_run_id not in returned_ids


@pytest.mark.parametrize(
    "path_factory",
    [
        lambda c: f"/api/v1/agent-workflow/runs/{c.own_run_id}",
        lambda c: "/api/v1/agent-runs/q015-own",
    ],
)
def test_q015_student_reads_own_run(
    agent_run_context: AgentRunContext, student_headers: dict[str, str], path_factory
):
    response = agent_run_context.client.get(path_factory(agent_run_context), headers=student_headers)
    assert response.status_code == 200
    assert response.json()["student_profile_id" if "agent-workflow" in path_factory(agent_run_context) else "student_id"]


@pytest.mark.parametrize(
    "path_factory",
    [
        lambda c: f"/api/v1/agent-workflow/runs/{c.peer_run_id}",
        lambda c: "/api/v1/agent-runs/q015-peer",
        lambda c: f"/api/v1/agent-workflow/runs/{c.foreign_run_id}",
        lambda c: "/api/v1/agent-runs/q015-foreign",
    ],
)
def test_q015_student_cannot_enumerate_other_runs(
    agent_run_context: AgentRunContext, student_headers: dict[str, str], path_factory
):
    response = agent_run_context.client.get(path_factory(agent_run_context), headers=student_headers)
    assert response.status_code == 404


@pytest.mark.parametrize("path", ["/api/v1/agent-workflow/runs", "/api/v1/agent-runs"])
def test_q015_teacher_lists_only_authorized_course_runs(
    agent_run_context: AgentRunContext, teacher_headers: dict[str, str], path: str
):
    response = agent_run_context.client.get(path, headers=teacher_headers)
    assert response.status_code == 200
    rows = response.json()
    assert agent_run_context.own_run_id in {row["id"] for row in rows}
    assert agent_run_context.peer_run_id in {row["id"] for row in rows}
    assert agent_run_context.foreign_run_id not in {row["id"] for row in rows}


def test_q015_teacher_cross_course_detail_is_hidden(
    agent_run_context: AgentRunContext, teacher_headers: dict[str, str]
):
    response = agent_run_context.client.get(
        f"/api/v1/agent-workflow/runs/{agent_run_context.foreign_run_id}", headers=teacher_headers
    )
    assert response.status_code == 404


def test_q015_other_teacher_can_read_own_mapped_course(
    agent_run_context: AgentRunContext, other_teacher_headers: dict[str, str]
):
    response = agent_run_context.client.get(
        f"/api/v1/agent-workflow/runs/{agent_run_context.foreign_run_id}", headers=other_teacher_headers
    )
    assert response.status_code == 200


def test_q015_admin_has_global_read_access(agent_run_context: AgentRunContext, admin_headers: dict[str, str]):
    response = agent_run_context.client.get("/api/v1/agent-runs", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_q015_student_cannot_rerun(agent_run_context: AgentRunContext, student_headers: dict[str, str]):
    response = agent_run_context.client.post(
        f"/api/v1/agent-workflow/runs/{agent_run_context.own_run_id}/rerun", headers=student_headers
    )
    assert response.status_code == 403


def test_q015_teacher_cannot_rerun_cross_course(agent_run_context: AgentRunContext, teacher_headers: dict[str, str]):
    response = agent_run_context.client.post(
        f"/api/v1/agent-workflow/runs/{agent_run_context.foreign_run_id}/rerun", headers=teacher_headers
    )
    assert response.status_code == 404


@pytest.mark.parametrize("run_attr", ["pending_run_id", "rejected_run_id"])
def test_q015_non_rerunnable_states_return_conflict(
    agent_run_context: AgentRunContext, teacher_headers: dict[str, str], run_attr: str
):
    response = agent_run_context.client.post(
        f"/api/v1/agent-workflow/runs/{getattr(agent_run_context, run_attr)}/rerun", headers=teacher_headers
    )
    assert response.status_code == 409


def test_q015_rerun_is_single_use_and_actor_comes_from_jwt(
    agent_run_context: AgentRunContext, teacher_headers: dict[str, str]
):
    path = f"/api/v1/agent-workflow/runs/{agent_run_context.own_run_id}/rerun"
    first = agent_run_context.client.post(path, headers=teacher_headers)
    second = agent_run_context.client.post(path, headers=teacher_headers)
    assert first.status_code == 200
    assert second.status_code == 409

    db = agent_run_context.session_factory()
    try:
        children = [
            row
            for row in db.query(AgentRun).all()
            if loads(row.input_json, {}).get("rerun_from") == agent_run_context.own_run_id
        ]
        audits = (
            db.query(AuditLog)
            .filter(AuditLog.action == "agent_run_rerun", AuditLog.target_id == str(agent_run_context.own_run_id))
            .all()
        )
        assert len(children) == 1
        assert len(audits) == 1
        assert (audits[0].actor_id, audits[0].actor_name, audits[0].actor_role) == (
            "teacher_001",
            "王老师",
            "teacher",
        )
    finally:
        db.close()


def test_q015_workflow_start_requires_course_scope_and_records_jwt_actor(
    agent_run_context: AgentRunContext, teacher_headers: dict[str, str]
):
    payload = {
        "course_id": agent_run_context.own_course_id,
        "student_name": "Q015学生",
        "current_level": "基础",
        "learning_goal": "循环结构",
        "weak_points": ["while"],
        "learning_preference": "案例",
    }
    success = agent_run_context.client.post(
        "/api/v1/agent-workflow/run-full-learning-flow", headers=teacher_headers, json=payload
    )
    assert success.status_code == 200

    payload["course_id"] = agent_run_context.foreign_course_id
    hidden = agent_run_context.client.post(
        "/api/v1/agent-workflow/run-full-learning-flow", headers=teacher_headers, json=payload
    )
    assert hidden.status_code == 404

    db = agent_run_context.session_factory()
    try:
        events = [
            event_to_dict(row)
            for row in db.query(SystemLog).all()
            if event_to_dict(row).get("event_type") == "agent_workflow_started"
        ]
        assert len(events) == 1
        assert (events[0]["actor_id"], events[0]["actor_name"], events[0]["actor_role"]) == (
            "teacher_001",
            "王老师",
            "teacher",
        )
    finally:
        db.close()


def test_q015_student_cannot_start_workflow(agent_run_context: AgentRunContext, student_headers: dict[str, str]):
    response = agent_run_context.client.post(
        "/api/v1/agent-workflow/run-full-learning-flow",
        headers=student_headers,
        json={
            "course_id": agent_run_context.own_course_id,
            "student_name": "李明",
            "current_level": "基础",
            "learning_goal": "循环结构",
            "weak_points": ["while"],
            "learning_preference": "案例",
        },
    )
    assert response.status_code == 403
