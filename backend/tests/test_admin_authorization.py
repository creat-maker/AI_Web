from __future__ import annotations

import io
import json
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routers import admin_reports, admin_users
from app.api.routers.auth import _sign_jwt
from app.db.session import Base, get_db
from app.main import app
from app.models import AuditLog, Course, LearningReport, StudentProfile
from app.services.json_utils import dumps


@dataclass
class AdminTestContext:
    client: TestClient
    session_factory: sessionmaker
    state_path: Path
    report_id: int
    report_file: Path


class SecretHeaders(dict[str, str]):
    def __repr__(self) -> str:
        return "{'Authorization': 'Bearer [REDACTED]'}"


def _auth_headers(role: str, *, username: str | None = None) -> dict[str, str]:
    now = int(time.time())
    names = {"student": "李明", "teacher": "王老师", "admin": "管理员"}
    user_ids = {"student": "student_001", "teacher": "teacher_001", "admin": "admin_001"}
    token = _sign_jwt(
        {
            "username": username or role,
            "role": role,
            "name": names[role],
            "display_name": names[role],
            "user_id": user_ids[role],
            "student_id": "1" if role == "student" else None,
            "iat": now,
            "exp": now + 3600,
        }
    )
    return SecretHeaders({"Authorization": f"Bearer {token}"})


