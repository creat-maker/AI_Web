from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routers.auth import _sign_jwt
from app.db.session import Base, get_db
from app.main import app
from app.models import AITaskRun, AgentRun, AuditLog, Course, ReviewItem, StudentProfile
from app.services.governance_service import create_teacher_arbitration_state
from app.services.json_utils import dumps, loads


class SecretHeaders(dict[str, str]):
    def __repr__(self) -> str:
        return "{'Authorization': 'Bearer [REDACTED]'}"


def _auth_headers(role: str, *, user_id: str | None = None, name: str | None = None) -> dict[str, str]:
    now = int(time.time())
    user_ids = {"student": "student_001", "teacher": "teacher_001", "admin": "admin_001"}
    names = {"student": "李明", "teacher": "王老师", "admin": "管理员"}
    principal = user_id or user_ids[role]
    token = _sign_jwt(
        {
            "username": principal,
            "user_id": principal,
            "role": role,
            "name": name or names[role],
            "display_name": name or names[role],
            "iat": now,
            "exp": now + 3600,
        }
    )
    return SecretHeaders({"Authorization": f"Bearer {token}"})


@dataclass
class ArbitrationContext:
    client: TestClient
    session_factory: sessionmaker
    own_run_id: int
    foreign_run_id: int
    completed_run_id: int
    mismatched_run_id: int
    review_item_id: int


def _pending_run(course_id: int, profile_id: int, run_id: str) -> AgentRun:
    arbitration = create_teacher_arbitration_state(
        {
            "run_id": run_id,
            "course_id": course_id,
            "retry_count": 1,
            "audit_result": {"risk_level": "medium", "review_status": "needs_review"},
            "generated_resources": [{"resource_type": "handout", "title": "原资源", "content": "原内容"}],
        }
    )
    state = {
        "run_id": run_id,
        "course_id": course_id,
        "student_profile_id": profile_id,
        "current_node": "TeacherArbitration",
        "status": "pending_review",
        "retry_count": 1,
        "messages": [],
        "generated_resources": [{"resource_type": "handout", "title": "原资源", "content": "原内容"}],
        "audit_result": {"risk_level": "medium", "review_status": "needs_review"},
        "teacher_arbitration_result": arbitration,
    }
    return AgentRun(
        course_id=course_id,
        student_profile_id=profile_id,
        workflow_name="q014-test",
        input_json=dumps({"student_name": run_id, "course_title": "隔离测试课程", "learning_goal": "循环结构"}),
        output_json=dumps({}),
        state=dumps(state),
        status="pending_review",
        current_node="TeacherArbitration",
        run_id=run_id,
        retry_count=1,
        audit_result=dumps({"risk_level": "medium", "review_status": "needs_review"}),
        teacher_arbitration_result=dumps(arbitration),
    )


@pytest.fixture()
def arbitration_context(tmp_path: Path) -> ArbitrationContext:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'q014-authorization.db'}",
        connect_args={"check_same_thread": False},
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
    foreign_profile = StudentProfile(
        owner_user_id="student_002",
        demo_profile_key="demo-foreign",
        student_name="其他课程学生",
        course_id=foreign_course.id,
        profile_json=dumps({"user_id": "student_002"}),
    )
    db.add_all([own_profile, foreign_profile])
    db.flush()

    own_run = _pending_run(own_course.id, own_profile.id, "q014-own")
    foreign_run = _pending_run(foreign_course.id, foreign_profile.id, "q014-foreign")
    mismatched_run = _pending_run(own_course.id, foreign_profile.id, "q014-mismatched-student")
    completed_run = _pending_run(own_course.id, own_profile.id, "q014-completed")
    completed_run.status = "success"
    completed_run.current_node = "ReporterAgent"
    completed_run.teacher_arbitration_result = dumps({"status": "approved", "decision": "approve"})
    db.add_all([own_run, foreign_run, mismatched_run, completed_run])
    db.flush()

    task = AITaskRun(
        task_type="resource_pack",
        title="Q014治理任务",
        actor_id="teacher_001",
        actor_role="teacher",
        input_summary=dumps({"course": "Python 程序设计"}),
        status="pending_review",
    )
    db.add(task)
    db.flush()
    review = ReviewItem(
        item_type="resource_pack",
        item_title="Q014复核项",
        source_task_id=task.id,
        content_json=dumps({"course": "Python 程序设计"}),
        status="pending_review",
    )
    db.add(review)
    db.commit()
    ids = (own_run.id, foreign_run.id, completed_run.id, mismatched_run.id, review.id)
    db.close()

    def override_get_db():
        test_db = testing_session()
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield ArbitrationContext(client, testing_session, *ids)
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
def admin_headers() -> dict[str, str]:
    return _auth_headers("admin")


