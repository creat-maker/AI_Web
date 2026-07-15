from app.services.curriculum_constraint import check_curriculum_alignment


def test_curriculum_semantic_full_partial_out_scope_and_extension():
    full = check_curriculum_alignment("while 循环条件更新和变量变化", chapter="循环结构", learning_objective="能够跟踪循环变量变化和终止条件")
    partial = check_curriculum_alignment("for 循环遍历列表", chapter="循环结构", learning_objective="能够跟踪循环变量变化和终止条件")
    out = check_curriculum_alignment("股票预测和量子化学训练", chapter="循环结构")
    extension = check_curriculum_alignment("循环嵌套可以作为算法思维拓展", chapter="循环结构", section="循环嵌套", prerequisite="for 循环")
    assert full["alignment_breakdown"]["semantic_similarity_score"] >= partial["alignment_breakdown"]["semantic_similarity_score"]
    assert out["is_out_of_curriculum"]
    assert out["suggested_rewrite"]
    assert extension["curriculum_alignment_score"] > out["curriculum_alignment_score"]


def test_curriculum_semantic_aliases_do_not_create_false_out_of_scope_terms():
    result = check_curriculum_alignment(
        "迭代过程中忘记修改退出条件，为什么会无限循环？",
        chapter="循环结构",
        section="while 循环",
        learning_objective="能够跟踪循环变量变化和终止条件",
        evidence_items=[{"citation_id": "course-1-doc-2-chunk-3"}],
    )

    assert result["is_out_of_curriculum"] is False
    assert result["out_of_scope_terms"] == []
    assert result["alignment_breakdown"]["semantic_similarity_score"] >= 0.8
    assert "能够跟踪循环变量变化和终止条件" in result["matched_objectives"]
