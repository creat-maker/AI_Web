from app.services.lightweight_rag_service import LightweightRAGService, ask_rag


def test_lightweight_rag_service_retrieve_and_answer():
    service = LightweightRAGService()
    result = service.answer_with_citations("while 循环为什么会死循环？")
    assert "answer" in result
    assert "citations" in result
    assert "retrieved_chunks" in result
    assert "curriculum_alignment" in result


def test_lightweight_rag_fallback_shape():
    result = LightweightRAGService().fallback_answer("量子化学")
    assert result["fallback_reason"]
    assert result["citations"] == []


def test_ask_rag_compat_has_new_fields():
    result = ask_rag("break 和 continue 有什么区别？")
    assert result["citations"]
    assert result["retrieved_chunks"]
    assert result["parser_warnings"] == []


def test_lightweight_rag_prefers_imported_course_vector_store():
    def retrieve(course_id: int, query: str, top_k: int):
        assert course_id == 7
        assert "while" in query
        return [
            {
                "content": "while 循环每轮都应更新条件变量，否则可能形成死循环。",
                "source_file": "chapter_03_control_flow.md",
                "section_title": "while 循环",
                "knowledge_point": "while 循环条件更新",
                "citation_id": "course-7-doc-3-chunk-2",
                "score": 0.91,
            }
        ][:top_k]

    result = LightweightRAGService(course_retriever=retrieve).answer_with_citations(
        "while 循环为什么会死循环？",
        course_id=7,
    )

    assert result["retrieval_mode"] == "course-vector-hybrid"
    assert result["fallback_used"] is False
    assert result["citations"][0]["citation_id"] == "course-7-doc-3-chunk-2"
    assert result["retrieved_chunks"][0]["retrieval_source"] == "course_vector_store"
