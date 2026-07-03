from pathlib import Path

from app.services import dkvmn_tracker as dkvmn_module
from app.services.dkvmn_tracker import dkvmn_tracker


def test_dkvmn_initial_state():
    state = dkvmn_tracker.initial_state()
    assert state["key_matrix"]
    assert state["concept_registry"]
    assert len(state["value_memory"]) >= 9
    assert all("value_vector" in row for row in state["value_memory"].values())


def test_dkvmn_correct_answer_increases_mastery():
    state = dkvmn_tracker.initial_state()
    before = dkvmn_tracker.predict_mastery("student-1", "while_loop", state)
    result = dkvmn_tracker.update_memory("student-1", "while_loop", True, difficulty=0.6, response_time=30, score=90, state=state)
    assert result["mastery_after"] > before
    assert result["confidence"] > 0


def test_dkvmn_wrong_answer_decreases_mastery():
    state = dkvmn_tracker.initial_state()
    before = dkvmn_tracker.predict_mastery("student-1", "for_loop", state)
    result = dkvmn_tracker.update_memory("student-1", "for_loop", False, difficulty=0.7, response_time=120, score=40, state=state)
    assert result["mastery_after"] < before
    assert result["evidence_items"]


def test_dkvmn_weak_concepts():
    state = dkvmn_tracker.initial_state()
    state = dkvmn_tracker.update("student-1", "while_loop", False, -0.2, state)
    state = dkvmn_tracker.update("student-1", "while_loop", False, -0.2, state)
    weak = dkvmn_tracker.get_weak_concepts("student-1", state)
    assert any(item["concept_id"] == "while_loop" for item in weak)


def test_dkvmn_profile_mapping():
    state = dkvmn_tracker.initial_state()
    dimensions = dkvmn_tracker.map_to_profile_dimensions(state)
    assert set(dimensions) == {"知识基础", "学习节奏", "学习偏好", "代码实操能力", "易错知识点", "学习风险"}
    assert dkvmn_tracker.get_mastery_vector("student-1", state)


def test_dkvmn_persistence_fallback(tmp_path: Path, monkeypatch):
    fallback = tmp_path / "dkvmn_memory.json"
    monkeypatch.setattr(dkvmn_module, "FALLBACK_STATE_PATH", fallback)
    dkvmn_tracker.update_memory("student-fallback", "break_continue", False, difficulty=0.8, response_time=100, score=30)
    assert fallback.exists()
    state = dkvmn_tracker.state_from_fallback("student-fallback")
    assert state["value_memory"]["break_continue"]["attempts"] == 1
