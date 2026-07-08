from app.services.quiz_service import QuizService, build_wrong_reason_analysis, grade_answers


def test_quiz_grade_wrong_reason_and_submit():
    service = QuizService()
    result = service.submit_quiz("student-test", "loop-basic-001", {"q1": "错误", "q2": "跳出循环", "q3": "3"})
    assert result["score"] < 100
    assert result["correct_count"] == 2
    assert result["dkvmn_updated"] is True
    assert result["wrong_reason_analysis"]
    assert result["recommended_tasks"]


def test_grade_answers_and_wrong_reason_analysis():
    graded = grade_answers(
        [{"id": "q1", "correctAnswer": "B", "concept_id": "break_continue"}],
        {"q1": "A"},
    )
    assert graded["score"] == 0
    reasons = build_wrong_reason_analysis(graded["items"])
    assert reasons[0]["concept_id"] == "break_continue"
