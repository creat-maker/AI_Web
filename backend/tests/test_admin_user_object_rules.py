from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.api.routers import admin_users
from app.models import AuditLog
from test_admin_authorization import AdminTestContext, admin_context, admin_headers  # noqa: F401


def test_admin_rejects_unknown_user_instead_of_synthetic_success(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
):
    response = admin_context.client.patch(
        "/api/v1/admin/users/999999/status",
        headers=admin_headers,
        json={"status": "禁用"},
    )
    assert response.status_code == 404


def test_admin_rejects_invalid_status_and_role_values(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
):
    bad_status = admin_context.client.patch(
        "/api/v1/admin/users/1/status",
        headers=admin_headers,
        json={"status": "任意字符串"},
    )
    bad_role = admin_context.client.patch(
        "/api/v1/admin/users/1/role",
        headers=admin_headers,
        json={"role": "super-root"},
    )
    assert bad_status.status_code == 422
    assert bad_role.status_code == 422


def test_last_enabled_admin_cannot_be_disabled_or_demoted(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
):
    disable = admin_context.client.patch(
        "/api/v1/admin/users/4/status",
        headers=admin_headers,
        json={"status": "禁用"},
    )
    demote = admin_context.client.patch(
        "/api/v1/admin/users/4/role",
        headers=admin_headers,
        json={"role": "teacher"},
    )
    assert disable.status_code == 409
    assert demote.status_code == 409
    assert not admin_context.state_path.exists()


def test_role_permission_update_requires_existing_role_and_known_permissions(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
):
    missing = admin_context.client.patch(
        "/api/v1/admin/roles/not-a-role/permissions",
        headers=admin_headers,
        json={"permissions": ["学习总览"]},
    )
    unknown = admin_context.client.patch(
        "/api/v1/admin/roles/student/permissions",
        headers=admin_headers,
        json={"permissions": ["读取服务器密钥"]},
    )
    assert missing.status_code == 404
    assert unknown.status_code == 422


def test_admin_state_save_is_atomic_and_backup_first(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
):
    admin_context.state_path.write_text(
        json.dumps({"users": admin_users.DEFAULT_USERS, "roles": admin_users.DEFAULT_ROLES}, ensure_ascii=False),
        encoding="utf-8",
    )
    original = admin_context.state_path.read_bytes()
    response = admin_context.client.patch(
        "/api/v1/admin/users/1/status",
        headers=admin_headers,
        json={"status": "禁用"},
    )
    assert response.status_code == 200
    backup = Path(f"{admin_context.state_path}.bak")
    assert backup.exists()
    assert backup.read_bytes() == original
    assert not Path(f"{admin_context.state_path}.tmp").exists()
    json.loads(admin_context.state_path.read_text(encoding="utf-8"))


def test_admin_state_replace_failure_preserves_original_file(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    admin_context.state_path.write_text(
        json.dumps({"users": admin_users.DEFAULT_USERS, "roles": admin_users.DEFAULT_ROLES}, ensure_ascii=False),
        encoding="utf-8",
    )
    original = admin_context.state_path.read_bytes()

    def fail_replace(self: Path, target: Path) -> Path:
        raise OSError("simulated atomic replace failure")

    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(OSError, match="simulated atomic replace failure"):
        admin_context.client.patch(
            "/api/v1/admin/users/1/status",
            headers=admin_headers,
            json={"status": "禁用"},
        )
    assert admin_context.state_path.read_bytes() == original
    assert Path(f"{admin_context.state_path}.bak").read_bytes() == original
    assert not Path(f"{admin_context.state_path}.tmp").exists()


def test_reset_password_secret_is_not_written_to_audit_log(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
):
    response = admin_context.client.post(
        "/api/v1/admin/users/1/reset-password",
        headers=admin_headers,
    )
    assert response.status_code == 200
    password = response.json()["temporary_password"]
    db = admin_context.session_factory()
    try:
        audit = db.query(AuditLog).filter(AuditLog.action == "admin_password_reset").first()
        assert audit is not None
        assert password not in (audit.detail or "")
    finally:
        db.close()


def test_report_status_update_validates_object_and_status(
    admin_context: AdminTestContext,
    admin_headers: dict[str, str],
):
    missing = admin_context.client.patch(
        "/api/v1/admin/reports/999999/status",
        headers=admin_headers,
        json={"status": "已通过"},
    )
    invalid = admin_context.client.patch(
        f"/api/v1/admin/reports/{admin_context.report_id}/status",
        headers=admin_headers,
        json={"status": "任意状态"},
    )
    valid = admin_context.client.patch(
        f"/api/v1/admin/reports/{admin_context.report_id}/status",
        headers=admin_headers,
        json={"status": "已通过"},
    )
    assert missing.status_code == 404
    assert invalid.status_code == 422
    assert valid.status_code == 200