def _decision_payload(run_id: str, decision: str, request_id: str, **extra) -> dict[str, str]:
    return {
        "decision": decision,
        "arbitration_item_id": f"arb-{run_id}-1-0",
        "decision_request_id": request_id,
        **extra,
    }


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("GET", "/api/v1/decision-center/overview", None),
        ("GET", "/api/v1/teacher-arbitrations", None),
        ("POST", "/api/v1/teacher-arbitration/1/decision", {"decision": "reject"}),
    ],
)
def test_q014_anonymous_cannot_reach_teacher_operations(
    arbitration_context: ArbitrationContext,
    method: str,
    path: str,
    payload: dict[str, str] | None,
):
    response = arbitration_context.client.request(method, path, json=payload)
    assert response.status_code == 401


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("GET", "/api/v1/decision-center/overview", None),
        ("GET", "/api/v1/teacher-arbitrations", None),
        ("POST", "/api/v1/teacher-arbitration/1/decision", {"decision": "reject", "actor_role": "teacher"}),
    ],
)
def test_q014_student_cannot_reach_teacher_operations(
    arbitration_context: ArbitrationContext,
    student_headers: dict[str, str],
    method: str,
    path: str,
    payload: dict[str, str] | None,
):
    response = arbitration_context.client.request(method, path, headers=student_headers, json=payload)
    assert response.status_code == 403


@pytest.mark.parametrize("role", ["teacher", "admin"])
@pytest.mark.parametrize("path", ["/api/v1/decision-center/overview", "/api/v1/teacher-arbitrations"])
def test_q014_staff_can_reach_read_operations(arbitration_context: ArbitrationContext, role: str, path: str):
    assert arbitration_context.client.get(path, headers=_auth_headers(role)).status_code == 200


def test_teacher_list_is_limited_to_explicit_demo_course_scope(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
):
    response = arbitration_context.client.get("/api/v1/teacher-arbitrations", headers=teacher_headers)
    assert response.status_code == 200
    ids = {item["agent_run_id"] for item in response.json()}
    assert arbitration_context.own_run_id in ids
    assert arbitration_context.foreign_run_id not in ids
    assert arbitration_context.completed_run_id not in ids


def test_admin_list_can_see_pending_runs_across_courses(
    arbitration_context: ArbitrationContext,
    admin_headers: dict[str, str],
):
    response = arbitration_context.client.get("/api/v1/teacher-arbitrations", headers=admin_headers)
    assert response.status_code == 200
    ids = {item["agent_run_id"] for item in response.json()}
    assert arbitration_context.own_run_id in ids
    assert arbitration_context.foreign_run_id in ids
    assert arbitration_context.completed_run_id not in ids


def test_teacher_cannot_decide_foreign_course_by_numeric_id(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
):
    response = arbitration_context.client.post(
        f"/api/v1/teacher-arbitration/{arbitration_context.foreign_run_id}/decision",
        headers=teacher_headers,
        json=_decision_payload("q014-foreign", "reject", "q020-foreign-numeric-0001"),
    )
    assert response.status_code == 404


def test_teacher_cannot_decide_foreign_course_by_run_id(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
):
    response = arbitration_context.client.post(
        "/api/v1/teacher-arbitration/q014-foreign/decision",
        headers=teacher_headers,
        json=_decision_payload("q014-foreign", "reject", "q020-foreign-run-0001"),
    )
    assert response.status_code == 404


def test_nonexistent_decision_does_not_create_ghost_audit(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
):
    db = arbitration_context.session_factory()
    before = db.query(AuditLog).filter(AuditLog.action == "teacher_arbitration_decision").count()
    db.close()
    response = arbitration_context.client.post(
        "/api/v1/teacher-arbitration/not-a-real-run/decision",
        headers=teacher_headers,
        json=_decision_payload("not-a-real-run", "approve", "q020-ghost-request-0001"),
    )
    assert response.status_code == 404
    db = arbitration_context.session_factory()
    assert db.query(AuditLog).filter(AuditLog.action == "teacher_arbitration_decision").count() == before
    db.close()


