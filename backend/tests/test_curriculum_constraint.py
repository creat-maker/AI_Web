from app.services.curriculum_constraint import build_constrained_prompt, check_curriculum_alignment


def test_curriculum_prompt_and_alignment():
    prompt = build_constrained_prompt("while 循环怎么写？")
    assert "课程范围" in prompt
    aligned = check_curriculum_alignment("while 循环需要条件和变量更新")
    assert not aligned["is_out_of_curriculum"]
    assert aligned["curriculum_alignment_score"] > 0.6


def test_out_of_scope_detection():
    result = check_curriculum_alignment("量子化学和股票法律问题")
    assert result["is_out_of_curriculum"]
    assert result["boundary_warning"]
