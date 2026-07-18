from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routers import knowledge_base, resources
from app.api.routers.auth import _sign_jwt
from app.db.session import Base, get_db
from app.main import app
from app.models import Course, GeneratedResource, LearningPath, StudentProfile, SystemLog
from app.services.business_event_service import event_to_dict
from app.services.json_utils import dumps


@dataclass
class SharedWriteContext:
    client: TestClient
    session_factory: sessionmaker
    own_course_id: int
    other_course_id: int
    own_profile_id: int
    other_profile_id: int
    own_resource_id: int
    other_resource_id: int


def _auth_headers(role: str, *, user_id: str | None = None, name: str | None = None) -> dict[str, str]:
    now = int(time.time())
    defaults = {
        "student": ("student_001", "李明"),
        "teacher": ("teacher_001", "王老师"),
        "admin": ("admin_001", "管理员"),
    }
    principal, display_name = defaults[role]
    token = _sign_jwt(
        {
            "username": principal,
            "role": role,
            "name": name or display_name,
            "display_name": name or display_name,
            "user_id": user_id or principal,
            "iat": now,
            "exp": now + 3600,
        }
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def shared_write_context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> SharedWriteContext:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = testing_session()
    own_course = Course(title="Python 程序设计", subject="程序设计", teacher_name="王老师")
    other_course = Course(title="人工智能导论", subject="人工智能", teacher_name="张老师")
    db.add_all([own_course, other_course])
    db.flush()
    own_profile = StudentProfile(
        student_name="李明",
        owner_user_id="student_001",
        demo_profile_key="demo-basic",
        course_id=own_course.id,
        current_level="基础薄弱",
        learning_goal="掌握循环结构",
        weak_points=dumps(["while 循环"]),
        learning_preference="代码案例",
        profile_json=dumps({"user_id": "student_001", "student_name": "李明", "weak_points": ["while 循环"]}),
    )
    other_profile = StudentProfile(
        student_name="王五",
        owner_user_id="demo_student_wangwu",
        demo_profile_key="demo-wangwu",
        course_id=other_course.id,
        current_level="中等",
        learning_goal="掌握人工智能基础",
        weak_points=dumps(["搜索算法"]),
        learning_preference="图解",
        profile_json=dumps({"user_id": "demo_student_wangwu", "student_name": "王五"}),
    )
    db.add_all([own_profile, other_profile])
    db.flush()
    own_resource = GeneratedResource(
        course_id=own_course.id,
        student_profile_id=own_profile.id,
        resource_type="讲义",
        title="循环结构讲义",
        content="while循环",
        source_agent="fixture",
    )
    other_resource = GeneratedResource(
        course_id=other_course.id,
        student_profile_id=other_profile.id,
        resource_type="讲义",
        title="搜索算法讲义",
        content="A*算法",
        source_agent="fixture",
    )
    db.add_all([own_resource, other_resource])
    db.flush()
    db.add(LearningPath(student_profile_id=own_profile.id, course_id=own_course.id, path_json=dumps({"stages": []})))
    db.commit()
    ids = (
        own_course.id,
        other_course.id,
        own_profile.id,
        other_profile.id,
        own_resource.id,
        other_resource.id,
    )
    db.close()

    upload_root = tmp_path / "uploads"
    monkeypatch.setattr(type(knowledge_base.settings), "path_from_root", lambda self, relative: upload_root)
    monkeypatch.setattr(knowledge_base.vector_store, "add_chunks", lambda *args, **kwargs: len(args[3]) if len(args) > 3 else 0)
    monkeypatch.setattr(resources, "build_multimodal_resources", lambda weak_points: [])

    def override_get_db():
        test_db = testing_session()
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield SharedWriteContext(client, testing_session, *ids)
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


def _anonymous_write_cases(context: SharedWriteContext) -> list[tuple[str, str, dict[str, Any] | None]]:
    return [
        ("POST", "/api/v1/courses", {"title": "匿名课程"}),
        ("PUT", f"/api/v1/courses/{context.own_course_id}", {"title": "匿名修改"}),
        ("DELETE", f"/api/v1/courses/{context.own_course_id}", None),
        ("POST", "/api/v1/knowledge-base/upload", None),
        ("POST", "/api/v1/resources/generate", {"course_id": context.own_course_id, "student_profile_id": context.own_profile_id}),
        ("POST", "/api/v1/resources/generate-pack", {"courseId": context.own_course_id, "studentId": "student_001"}),
        ("POST", "/api/v1/resources/courseware-outline", {"course": "Python 程序设计"}),
        ("POST", f"/api/v1/resources/{context.own_resource_id}/rate", {"rating": 5}),
        ("POST", "/api/v1/events", {"event_type": "forged", "title": "伪造", "description": "伪造", "actor_role": "admin"}),
        ("POST", "/api/v1/events/resource-package", {"course_id": context.own_course_id, "student_profile_id": context.own_profile_id}),
        ("POST", "/api/v1/events/add-resource-to-path", {"package_id": "pkg-test", "course_id": context.own_course_id, "student_profile_id": context.own_profile_id}),
        ("POST", "/api/v1/events/assign-task", {"course_id": context.own_course_id, "student_profile_id": context.own_profile_id}),
        ("POST", "/api/v1/events/demo-quiz", {"course_id": context.own_course_id, "student_profile_id": context.own_profile_id}),
        ("POST", "/api/v1/events/admin-review", {"event_type": "ignored", "title": "审核", "description": "审核", "actor_role": "admin"}),
    ]


@pytest.mark.parametrize("case_index", range(14))
def test_q018_all_shared_writes_require_authentication(shared_write_context: SharedWriteContext, case_index: int):
    method, path, payload = _anonymous_write_cases(shared_write_context)[case_index]
    if path == "/api/v1/knowledge-base/upload":
        response = shared_write_context.client.post(
            f"{path}?course_id={shared_write_context.own_course_id}",
            files={"file": ("lesson.txt", b"while loop", "text/plain")},
        )
    else:
        response = shared_write_context.client.request(method, path, json=payload)
    assert response.status_code == 401, f"{method} {path}: {response.status_code} {response.text[:200]}"


@pytest.mark.parametrize(
    ("method", "path_factory", "payload_factory"),
    [
        ("POST", lambda c: "/api/v1/courses", lambda c: {"title": "学生课程"}),
        ("POST", lambda c: "/api/v1/resources/generate", lambda c: {"course_id": c.own_course_id, "student_profile_id": c.own_profile_id}),
        ("POST", lambda c: "/api/v1/resources/generate-pack", lambda c: {"courseId": c.own_course_id, "studentId": "student_001"}),
        ("POST", lambda c: "/api/v1/resources/courseware-outline", lambda c: {"course": "Python 程序设计"}),
        ("POST", lambda c: "/api/v1/events", lambda c: {"event_type": "forged", "title": "伪造", "description": "伪造"}),
        ("POST", lambda c: "/api/v1/events/resource-package", lambda c: {"course_id": c.own_course_id, "student_profile_id": c.own_profile_id}),
        ("POST", lambda c: "/api/v1/events/assign-task", lambda c: {"course_id": c.own_course_id, "student_profile_id": c.own_profile_id}),
        ("POST", lambda c: "/api/v1/events/admin-review", lambda c: {"event_type": "x", "title": "x", "description": "x"}),
    ],
)
def test_q018_student_cannot_invoke_staff_or_admin_writes(
    shared_write_context: SharedWriteContext,
    student_headers: dict[str, str],
    method,
    path_factory,
    payload_factory,
):
    response = shared_write_context.client.request(
        method,
        path_factory(shared_write_context),
        headers=student_headers,
        json=payload_factory(shared_write_context),
    )
    assert response.status_code == 403


def test_q018_teacher_course_writes_are_scoped_and_admin_remains_global(
    shared_write_context: SharedWriteContext,
    teacher_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    client = shared_write_context.client
    own_update = client.put(
        f"/api/v1/courses/{shared_write_context.own_course_id}",
        headers=teacher_headers,
        json={"title": "Python 程序设计", "description": "Q018作用域测试"},
    )
    cross_update = client.put(
        f"/api/v1/courses/{shared_write_context.other_course_id}",
        headers=teacher_headers,
        json={"title": "越权修改"},
    )
    admin_update = client.put(
        f"/api/v1/courses/{shared_write_context.other_course_id}",
        headers=admin_headers,
        json={"title": "人工智能导论", "description": "管理员合法修改"},
    )
    assert own_update.status_code == 200
    assert cross_update.status_code == 404
    assert admin_update.status_code == 200


def test_q018_teacher_cannot_upload_or_generate_for_cross_course(
    shared_write_context: SharedWriteContext,
    teacher_headers: dict[str, str],
):
    upload = shared_write_context.client.post(
        f"/api/v1/knowledge-base/upload?course_id={shared_write_context.other_course_id}",
        headers=teacher_headers,
        files={"file": ("cross.txt", b"cross course", "text/plain")},
    )
    generate = shared_write_context.client.post(
        "/api/v1/resources/generate",
        headers=teacher_headers,
        json={"course_id": shared_write_context.other_course_id, "student_profile_id": shared_write_context.other_profile_id},
    )
    assign = shared_write_context.client.post(
        "/api/v1/events/assign-task",
        headers=teacher_headers,
        json={"course_id": shared_write_context.other_course_id, "student_profile_id": shared_write_context.other_profile_id},
    )
    assert upload.status_code == 404
    assert generate.status_code == 404
    assert assign.status_code == 404


def test_q018_student_object_writes_are_limited_to_self(
    shared_write_context: SharedWriteContext,
    student_headers: dict[str, str],
):
    own_rating = shared_write_context.client.post(
        f"/api/v1/resources/{shared_write_context.own_resource_id}/rate",
        headers=student_headers,
        json={"rating": 4},
    )
    other_rating = shared_write_context.client.post(
        f"/api/v1/resources/{shared_write_context.other_resource_id}/rate",
        headers=student_headers,
        json={"rating": 1},
    )
    own_quiz = shared_write_context.client.post(
        "/api/v1/events/demo-quiz",
        headers=student_headers,
        json={"course_id": shared_write_context.own_course_id, "student_profile_id": shared_write_context.own_profile_id},
    )
    other_quiz = shared_write_context.client.post(
        "/api/v1/events/demo-quiz",
        headers=student_headers,
        json={"course_id": shared_write_context.other_course_id, "student_profile_id": shared_write_context.other_profile_id},
    )
    assert own_rating.status_code == 200
    assert other_rating.status_code == 404
    assert own_quiz.status_code == 200
    assert other_quiz.status_code == 404


def test_q018_forged_actor_fields_are_ignored_and_admin_review_is_admin_only(
    shared_write_context: SharedWriteContext,
    teacher_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    denied = shared_write_context.client.post(
        "/api/v1/events/admin-review",
        headers=teacher_headers,
        json={
            "event_type": "forged",
            "title": "教师伪造管理员",
            "description": "不得写入",
            "actor_id": "admin_001",
            "actor_name": "管理员",
            "actor_role": "admin",
        },
    )
    accepted = shared_write_context.client.post(
        "/api/v1/events/admin-review",
        headers=admin_headers,
        json={
            "event_type": "forged",
            "title": "管理员审核",
            "description": "合法审核",
            "actor_id": "forged_actor",
            "actor_name": "伪造姓名",
            "actor_role": "student",
        },
    )
    assert denied.status_code == 403
    assert accepted.status_code == 200
    db = shared_write_context.session_factory()
    try:
        row = db.query(SystemLog).filter(SystemLog.id == accepted.json()["event_id"]).one()
        event = event_to_dict(row)
        assert event["actor_id"] == "admin_001"
        assert event["actor_name"] == "管理员"
        assert event["actor_role"] == "admin"
    finally:
        db.close()


def test_q018_existing_governance_and_content_review_guards_remain_active(
    shared_write_context: SharedWriteContext,
    student_headers: dict[str, str],
    teacher_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    assert shared_write_context.client.post("/api/v1/tasks", json={"title": "匿名"}).status_code == 401
    assert shared_write_context.client.post("/api/v1/tasks", headers=teacher_headers, json={"title": "教师"}).status_code == 403
    assert shared_write_context.client.post("/api/v1/tasks", headers=admin_headers, json={"title": "管理员"}).status_code == 200
    payload = {"content": "循环必须有终止条件", "courseId": shared_write_context.own_course_id}
    assert shared_write_context.client.post("/api/v1/content-review/check", json=payload).status_code == 401
    assert shared_write_context.client.post("/api/v1/content-review/check", headers=student_headers, json=payload).status_code == 403
    assert shared_write_context.client.post("/api/v1/content-review/check", headers=teacher_headers, json=payload).status_code == 200


def test_q018_teacher_and_admin_keep_legitimate_course_and_knowledge_writes(
    shared_write_context: SharedWriteContext,
    teacher_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    created = shared_write_context.client.post(
        "/api/v1/courses",
        headers=teacher_headers,
        json={"title": "Q018教师自建课程", "teacher_name": "伪造教师"},
    )
    uploaded = shared_write_context.client.post(
        f"/api/v1/knowledge-base/upload?course_id={shared_write_context.own_course_id}",
        headers=teacher_headers,
        files={"file": ("lesson.txt", b"while loop", "text/plain")},
    )
    admin_cross_upload = shared_write_context.client.post(
        f"/api/v1/knowledge-base/upload?course_id={shared_write_context.other_course_id}",
        headers=admin_headers,
        files={"file": ("admin.txt", b"ai lesson", "text/plain")},
    )
    assert created.status_code == 200
    assert created.json()["teacher_name"] == "王老师"
    assert uploaded.status_code == 200
    assert admin_cross_upload.status_code == 200


def test_q018_valid_resource_generation_and_courseware_roles_are_preserved(
    shared_write_context: SharedWriteContext,
    teacher_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    generated = shared_write_context.client.post(
        "/api/v1/resources/generate",
        headers=teacher_headers,
        json={"course_id": shared_write_context.own_course_id, "student_profile_id": shared_write_context.own_profile_id},
    )
    packed = shared_write_context.client.post(
        "/api/v1/resources/generate-pack",
        headers=teacher_headers,
        json={"courseId": shared_write_context.own_course_id, "studentId": "student_001", "courseName": "Python 程序设计"},
    )
    outlined = shared_write_context.client.post(
        "/api/v1/resources/courseware-outline",
        headers=teacher_headers,
        json={"course": "Python 程序设计"},
    )
    admin_cross = shared_write_context.client.post(
        "/api/v1/resources/generate",
        headers=admin_headers,
        json={"course_id": shared_write_context.other_course_id, "student_profile_id": shared_write_context.other_profile_id},
    )
    assert generated.status_code == 200
    assert packed.status_code == 200
    assert outlined.status_code == 200
    assert admin_cross.status_code == 200


def test_q018_event_actor_comes_from_jwt_for_teacher_and_student_flows(
    shared_write_context: SharedWriteContext,
    teacher_headers: dict[str, str],
    student_headers: dict[str, str],
):
    assigned = shared_write_context.client.post(
        "/api/v1/events/assign-task",
        headers=teacher_headers,
        json={
            "course_id": shared_write_context.own_course_id,
            "student_profile_id": shared_write_context.own_profile_id,
            "actor_name": "管理员",
            "actor_role": "admin",
        },
    )
    quiz = shared_write_context.client.post(
        "/api/v1/events/demo-quiz",
        headers=student_headers,
        json={
            "course_id": shared_write_context.own_course_id,
            "student_profile_id": shared_write_context.own_profile_id,
            "actor_name": "管理员",
            "actor_role": "admin",
        },
    )
    assert assigned.status_code == 200
    assert quiz.status_code == 200
    db = shared_write_context.session_factory()
    try:
        events = [event_to_dict(item) for item in db.query(SystemLog).filter(SystemLog.type == "business_event").all()]
        task_event = next(item for item in events if item["event_type"] == "task_assigned")
        quiz_event = next(item for item in events if item["event_type"] == "quiz_completed")
        assert (task_event["actor_id"], task_event["actor_name"], task_event["actor_role"]) == (
            "teacher_001",
            "王老师",
            "teacher",
        )
        assert (quiz_event["actor_id"], quiz_event["actor_name"], quiz_event["actor_role"]) == (
            "student_001",
            "李明",
            "student",
        )
    finally:
        db.close()


def test_q018_old_ids_and_course_profile_mismatch_are_hidden_without_side_effect(
    shared_write_context: SharedWriteContext,
    teacher_headers: dict[str, str],
):
    db = shared_write_context.session_factory()
    try:
        before_resources = db.query(GeneratedResource).count()
        before_events = db.query(SystemLog).count()
    finally:
        db.close()
    missing = shared_write_context.client.post(
        "/api/v1/events/assign-task",
        headers=teacher_headers,
        json={"course_id": 999999, "student_profile_id": 999999},
    )
    mismatch = shared_write_context.client.post(
        "/api/v1/resources/generate",
        headers=teacher_headers,
        json={"course_id": shared_write_context.own_course_id, "student_profile_id": shared_write_context.other_profile_id},
    )
    assert missing.status_code == 404
    assert mismatch.status_code == 404
    db = shared_write_context.session_factory()
    try:
        assert db.query(GeneratedResource).count() == before_resources
        assert db.query(SystemLog).count() == before_events
    finally:
        db.close()


def test_q018_content_review_enforces_teacher_course_scope(
    shared_write_context: SharedWriteContext,
    teacher_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    own = shared_write_context.client.post(
        "/api/v1/content-review/check",
        headers=teacher_headers,
        json={"content": "while循环必须有终止条件", "courseId": shared_write_context.own_course_id},
    )
    cross = shared_write_context.client.post(
        "/api/v1/content-review/check",
        headers=teacher_headers,
        json={"content": "人工智能导论", "courseId": shared_write_context.other_course_id},
    )
    admin_cross = shared_write_context.client.post(
        "/api/v1/content-review/check",
        headers=admin_headers,
        json={"content": "人工智能导论", "courseId": shared_write_context.other_course_id},
    )
    assert own.status_code == 200
    assert cross.status_code == 404
    assert admin_cross.status_code == 200


def test_q018_resource_package_and_task_replays_are_rejected_without_duplicate_writes(
    shared_write_context: SharedWriteContext,
    teacher_headers: dict[str, str],
):
    package_payload = {
        "course_id": shared_write_context.own_course_id,
        "student_profile_id": shared_write_context.own_profile_id,
    }
    first_package = shared_write_context.client.post(
        "/api/v1/events/resource-package",
        headers=teacher_headers,
        json=package_payload,
    )
    repeated_package = shared_write_context.client.post(
        "/api/v1/events/resource-package",
        headers=teacher_headers,
        json=package_payload,
    )
    task_payload = {
        "course_id": shared_write_context.own_course_id,
        "student_profile_id": shared_write_context.own_profile_id,
        "weak_point": "while 循环",
        "task_type": "完成练习",
    }
    first_task = shared_write_context.client.post(
        "/api/v1/events/assign-task",
        headers=teacher_headers,
        json=task_payload,
    )
    repeated_task = shared_write_context.client.post(
        "/api/v1/events/assign-task",
        headers=teacher_headers,
        json=task_payload,
    )
    assert first_package.status_code == 200
    assert repeated_package.status_code == 409
    assert first_task.status_code == 200
    assert repeated_task.status_code == 409
    db = shared_write_context.session_factory()
    try:
        package_id = first_package.json()["package_id"]
        task_id = first_task.json()["task"]["task_id"]
        assert db.query(SystemLog).filter(SystemLog.related_id == package_id).count() == 1
        assert db.query(SystemLog).filter(SystemLog.related_id == task_id).count() == 2
    finally:
        db.close()


def test_q018_add_to_path_requires_real_package_bound_to_same_student_and_course(
    shared_write_context: SharedWriteContext,
    teacher_headers: dict[str, str],
):
    missing = shared_write_context.client.post(
        "/api/v1/events/add-resource-to-path",
        headers=teacher_headers,
        json={
            "package_id": "pkg-does-not-exist",
            "course_id": shared_write_context.own_course_id,
            "student_profile_id": shared_write_context.own_profile_id,
        },
    )
    package = shared_write_context.client.post(
        "/api/v1/events/resource-package",
        headers=teacher_headers,
        json={
            "course_id": shared_write_context.own_course_id,
            "student_profile_id": shared_write_context.own_profile_id,
        },
    )
    accepted = shared_write_context.client.post(
        "/api/v1/events/add-resource-to-path",
        headers=teacher_headers,
        json={
            "package_id": package.json()["package_id"],
            "course_id": shared_write_context.own_course_id,
            "student_profile_id": shared_write_context.own_profile_id,
        },
    )
    assert missing.status_code == 404
    assert package.status_code == 200
    assert accepted.status_code == 200
