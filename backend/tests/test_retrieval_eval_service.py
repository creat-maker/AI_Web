from pathlib import Path

from app.services.retrieval_eval_service import RetrievalEvalService, evaluate_retrieval


def test_retrieval_eval_metrics_and_export(tmp_path: Path):
    def search(question: str, top_k: int):
        return [{"content": question, "section": "循环结构"} for _ in range(min(top_k, 2))]

    result = evaluate_retrieval(search, top_k=3)
    assert {"recall_at_k", "mrr", "ndcg_at_k", "precision_at_k", "coverage_rate"} <= set(result)
    path = RetrievalEvalService().export_eval_summary(result, tmp_path / "summary.md")
    assert path.exists()
    assert "Precision@K" in path.read_text(encoding="utf-8")