def test_non_pending_run_cannot_be_decided(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
):
    response = arbitration_context.client.post(
        f"/api/v1/teacher-arbitration/{arbitration_context.completed_run_id}/decision",
        headers=teacher_headers,
        json=_decision_payload("q014-completed", "approve", "q020-completed-request-0001"),
    )
    assert response.status_code == 409


def test_repeat_decision_is_rejected_without_duplicate_audit(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
):
    path = f"/api/v1/teacher-arbitration/{arbitration_context.own_run_id}/decision"
    first = arbitration_context.client.post(
        path,
        headers=teacher_headers,
        json=_decision_payload("q014-own", "reject", "q020-repeat-request-0001"),
    )
    assert first.status_code == 200
    second = arbitration_context.client.post(
        path,
        headers=teacher_headers,
        json=_decision_payload("q014-own", "reject", "q020-repeat-request-0002"),
    )
    assert second.status_code == 409
    db = arbitration_context.session_factory()
    logs = db.query(AuditLog).filter(AuditLog.action == "teacher_arbitration_decision").all()
    assert len(logs) == 1
    db.close()


def test_admin_decision_audit_actor_comes_from_jwt(
    arbitration_context: ArbitrationContext,
    admin_headers: dict[str, str],
):
    response = arbitration_context.client.post(
        f"/api/v1/teacher-arbitration/{arbitration_context.foreign_run_id}/decision",
        headers=admin_headers,
        json=_decision_payload(
            "q014-foreign", "reject", "q020-admin-request-0001", teacher_comment="管理员复核"
        ),
    )
    assert response.status_code == 200
    db = arbitration_context.session_factory()
    log = db.query(AuditLog).filter(AuditLog.action == "teacher_arbitration_decision").one()
    assert (log.actor_id, log.actor_name, log.actor_role) == ("admin_001", "管理员", "admin")
    db.close()


def test_student_profile_course_must_match_agent_run_course(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
):
    response = arbitration_context.client.post(
        f"/api/v1/teacher-arbitration/{arbitration_context.mismatched_run_id}/decision",
        headers=teacher_headers,
        json=_decision_payload("q014-mismatched-student", "reject", "q020-mismatch-request-0001"),
    )
    assert response.status_code == 409


def test_second_teacher_actor_and_scope_come_from_signed_jwt(arbitration_context: ArbitrationContext):
    headers = _auth_headers("teacher", user_id="teacher_002", name="张老师")
    listing = arbitration_context.client.get("/api/v1/teacher-arbitrations", headers=headers)
    assert listing.status_code == 200
    assert {item["agent_run_id"] for item in listing.json()} == {arbitration_context.foreign_run_id}
    response = arbitration_context.client.post(
        f"/api/v1/teacher-arbitration/{arbitration_context.foreign_run_id}/decision",
        headers=headers,
        json=_decision_payload(
            "q014-foreign", "reject", "q020-teacher2-request-0001", teacher_comment="第二教师复核"
        ),
    )
    assert response.status_code == 200
    db = arbitration_context.session_factory()
    log = db.query(AuditLog).filter(AuditLog.action == "teacher_arbitration_decision").one()
    assert (log.actor_id, log.actor_name, log.actor_role) == ("teacher_002", "张老师", "teacher")
    db.close()


def test_unmapped_teacher_has_empty_scope_and_cannot_enumerate(arbitration_context: ArbitrationContext):
    headers = _auth_headers("teacher", user_id="teacher_unmapped", name="未分配教师")
    listing = arbitration_context.client.get("/api/v1/teacher-arbitrations", headers=headers)
    assert listing.status_code == 200
    assert listing.json() == []
    response = arbitration_context.client.post(
        f"/api/v1/teacher-arbitration/{arbitration_context.own_run_id}/decision",
        headers=headers,
        json=_decision_payload("q014-own", "approve", "q020-unmapped-request-0001"),
    )
    assert response.status_code == 404


def test_student_rejection_does_not_change_agent_or_create_decision_audit(
    arbitration_context: ArbitrationContext,
    student_headers: dict[str, str],
):
    response = arbitration_context.client.post(
        f"/api/v1/teacher-arbitration/{arbitration_context.own_run_id}/decision",
        headers=student_headers,
        json=_decision_payload("q014-own", "reject", "q020-student-request-0001"),
    )
    assert response.status_code == 403
    db = arbitration_context.session_factory()
    run = db.query(AgentRun).filter(AgentRun.id == arbitration_context.own_run_id).one()
    assert (run.status, run.current_node) == ("pending_review", "TeacherArbitration")
    assert db.query(AuditLog).filter(AuditLog.action == "teacher_arbitration_decision").count() == 0
    db.close()


