from app.services.lightweight_rag_service import ask_rag


def test_rag_returns_citations_and_debug_scores():
    result = ask_rag("while 循环为什么会死循环？", "python-programming", "demo-basic")
    assert result["answer"]
    assert isinstance(result["citations"], list)
    assert "curriculum_alignment_score" in result
    assert "alignment_breakdown" in result
    assert "matched_objectives" in result
    assert "evidence_coverage_score" in result
    assert result["retrieval_debug"]["scores"]
    assert {"vector_score", "lexical_score", "fusion_score"} <= set(result["retrieval_debug"]["scores"][0])


def test_rag_confidence_and_next_step_present():
    result = ask_rag("break 和 continue 有什么区别？", "python-programming", "demo-basic")
    assert isinstance(result["confidence"], float)
    assert result["lowEvidenceRisk"] in {"低", "中", "高"}
    assert result["nextStep"]
    assert result["suggested_actions"]


def test_rag_out_of_scope_boundary_fields():
    result = ask_rag("股票机器学习训练怎么做？", "python-programming", "demo-basic")
    assert "is_out_of_curriculum" in result
    assert "out_of_scope_terms" in result
    assert "boundary_warning" in result


def test_non_practice_query_keeps_citation_shape():
    result = ask_rag("for 循环适合什么场景？", "python-programming", "demo-basic")
    assert result["retrievalMode"] == "hybrid-tfidf-json-fallback"
    assert result["retrieval_debug"]["json_fallback"]
    assert all("citation_id" in item for item in result["citations"])


def test_question_bank_chunks_are_downweighted_for_concept_query():
    result = ask_rag("while 循环适合什么场景？", "python-programming", "demo-basic")
    scores = result["retrieval_debug"]["scores"]
    assert scores
    assert all("fusion_score" in item for item in scores)
    assert result["matchedChunks"][0]["confidence"] >= result["matchedChunks"][-1]["confidence"]


def test_json_fallback_dataset_is_reported():
    result = ask_rag("列表遍历和循环有什么关系？", "python-programming", "demo-basic")
    assert result["retrieval_debug"]["chroma_status"] == "fallback_json_keyword"
    assert result["dataset"].endswith("python_programming.json")
