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