def test_invalid_decision_is_rejected_before_state_change(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
):
    response = arbitration_context.client.post(
        f"/api/v1/teacher-arbitration/{arbitration_context.own_run_id}/decision",
        headers=teacher_headers,
        json=_decision_payload("q014-own", "publish", "q020-invalid-request-0001"),
    )
    assert response.status_code == 400
    db = arbitration_context.session_factory()
    run = db.query(AgentRun).filter(AgentRun.id == arbitration_context.own_run_id).one()
    assert run.status == "pending_review"
    db.close()


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("GET", "/api/v1/tasks", None),
        ("POST", "/api/v1/tasks", {"title": "不应由教师创建"}),
        ("GET", "/api/v1/review-items", None),
        ("POST", "/api/v1/review-items/1/approve", {"comment": "不应批准"}),
        ("POST", "/api/v1/review-items/1/reject", {"comment": "不应驳回"}),
    ],
)
def test_unscoped_global_governance_operations_are_admin_only(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
    method: str,
    path: str,
    payload: dict[str, str] | None,
):
    response = arbitration_context.client.request(method, path, headers=teacher_headers, json=payload)
    assert response.status_code == 403


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("GET", "/api/v1/tasks", None),
        ("POST", "/api/v1/tasks", {"title": "管理员治理任务"}),
        ("GET", "/api/v1/review-items", None),
        ("POST", "/api/v1/review-items/1/approve", {"comment": "管理员批准"}),
        ("POST", "/api/v1/review-items/1/reject", {"comment": "管理员驳回"}),
    ],
)
def test_admin_keeps_global_governance_compatibility(
    arbitration_context: ArbitrationContext,
    admin_headers: dict[str, str],
    method: str,
    path: str,
    payload: dict[str, str] | None,
):
    response = arbitration_context.client.request(method, path, headers=admin_headers, json=payload)
    assert response.status_code not in {401, 403}


def test_frontend_does_not_turn_auth_failure_into_writable_fallback():
    source = Path("frontend/src/views/TeachingDecisionCenter.vue").read_text(encoding="utf-8")
    assert "const tasks = ref<ArbitrationTask[]>([]);" in source
    assert "tasks.value = fallbackTasks" not in source
    assert "已展示本地仲裁演示队列" not in source


def test_q020_teacher_list_exposes_current_arbitration_item_id(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
):
    response = arbitration_context.client.get("/api/v1/teacher-arbitrations", headers=teacher_headers)
    assert response.status_code == 200
    own = next(item for item in response.json() if item["agent_run_id"] == arbitration_context.own_run_id)
    assert own["arbitration_item_id"] == "arb-q014-own-1-0"


