from app.services.lightweight_rag_service import ask_rag


def test_rag_returns_citations_and_debug_scores():
    result = ask_rag("while 循环为什么会死循环？", "python-programming", "demo-basic")
    assert result["answer"]
    assert isinstance(result["citations"], list)
    assert "curriculum_alignment_score" in result
    assert result["retrieval_debug"]["scores"]
    assert {"vector_score", "lexical_score", "fusion_score"} <= set(result["retrieval_debug"]["scores"][0])


def test_non_practice_query_keeps_citation_shape():
    result = ask_rag("for 循环适合什么场景？", "python-programming", "demo-basic")
    assert result["retrievalMode"] == "hybrid-tfidf-json-fallback"
    assert all("citation_id" in item for item in result["citations"])
