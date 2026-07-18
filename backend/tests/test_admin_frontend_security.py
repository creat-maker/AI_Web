from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_admin_frontend_routes_remain_role_scoped():
    source = _read("frontend/src/router/index.ts")
    for path in ("/dashboard", "/admin/users", "/admin/reports", "/admin/settings"):
        route_line = next(line for line in source.splitlines() if f"path: '{path}'" in line)
        assert "roles: ['admin']" in route_line


def test_admin_frontend_guard_uses_server_authenticated_role():
    source = _read("frontend/src/router/index.ts")
    assert "'/api/v1/auth/me'" in source
    assert "resolveAuthenticatedRole" in source
    assert "allowedRoles.includes(authenticatedRole)" in source


def test_admin_frontend_session_requires_token_not_local_role_only():
    source = _read("frontend/src/composables/useRole.ts")
    function_body = source.split("export function hasDemoSession()", 1)[1].split("}", 1)[0]
    assert "TOKEN_KEY" in function_body
    assert "readStoredRole" not in function_body


def test_role_switch_clears_admin_scoped_state():
    source = _read("frontend/src/composables/useRole.ts")
    assert "ADMIN_STATE_KEYS" in source
    assert "ADMIN_STATE_KEYS.forEach" in source


def test_admin_report_download_uses_authenticated_fetch_blob():
    view = _read("frontend/src/views/AdminReports.vue")
    client = _read("frontend/src/api/client.ts")
    assert "window.open" not in view
    assert "api.download" in view
    assert "URL.createObjectURL" in view
    assert "download:" in client
    assert "Authorization" in client


def test_admin_frontend_does_not_put_token_in_download_url():
    view = _read("frontend/src/views/AdminReports.vue")
    assert "accessToken" not in view
    assert "?token=" not in view
    assert "Authorization" not in view
