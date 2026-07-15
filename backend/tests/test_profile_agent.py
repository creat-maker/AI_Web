from app.services.dkvmn_tracker import dkvmn_tracker
from app.agents.profile_agent import profile_agent


def test_dkvmn_six_dimension_profile_mapping():
    state = dkvmn_tracker.initial_state()
    state = dkvmn_tracker.update("student-1", "while_loop", False, -0.1, state)
    state = dkvmn_tracker.update("student-1", "while_loop", False, -0.1, state)
    dimensions = dkvmn_tracker.map_to_profile_dimensions(state)
    assert len(dimensions) == 6
    assert dkvmn_tracker.get_weak_concepts("student-1", state)
    assert dimensions["学习风险"]["evidence_items"]


def test_profile_agent_reuses_dialog_profile():
    profile = {"source": "dialog", "studentName": "李明", "dimensions": []}
    state = profile_agent({"student_profile": profile, "messages": []})
    assert state["student_profile"] is profile
    assert "对话式画像" in state["messages"][-1]


def test_profile_agent_generates_six_dimension_profile():
    state = profile_agent(
        {
            "student_name": "李明",
            "course_title": "Python 程序设计",
            "weak_points": ["while 循环条件更新"],
            "learning_preference": "代码案例",
            "messages": [],
        }
    )
    profile = state["student_profile"]
    assert profile
    assert "messages" in state
    assert any(key in profile for key in ["dimensions", "dimension_scores", "weak_points", "summary"])


def test_dkvmn_cognitive_state_maps_to_profile_dimensions():
    state = dkvmn_tracker.initial_state()
    state = dkvmn_tracker.update("student-1", "break_continue", False, -0.2, state)
    cognitive_state = dkvmn_tracker.get_cognitive_state("student-1", state)
    dimensions = dkvmn_tracker.map_to_profile_dimensions(state)
    assert cognitive_state["weak_concepts"]
    assert "代码实操能力" in dimensions
    assert dimensions["代码实操能力"]["confidence"] > 0
