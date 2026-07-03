from app.services.dkvmn_tracker import dkvmn_tracker
from app.agents.planner_agent import planner_agent


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


def test_planner_agent_generates_learning_path():
    state = planner_agent(
        {
            "student_profile": {
                "learning_goal": "掌握 Python 循环结构",
                "weak_points": ["while 循环条件更新"],
                "learning_preference": "代码案例",
            },
            "course_title": "Python 程序设计",
            "retrieved_context": [{"citation_id": "c1", "confidence": 0.8}],
            "knowledge_evidence": {"confidence": 0.8},
            "messages": [],
        }
    )
    path = state["learning_path"]
    assert path["course_title"] == "Python 程序设计"
    assert path.get("stages")
    assert "PlannerAgent" in state["messages"][-1]


def test_consecutive_wrong_answers_insert_practice_need():
    state = dkvmn_tracker.initial_state()
    for _ in range(3):
        state = dkvmn_tracker.update("student-1", "nested_loop", False, -0.2, state)
    weak = dkvmn_tracker.get_weak_concepts("student-1", state)
    assert weak[0]["concept_id"] == "nested_loop"
    assert weak[0]["wrong_streak"] >= 3


def test_strong_concepts_support_difficulty_upgrade():
    state = dkvmn_tracker.initial_state()
    for _ in range(4):
        state = dkvmn_tracker.update("student-1", "list_iteration", True, 0.2, state)
    strong = dkvmn_tracker.get_strong_concepts("student-1", state)
    assert any(item["concept_id"] == "list_iteration" for item in strong)


def test_mastery_distribution_records_adjustment_basis():
    state = dkvmn_tracker.initial_state()
    state = dkvmn_tracker.update("student-1", "while_loop", False, -0.2, state)
    distribution = dkvmn_tracker.get_mastery_distribution("student-1", state)
    assert set(distribution) == {"average_mastery", "high", "medium", "low"}
    assert distribution["low"] >= 1
