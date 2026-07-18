from __future__ import annotations

import time
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routers.auth import _sign_jwt
from app.db.session import Base, get_db
from app.main import app
from app.models import Course, StudentProfile
from app.services.json_utils import dumps


@dataclass
class ProfileTestContext:
    client: TestClient
    session_factory: sessionmaker
    course_id: int
    own_profile_id: int
    other_profile_id: int


def _auth_headers(
    role: str,
    user_id: str,
    name: str,
    *,
    student_id: str | None = None,
) -> dict[str, str]:
    now = int(time.time())
    token = _sign_jwt(
        {
            "username": f"test_{role}",
            "role": role,
            "name": name,
            "display_name": name,
            "user_id": user_id,
            "student_id": student_id,
            "iat": now,
            "exp": now + 3600,
        }
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def profile_context() -> ProfileTestContext:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = testing_session()
    course = Course(title="Python 程序设计", subject="程序设计", teacher_name="王老师")
    db.add(course)
    db.flush()

    own_profile = StudentProfile(
        student_name="李明",
        course_id=course.id,
        current_level="基础薄弱",
        learning_goal="补齐循环结构",
        weak_points=dumps(["while 循环"]),
        learning_preference="代码案例",
        profile_json=dumps({"user_id": "student_001", "student_name": "李明"}),
    )
    other_profile = StudentProfile(
        student_name="张三",
        course_id=course.id,
        current_level="中等",
        learning_goal="完成课程项目",
        weak_points=dumps(["异常处理"]),
        learning_preference="项目案例",
        profile_json=dumps({"user_id": "demo_student_zhangsan", "student_name": "张三"}),
    )
    if hasattr(StudentProfile, "owner_user_id"):
        own_profile.owner_user_id = "student_001"
        other_profile.owner_user_id = "demo_student_zhangsan"
    if hasattr(StudentProfile, "demo_profile_key"):
        own_profile.demo_profile_key = "demo-basic"
        other_profile.demo_profile_key = "demo-python-crawler-zhangsan"

    db.add_all([own_profile, other_profile])
    db.commit()
    db.refresh(course)
    db.refresh(own_profile)
    db.refresh(other_profile)
    db.close()

    def override_get_db():
        test_db = testing_session()
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield ProfileTestContext(
            client=client,
            session_factory=testing_session,
            course_id=course.id,
            own_profile_id=own_profile.id,
            other_profile_id=other_profile.id,
        )
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def student_headers() -> dict[str, str]:
    return _auth_headers("student", "student_001", "李明", student_id="1")


@pytest.fixture()
def teacher_headers() -> dict[str, str]:
    return _auth_headers("teacher", "teacher_001", "王老师")


@pytest.fixture()
def admin_headers() -> dict[str, str]:
    return _auth_headers("admin", "admin_001", "管理员")


def test_auth_01_anonymous_profile_list_returns_401(profile_context: ProfileTestContext):
    response = profile_context.client.get("/api/v1/profiles")
    assert response.status_code == 401


def test_auth_02_anonymous_profile_detail_returns_401(profile_context: ProfileTestContext):
    response = profile_context.client.get(f"/api/v1/profiles/{profile_context.own_profile_id}")
    assert response.status_code == 401


def test_auth_03_student_reads_own_profile(
    profile_context: ProfileTestContext,
    student_headers: dict[str, str],
):
    response = profile_context.client.get(
        f"/api/v1/profiles/{profile_context.own_profile_id}",
        headers=student_headers,
    )
    assert response.status_code == 200
    assert response.json()["student_name"] == "李明"


def test_auth_04_student_cannot_read_other_profile(
    profile_context: ProfileTestContext,
    student_headers: dict[str, str],
):
    response = profile_context.client.get(
        f"/api/v1/profiles/{profile_context.other_profile_id}",
        headers=student_headers,
    )
    assert response.status_code == 404


def test_auth_05_student_cannot_list_profiles(
    profile_context: ProfileTestContext,
    student_headers: dict[str, str],
):
    response = profile_context.client.get("/api/v1/profiles", headers=student_headers)
    assert response.status_code == 403


def test_auth_06_student_cannot_update_other_profile(
    profile_context: ProfileTestContext,
    student_headers: dict[str, str],
):
    response = profile_context.client.put(
        f"/api/v1/profiles/{profile_context.other_profile_id}/update",
        headers=student_headers,
        json={"learning_goal": "越权修改"},
    )
    assert response.status_code == 404


def test_auth_07_spoofed_demo_header_cannot_switch_student(
    profile_context: ProfileTestContext,
    student_headers: dict[str, str],
):
    response = profile_context.client.get(
        "/api/v1/profiles/me",
        headers={**student_headers, "X-Demo-User-Id": "demo_student_zhangsan"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == profile_context.own_profile_id
    assert response.json()["student_name"] == "李明"


def test_auth_08_spoofed_query_cannot_switch_student(
    profile_context: ProfileTestContext,
    student_headers: dict[str, str],
):
    response = profile_context.client.get(
        f"/api/v1/profiles/me?student_id={profile_context.other_profile_id}",
        headers=student_headers,
    )
    assert response.status_code == 200
    assert response.json()["id"] == profile_context.own_profile_id


def test_auth_09_teacher_can_list_profiles(
    profile_context: ProfileTestContext,
    teacher_headers: dict[str, str],
):
    response = profile_context.client.get("/api/v1/profiles", headers=teacher_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_auth_10_admin_can_update_profile(
    profile_context: ProfileTestContext,
    admin_headers: dict[str, str],
):
    response = profile_context.client.put(
        f"/api/v1/profiles/{profile_context.other_profile_id}/update",
        headers=admin_headers,
        json={"learning_goal": "管理员合法更新"},
    )
    assert response.status_code == 200


def test_auth_11_id_enumeration_does_not_reveal_existence(
    profile_context: ProfileTestContext,
    student_headers: dict[str, str],
):
    existing = profile_context.client.get(
        f"/api/v1/profiles/{profile_context.other_profile_id}",
        headers=student_headers,
    )
    missing = profile_context.client.get(
        "/api/v1/profiles/999999",
        headers=student_headers,
    )
    assert existing.status_code == missing.status_code == 404
    assert existing.json() == missing.json()


def test_auth_12_profiles_me_returns_only_authenticated_student(
    profile_context: ProfileTestContext,
    student_headers: dict[str, str],
):
    response = profile_context.client.get("/api/v1/profiles/me", headers=student_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json()["id"] == profile_context.own_profile_id
    assert response.json()["student_name"] == "李明"


def test_auth_13_invalid_token_returns_401(profile_context: ProfileTestContext):
    response = profile_context.client.get(
        "/api/v1/profiles",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_auth_14_student_cannot_create_profile_for_other_owner(
    profile_context: ProfileTestContext,
    student_headers: dict[str, str],
):
    response = profile_context.client.post(
        "/api/v1/profiles",
        headers={**student_headers, "X-Demo-User-Id": "demo_student_zhangsan"},
        json={
            "course_id": profile_context.course_id,
            "student_name": "张三",
            "user_id": "demo_student_zhangsan",
            "learning_goal": "越权创建",
        },
    )
    assert response.status_code == 200
    db = profile_context.session_factory()
    try:
        created = db.query(StudentProfile).order_by(StudentProfile.id.desc()).first()
        assert created is not None
        assert created.student_name == "李明"
        assert getattr(created, "owner_user_id", None) == "student_001"
    finally:
        db.close()


def test_auth_15_student_cannot_generate_profile_for_other_owner(
    profile_context: ProfileTestContext,
    student_headers: dict[str, str],
):
    response = profile_context.client.post(
        "/api/v1/profiles/generate",
        headers=student_headers,
        json={
            "course_id": profile_context.course_id,
            "student_name": "张三",
            "user_id": "demo_student_zhangsan",
            "learning_goal": "越权生成",
        },
    )
    assert response.status_code == 200
    db = profile_context.session_factory()
    try:
        created = db.query(StudentProfile).order_by(StudentProfile.id.desc()).first()
        assert created is not None
        assert created.student_name == "李明"
        assert getattr(created, "owner_user_id", None) == "student_001"
    finally:
        db.close()


def test_anonymous_demo_users_returns_401(profile_context: ProfileTestContext):
    response = profile_context.client.get("/api/v1/profiles/demo-users")
    assert response.status_code == 401


def test_student_cannot_visualize_other_profile(
    profile_context: ProfileTestContext,
    student_headers: dict[str, str],
):
    response = profile_context.client.get(
        f"/api/v1/profiles/{profile_context.other_profile_id}/visualization",
        headers=student_headers,
    )
    assert response.status_code == 404


def test_student_cannot_update_own_advanced_profile_fields(
    profile_context: ProfileTestContext,
    student_headers: dict[str, str],
):
    response = profile_context.client.put(
        f"/api/v1/profiles/{profile_context.own_profile_id}/update",
        headers=student_headers,
        json={"risk_level": "low"},
    )
    assert response.status_code == 403


def test_teacher_generates_zhangsan_without_liming_template_fallback(
    profile_context: ProfileTestContext,
    teacher_headers: dict[str, str],
):
    response = profile_context.client.post(
        "/api/v1/profiles/generate",
        headers=teacher_headers,
        json={
            "course_id": profile_context.course_id,
            "user_id": "demo_student_zhangsan",
            "student_name": "张三",
            "current_level": "中等",
            "learning_goal": "完成课程项目",
            "weak_points": ["异常处理"],
            "learning_preference": "项目案例",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["student_name"] == "张三"
    assert body["owner_user_id"] == "demo_student_zhangsan"
    assert body["demo_profile_key"] == "demo-zhangsan"
    assert body["profile_json"]["student_name"] == "张三"
    assert body["profile_json"]["user_id"] == "demo_student_zhangsan"


def test_teacher_generates_unknown_stable_owner_without_liming_fallback(
    profile_context: ProfileTestContext,
    teacher_headers: dict[str, str],
):
    response = profile_context.client.post(
        "/api/v1/profiles/generate",
        headers=teacher_headers,
        json={
            "course_id": profile_context.course_id,
            "user_id": "student_external_001",
            "student_name": "赵六",
            "current_level": "待评估",
            "learning_goal": "完成基础诊断",
            "weak_points": [],
            "learning_preference": "未确认",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["student_name"] == "赵六"
    assert body["owner_user_id"] == "student_external_001"
    assert body["demo_profile_key"] == "student_external_001"
    assert body["profile_json"]["student_name"] == "赵六"
    assert body["profile_json"]["user_id"] == "student_external_001"