@pytest.fixture()
def admin_context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AdminTestContext:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    report_file = tmp_path / "reports" / "sample-report.docx"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_bytes(b"Q013 isolated report fixture")

    db = testing_session()
    course = Course(title="Python 程序设计", subject="程序设计", teacher_name="王老师")
    db.add(course)
    db.flush()
    profile = StudentProfile(
        student_name="李明",
        course_id=course.id,
        current_level="基础薄弱",
        learning_goal="补齐循环结构",
        weak_points=dumps(["while 循环"]),
        learning_preference="代码案例",
        profile_json=dumps({"user_id": "student_001", "student_name": "李明"}),
    )
    if hasattr(StudentProfile, "owner_user_id"):
        profile.owner_user_id = "student_001"
    if hasattr(StudentProfile, "demo_profile_key"):
        profile.demo_profile_key = "demo-basic"
    db.add(profile)
    db.flush()
    report = LearningReport(
        student_profile_id=profile.id,
        course_id=course.id,
        report_title="Q013 隔离测试报告",
        report_path=str(report_file),
        report_json=dumps({"summary": "隔离测试", "review_status": "待审核"}),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    report_id = report.id
    db.close()

    state_path = tmp_path / "admin_users_state.json"
    monkeypatch.setattr(admin_users, "STATE_PATH", state_path)
    monkeypatch.setattr(
        type(admin_reports.settings),
        "path_from_root",
        lambda self, relative: tmp_path / Path(str(relative)).name,
    )

    def override_get_db():
        test_db = testing_session()
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield AdminTestContext(client, testing_session, state_path, report_id, report_file)
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


def _operation_cases(report_id: int) -> list[tuple[str, str, str, dict[str, Any] | None]]:
    return [
        ("ADMIN-01-users-list", "GET", "/api/v1/admin/users", None),
        ("ADMIN-02-user-status", "PATCH", "/api/v1/admin/users/1/status", {"status": "禁用"}),
        ("ADMIN-03-user-role", "PATCH", "/api/v1/admin/users/1/role", {"role": "teacher"}),
        ("ADMIN-04-reset-password", "POST", "/api/v1/admin/users/1/reset-password", None),
        ("ADMIN-05-roles-list", "GET", "/api/v1/admin/roles", None),
        ("ADMIN-06-role-permissions", "PATCH", "/api/v1/admin/roles/student/permissions", {"permissions": ["学习总览"]}),
        ("ADMIN-07-reports-list", "GET", "/api/v1/admin/reports", None),
        ("ADMIN-08-report-preview", "GET", f"/api/v1/admin/reports/{report_id}/preview", None),
        ("ADMIN-09-report-download", "GET", f"/api/v1/admin/reports/{report_id}/download", None),
        ("ADMIN-10-report-regenerate", "POST", f"/api/v1/admin/reports/{report_id}/regenerate", None),
        ("ADMIN-11-report-monthly", "POST", "/api/v1/admin/reports/monthly", None),
        ("ADMIN-12-report-export", "POST", "/api/v1/admin/reports/export", None),
        ("ADMIN-13-report-status", "PATCH", f"/api/v1/admin/reports/{report_id}/status", {"status": "已通过"}),
        ("ADMIN-14-content-review-queue", "GET", "/api/v1/admin/content-review", None),
        ("ADMIN-15-platform-quality", "GET", "/api/v1/admin/platform-quality", None),
        ("ADMIN-16-dashboard-summary", "GET", "/api/dashboard/summary", None),
        ("ADMIN-17-dashboard-activity", "GET", "/api/dashboard/activity", None),
        ("ADMIN-18-settings", "GET", "/api/v1/settings", None),
        ("ADMIN-19-settings-test", "POST", "/api/v1/settings/test", None),
        ("ADMIN-20-content-check", "POST", "/api/v1/content-review/check", {"content": "递归必须有出口。"}),
        ("ADMIN-21-content-records", "GET", "/api/v1/content-review/records", None),
    ]


ADMIN_ONLY_CASE_INDEXES = [*range(15), 17, 18]


@pytest.mark.parametrize("case_index", range(21))
def test_admin_01_21_anonymous_protected_operation_returns_401(
    admin_context: AdminTestContext,
    case_index: int,
):
    case_name, method, path, payload = _operation_cases(admin_context.report_id)[case_index]
    response = admin_context.client.request(method, path, json=payload)
    assert response.status_code == 401, f"{case_name}: {response.status_code} {response.text[:200]}"


def test_admin_22_demo_status_remains_public_and_sanitized(admin_context: AdminTestContext):
    response = admin_context.client.get("/api/v1/demo-status")
    assert response.status_code == 200
    serialized = json.dumps(response.json(), ensure_ascii=False).lower()
    assert str(Path.cwd()).lower() not in serialized
    assert "api_secret" not in serialized
    assert "access_token" not in serialized


def test_admin_23_student_cannot_list_admin_users(
    admin_context: AdminTestContext,
    student_headers: dict[str, str],
):
    response = admin_context.client.get("/api/v1/admin/users", headers=student_headers)
    assert response.status_code == 403


def test_admin_24_teacher_cannot_list_admin_users(
    admin_context: AdminTestContext,
    teacher_headers: dict[str, str],
):
    response = admin_context.client.get("/api/v1/admin/users", headers=teacher_headers)
    assert response.status_code == 403


def test_admin_25_admin_can_list_users_with_minimal_shape(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
):
    response = admin_context.client.get("/api/v1/admin/users", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()
    assert set(response.json()[0]).isdisjoint({"password", "password_hash", "token", "api_key"})


def test_admin_26_forged_role_header_does_not_grant_access(admin_context: AdminTestContext):
    response = admin_context.client.get(
        "/api/v1/admin/users",
        headers={"X-Role": "admin", "X-User-Role": "admin"},
    )
    assert response.status_code == 401


def test_admin_27_invalid_token_returns_401(admin_context: AdminTestContext):
    response = admin_context.client.get(
        "/api/v1/admin/users",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_admin_28_dashboard_role_matrix(
    admin_context: AdminTestContext,
    student_headers: dict[str, str],
    teacher_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    assert admin_context.client.get("/api/dashboard/summary", headers=student_headers).status_code == 403
    assert admin_context.client.get("/api/dashboard/summary", headers=teacher_headers).status_code == 200
    assert admin_context.client.get("/api/dashboard/summary", headers=admin_headers).status_code == 200


def test_admin_29_content_review_role_matrix(
    admin_context: AdminTestContext,
    student_headers: dict[str, str],
    teacher_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    payload = {"content": "递归必须有出口。"}
    assert admin_context.client.post("/api/v1/content-review/check", headers=student_headers, json=payload).status_code == 403
    assert admin_context.client.post("/api/v1/content-review/check", headers=teacher_headers, json=payload).status_code == 200
    assert admin_context.client.post("/api/v1/content-review/check", headers=admin_headers, json=payload).status_code == 200


def test_admin_30_q012_profile_permission_contract_stays_active(
    admin_context: AdminTestContext,
    student_headers: dict[str, str],
):
    assert admin_context.client.get("/api/v1/profiles").status_code == 401
    assert admin_context.client.get("/api/v1/profiles", headers=student_headers).status_code == 403
    assert admin_context.client.get("/api/v1/profiles/me", headers=student_headers).status_code == 200


@pytest.mark.parametrize("role", ["student", "teacher"])
@pytest.mark.parametrize("case_index", ADMIN_ONLY_CASE_INDEXES)
def test_every_admin_only_operation_rejects_non_admin_roles(
    admin_context: AdminTestContext,
    case_index: int,
    role: str,
):
    case_name, method, path, payload = _operation_cases(admin_context.report_id)[case_index]
    response = admin_context.client.request(method, path, headers=_auth_headers(role), json=payload)
    assert response.status_code == 403, f"{role} {case_name}: {response.status_code} {response.text[:200]}"


@pytest.mark.parametrize("case_index", ADMIN_ONLY_CASE_INDEXES)
def test_every_admin_only_operation_accepts_admin_identity(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
    case_index: int,
):
    case_name, method, path, payload = _operation_cases(admin_context.report_id)[case_index]
    response = admin_context.client.request(method, path, headers=admin_headers, json=payload)
    assert response.status_code not in {401, 403}, f"admin {case_name}: {response.status_code} {response.text[:200]}"


def test_demo_status_public_compatibility_for_all_roles(admin_context: AdminTestContext):
    assert admin_context.client.get("/api/v1/demo-status").status_code == 200
    for role in ("student", "teacher", "admin"):
        assert admin_context.client.get("/api/v1/demo-status", headers=_auth_headers(role)).status_code == 200


def test_unimplemented_user_create_and_delete_routes_do_not_exist(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
):
    create = admin_context.client.post(
        "/api/v1/admin/users",
        headers=admin_headers,
        json={"account": "not-created", "role": "student"},
    )
    delete = admin_context.client.delete("/api/v1/admin/users/1", headers=admin_headers)
    assert create.status_code == 405
    assert delete.status_code == 404
    assert not admin_context.state_path.exists()


def test_role_in_body_cannot_elevate_student(
    admin_context: AdminTestContext,
    student_headers: dict[str, str],
):
    response = admin_context.client.patch(
        "/api/v1/admin/users/1/role",
        headers=student_headers,
        json={"role": "admin", "actor_role": "admin"},
    )
    assert response.status_code == 403
    assert not admin_context.state_path.exists()


def test_existing_logs_permission_contract_is_unchanged(
    admin_context: AdminTestContext,
    student_headers: dict[str, str],
    teacher_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    assert admin_context.client.get("/api/v1/logs").status_code == 401
    assert admin_context.client.get("/api/v1/logs", headers=student_headers).status_code == 403
    assert admin_context.client.get("/api/v1/logs", headers=teacher_headers).status_code == 403
    assert admin_context.client.get("/api/v1/logs", headers=admin_headers).status_code == 200


def test_non_admin_role_write_has_no_state_side_effect(
    admin_context: AdminTestContext,
    student_headers: dict[str, str],
    teacher_headers: dict[str, str],
):
    for headers in (student_headers, teacher_headers):
        response = admin_context.client.patch(
            "/api/v1/admin/users/1/role",
            headers=headers,
            json={"role": "admin"},
        )
        assert response.status_code == 403
    assert not admin_context.state_path.exists()


def test_admin_valid_write_is_persisted_and_audited(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
):
    response = admin_context.client.patch(
        "/api/v1/admin/users/1/status",
        headers=admin_headers,
        json={"status": "禁用"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "禁用"
    stored = json.loads(admin_context.state_path.read_text(encoding="utf-8"))
    assert next(item for item in stored["users"] if item["id"] == 1)["status"] == "禁用"
    db = admin_context.session_factory()
    try:
        audit = db.query(AuditLog).filter(AuditLog.action == "admin_user_status_updated").first()
        assert audit is not None
        assert audit.actor_role == "admin"
    finally:
        db.close()


def test_admin_report_responses_and_export_hide_physical_paths(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
):
    listing = admin_context.client.get("/api/v1/admin/reports", headers=admin_headers)
    assert listing.status_code == 200
    serialized = json.dumps(listing.json(), ensure_ascii=False)
    assert "report_path" not in serialized
    assert str(admin_context.report_file) not in serialized

    exported = admin_context.client.post("/api/v1/admin/reports/export", headers=admin_headers)
    assert exported.status_code == 200
    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
    assert manifest
    assert all("path" not in item for item in manifest)


def test_admin_settings_hide_secrets_connections_and_absolute_paths(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
):
    response = admin_context.client.get("/api/v1/settings", headers=admin_headers)
    assert response.status_code == 200
    serialized = json.dumps(response.json(), ensure_ascii=False).lower()
    assert str(Path.cwd()).lower() not in serialized
    for forbidden in ("api_secret", "password_hash", "sqlite:///", "access_token"):
        assert forbidden not in serialized
