from app.services.dkvmn_tracker import dkvmn_tracker


def test_dkvmn_six_dimension_profile_mapping():
    state = dkvmn_tracker.initial_state()
    state = dkvmn_tracker.update("student-1", "while_loop", False, -0.1, state)
    state = dkvmn_tracker.update("student-1", "while_loop", False, -0.1, state)
    dimensions = dkvmn_tracker.map_to_profile_dimensions(state)
    assert len(dimensions) == 6
    assert dkvmn_tracker.get_weak_concepts("student-1", state)
    assert dimensions["学习风险"]["evidence_items"]
