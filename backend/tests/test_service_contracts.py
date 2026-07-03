from types import SimpleNamespace

from app.services.chunk_strategy import chunk_document
from app.services.embedding_interface import TfidfEmbeddingProvider
from app.services.json_utils import dumps
from app.services.profile_service import profile_to_dict
from app.services.quiz_service import _answer_correctness, _question_concept
from app.services.retrieval_eval_service import evaluate_retrieval


def test_chunk_strategy_preserves_citation_metadata():
    chunks = chunk_document(
        {
            "source_file": "loop.md",
            "sections": [{"title": "while 循环", "paragraphs": ["条件更新" * 80]}],
            "warnings": ["demo warning"],
        },
        chunk_size=80,
        overlap=10,
    )
    assert len(chunks) > 1
    assert chunks[0]["citation_id"] == "loop.md-001"
    assert chunks[0]["metadata"]["parser_warnings"] == ["demo warning"]


def test_tfidf_embedding_similarity_prefers_related_text():
    provider = TfidfEmbeddingProvider()
    related = provider.similarity("while 循环 条件更新", "while 循环必须更新条件变量")
    unrelated = provider.similarity("while 循环 条件更新", "量子化学 股票")
    assert related > unrelated
    assert len(provider.embed(["for 循环", "while 循环"])) == 2


def test_retrieval_eval_returns_metric_shape():
    def search(question: str, top_k: int):
        return [{"content": question, "section_title": "循环结构"}][:top_k]

    result = evaluate_retrieval(search, top_k=3)
    assert result["dataset_size"] == 5
    assert {"MRR", "Recall@K", "NDCG@K", "details"} <= set(result)
    assert result["details"][0]["top_k"] == 1


def test_profile_to_dict_returns_stable_fields():
    profile = SimpleNamespace(
        id=1,
        student_name="李明",
        course_id=2,
        current_level="基础薄弱",
        learning_goal="掌握循环结构",
        weak_points=dumps(["while 循环"]),
        learning_preference="代码案例",
        profile_json=dumps({"user_id": "demo", "student_name": "李明"}),
        dimension_scores=dumps({"知识基础": {"score": 62}}),
        evidence_items=dumps([{"source_type": "quiz"}]),
        cognitive_state=dumps({"model": "lightweight-key-value-memory-dkvmn"}),
        profile_history=dumps([]),
        risk_level="medium",
        created_at=None,
        updated_at=None,
    )
    data = profile_to_dict(profile)
    assert data["student_name"] == "李明"
    assert data["dimension_scores"]["知识基础"]["score"] == 62
    assert data["cognitive_state"]["model"] == "lightweight-key-value-memory-dkvmn"


def test_quiz_service_concept_and_correctness_helpers():
    question = {"id": "q1", "conceptId": "while_loop", "correctAnswer": "B"}
    assert _question_concept(question, 0) == "while_loop"
    assert _answer_correctness(question, {"q1": "B"}, 0, 0)
    assert not _answer_correctness(question, {"q1": "A"}, 0, 100)
