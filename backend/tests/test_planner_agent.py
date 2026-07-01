from app.services.dkvmn_tracker import dkvmn_tracker


def test_path_rules_for_low_and_high_score():
    state = dkvmn_tracker.initial_state()
    state = dkvmn_tracker.update("student-1", "while_loop", False, -0.1, state)
    state = dkvmn_tracker.update("student-1", "while_loop", False, -0.1, state)
    weak = dkvmn_tracker.get_weak_concepts("student-1", state)
    assert any(item["concept_id"] == "while_loop" for item in weak)

    state = dkvmn_tracker.update("student-1", "for_loop", True, 0.2, state)
    state = dkvmn_tracker.update("student-1", "for_loop", True, 0.2, state)
    state = dkvmn_tracker.update("student-1", "for_loop", True, 0.2, state)
    assert dkvmn_tracker.get_strong_concepts("student-1", state)