def test_q020_repeated_revise_same_request_has_one_side_effect(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    def reenter_pending(state):
        arbitration = create_teacher_arbitration_state(state)
        return {
            **state,
            "status": "pending_review",
            "current_node": "TeacherArbitration",
            "teacher_arbitration_result": arbitration,
        }

    monkeypatch.setattr("app.agents.graph.continue_after_teacher_arbitration", reenter_pending)
    path = f"/api/v1/teacher-arbitration/{arbitration_context.own_run_id}/decision"
    payload = {
        "decision": "revise",
        "teacher_comment": "Q020单次修订",
        "revised_content": "仅保留Python循环课程内容",
        "suggested_action": "revise",
        "arbitration_item_id": "arb-q014-own-1-0",
        "decision_request_id": "q020-stable-request-0001",
    }

    first = arbitration_context.client.post(path, headers=teacher_headers, json=payload)
    second = arbitration_context.client.post(path, headers=teacher_headers, json=payload)

    assert first.status_code == 200
    assert second.status_code == 409
    db = arbitration_context.session_factory()
    run = db.query(AgentRun).filter(AgentRun.id == arbitration_context.own_run_id).one()
    state = loads(run.state, {})
    assert state["teacher_revision_count"] == 1
    assert len(state["teacher_decision_log"]) == 1
    assert db.query(AuditLog).filter(AuditLog.action == "teacher_arbitration_decision").count() == 1
    db.close()


def test_q020_concurrent_same_request_has_one_side_effect(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    def reenter_pending(state):
        arbitration = create_teacher_arbitration_state(state)
        return {
            **state,
            "status": "pending_review",
            "current_node": "TeacherArbitration",
            "teacher_arbitration_result": arbitration,
        }

    monkeypatch.setattr("app.agents.graph.continue_after_teacher_arbitration", reenter_pending)
    path = f"/api/v1/teacher-arbitration/{arbitration_context.own_run_id}/decision"
    payload = {
        "decision": "revise",
        "teacher_comment": "Q020并发修订",
        "revised_content": "仅保留Python循环课程内容",
        "suggested_action": "revise",
        "arbitration_item_id": "arb-q014-own-1-0",
        "decision_request_id": "q020-concurrent-request-0001",
    }

    def submit():
        return arbitration_context.client.post(path, headers=teacher_headers, json=payload).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = sorted(executor.map(lambda _: submit(), range(2)))

    assert statuses == [200, 409]
    db = arbitration_context.session_factory()
    run = db.query(AgentRun).filter(AgentRun.id == arbitration_context.own_run_id).one()
    state = loads(run.state, {})
    assert state["teacher_revision_count"] == 1
    assert len(state["teacher_decision_log"]) == 1
    assert db.query(AuditLog).filter(AuditLog.action == "teacher_arbitration_decision").count() == 1
    db.close()


def test_q020_old_item_with_new_key_is_rejected_without_second_write(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    def reenter_pending(state):
        arbitration = create_teacher_arbitration_state(state)
        return {
            **state,
            "status": "pending_review",
            "current_node": "TeacherArbitration",
            "teacher_arbitration_result": arbitration,
        }

    monkeypatch.setattr("app.agents.graph.continue_after_teacher_arbitration", reenter_pending)
    path = f"/api/v1/teacher-arbitration/{arbitration_context.own_run_id}/decision"
    base = {
        "decision": "revise",
        "teacher_comment": "Q020旧item测试",
        "revised_content": "仅保留Python循环课程内容",
        "suggested_action": "revise",
        "arbitration_item_id": "arb-q014-own-1-0",
    }
    first = arbitration_context.client.post(
        path,
        headers=teacher_headers,
        json={**base, "decision_request_id": "q020-old-item-request-0001"},
    )
    stale = arbitration_context.client.post(
        path,
        headers=teacher_headers,
        json={**base, "decision_request_id": "q020-old-item-request-0002"},
    )

    assert first.status_code == 200
    assert stale.status_code == 409
    db = arbitration_context.session_factory()
    run = db.query(AgentRun).filter(AgentRun.id == arbitration_context.own_run_id).one()
    assert loads(run.state, {})["teacher_revision_count"] == 1
    assert db.query(AuditLog).filter(AuditLog.action == "teacher_arbitration_decision").count() == 1
    db.close()


def test_q020_decision_requires_item_and_idempotency_key(
    arbitration_context: ArbitrationContext,
    teacher_headers: dict[str, str],
):
    response = arbitration_context.client.post(
        f"/api/v1/teacher-arbitration/{arbitration_context.own_run_id}/decision",
        headers=teacher_headers,
        json={"decision": "revise"},
    )
    assert response.status_code == 422


def test_q020_frontend_locks_submission_reuses_key_and_removes_processed_item():
    source = Path("frontend/src/views/TeachingDecisionCenter.vue").read_text(encoding="utf-8")
    assert "decisionRequestIds" in source
    assert "crypto.randomUUID" in source
    assert "submitting[task.id] = true" in source
    assert "submitting[task.id] || task.status !== 'pending'" in source
    assert "tasks.value.splice" in source
    assert "arbitration_item_id" in source
    assert "decision_request_id" in source


def test_q022_frontend_uses_item_key_and_requires_manual_refresh_after_success():
    source = Path("frontend/src/views/TeachingDecisionCenter.vue").read_text(encoding="utf-8")
    assert ':key="`${task.id}:${task.arbitration_item_id}`"' in source
    assert "const pageFrozen = ref(false);" in source
    assert "const decisionInFlight = ref(false);" in source
    assert "if (decisionInFlight.value || pageFrozen.value) return;" in source
    assert "decisionInFlight.value = true;" in source
    assert "pageFrozen.value = true;" in source
    assert "本次操作已完成，请手动刷新后继续" in source
    assert "async function refreshQueue()" in source
    assert "@click=\"refreshQueue\"" in source
    assert "decisionInFlight || pageFrozen" in source
    assert '@click.stop.prevent="decide(task, \'revise\')"' in source
