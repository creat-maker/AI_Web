from app.services.curriculum_constraint import build_constrained_prompt, check_curriculum_alignment


def test_curriculum_prompt_and_alignment():
    prompt = build_constrained_prompt("while 循环怎么写？")
    assert "课程范围" in prompt
    aligned = check_curriculum_alignment("while 循环需要条件和变量更新", evidence_items=[{"citation_id": "c1"}])
    assert not aligned["is_out_of_curriculum"]
    assert aligned["curriculum_alignment_score"] > 0.6
    assert aligned["alignment_breakdown"]["syllabus_terms_overlap"] > 0
    assert aligned["suggested_actions"]


def test_curriculum_alignment_returns_matched_objectives():
    result = check_curriculum_alignment(
        "for 循环和 while 循环都需要理解终止条件，并跟踪循环变量变化。",
        evidence_items=[{"citation_id": "c1"}, {"citation_id": "c2"}],
    )
    assert result["curriculum_alignment_score"] > 0.6
    assert result["matched_objectives"]
    assert result["alignment_breakdown"]["learning_objective_overlap"] > 0


def test_out_of_scope_detection():
    result = check_curriculum_alignment("量子化学和股票法律问题")
    assert result["is_out_of_curriculum"]
    assert result["boundary_warning"]
    assert result["out_of_scope_terms"]


def test_insufficient_evidence_boundary_warning():
    result = check_curriculum_alignment("股票预测模型和医学法律建议")
    assert result["curriculum_alignment_score"] < 0.65
    assert "教师复核" in result["suggested_actions"][0]
    assert result["boundary_warning"]


def test_evidence_coverage_score_scales_with_citations():
    low = check_curriculum_alignment("while 循环条件更新", evidence_items=[])
    high = check_curriculum_alignment(
        "while 循环条件更新",
        evidence_items=[{"citation_id": "c1"}, {"citation_id": "c2"}, {"citation_id": "c3"}],
    )
    assert low["evidence_coverage_score"] == 0
    assert high["evidence_coverage_score"] == 1
