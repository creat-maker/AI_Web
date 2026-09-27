from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROFILE_VIEW = ROOT / "frontend" / "src" / "views" / "StudentProfile.vue"
LOGIN_VIEW = ROOT / "frontend" / "src" / "views" / "Login.vue"
ROLE_STATE = ROOT / "frontend" / "src" / "composables" / "useRole.ts"
API_CLIENT = ROOT / "frontend" / "src" / "api" / "client.ts"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_front_01_student_profile_hides_teacher_student_list():
    source = _read(PROFILE_VIEW)
    assert 'data-testid="teacher-student-list"' in source
    assert 'v-if="currentRole === \'teacher\'"' in source


def test_front_02_student_identity_comes_from_profiles_me():
    source = _read(PROFILE_VIEW)
    assert "api.get<StudentProfileItem>('/api/v1/profiles/me')" in source
    assert "/api/v1/profiles?user_id=" not in source


def test_front_03_student_page_only_uses_profiles_me_for_profile_selection():
    source = _read(PROFILE_VIEW)
    assert "currentRole.value === 'student'" in source
    assert "studentProfile ? [studentProfile] : []" in source


def test_front_04_student_api_failure_does_not_render_other_identity_fallback():
    source = _read(PROFILE_VIEW)
    assert "currentRole.value === 'student' ? [] : fallbackStudents" in source
    assert "画像接口暂不可用，未显示本地学生身份数据。" in source


def test_front_05_login_clears_previous_role_profile_state():
    login_source = _read(LOGIN_VIEW)
    role_source = _read(ROLE_STATE)
    assert "clearRole, setDemoUserId, setRole" in login_source
    assert login_source.index("clearRole();") < login_source.index("localStorage.setItem('edumind.accessToken'")
    assert "localStorage.removeItem(USER_ID_KEY)" in role_source
    assert "localStorage.removeItem(STUDENT_ID_KEY)" in role_source


def test_front_06_sensitive_profile_requests_do_not_receive_demo_identity_header():
    source = _read(API_CLIENT)
    assert "if (shouldAppendUserId(url.pathname))" in source
    assert "headers.set('X-Demo-User-Id', userId);" in source
    assert source.index("if (shouldAppendUserId(url.pathname))") < source.index(
        "headers.set('X-Demo-User-Id', userId);"
    )
