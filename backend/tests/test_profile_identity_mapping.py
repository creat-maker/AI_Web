from __future__ import annotations

import pytest

from app.services.demo_profile_chain import normalize_user_id


def test_legacy_student_one_maps_only_to_liming_template():
    assert normalize_user_id("1") == "demo-basic"
    assert normalize_user_id("student_001") == "demo-basic"
    assert normalize_user_id("student-li-ming") == "demo-basic"


def test_legacy_student_two_has_distinct_mapping():
    assert normalize_user_id("2") == "demo-advanced"


def test_legacy_student_three_has_distinct_mapping():
    assert normalize_user_id("3") == "demo-exam"


def test_unknown_or_zhangsan_identity_does_not_fall_back_to_liming():
    with pytest.raises(ValueError):
        normalize_user_id("demo-student-zhangsan")
    with pytest.raises(ValueError):
        normalize_user_id("999")
