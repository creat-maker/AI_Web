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
