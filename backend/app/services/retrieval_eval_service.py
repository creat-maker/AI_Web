from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Callable


LOOP_RETRIEVAL_SET = [
    {"question": "for 循环适合什么场景？", "expected_terms": ["for", "range", "遍历"]},
    {"question": "while 循环为什么会死循环？", "expected_terms": ["while", "条件", "更新"]},
    {"question": "break 和 continue 有什么区别？", "expected_terms": ["break", "continue", "跳出", "跳过"]},
    {"question": "循环嵌套怎么跟踪变量？", "expected_terms": ["嵌套", "变量", "内层", "外层"]},
    {"question": "列表遍历常见错误是什么？", "expected_terms": ["列表", "遍历", "下标"]},
]


def _metric_rows(search_fn: Callable[[str, int], list[dict[str, Any]]], dataset: list[dict[str, Any]], top_k: int) -> dict[str, Any]:
    rows = []
    reciprocal_ranks = []
    recalls = []
    ndcgs = []
    precisions = []
    coverages = []
    for case in dataset:
        results = search_fn(case["question"], top_k)
        hit_ranks = []
        gains = []
        for index, item in enumerate(results, start=1):
            text = " ".join(str(item.get(key, "")) for key in ("content", "snippet", "section", "section_title", "sourceFile"))
            gain = 1 if any(term.lower() in text.lower() for term in case["expected_terms"]) else 0
            gains.append(gain)
            if gain:
                hit_ranks.append(index)
        reciprocal_ranks.append(1 / hit_ranks[0] if hit_ranks else 0)
        recalls.append(1.0 if hit_ranks else 0.0)
        precisions.append(sum(gains) / max(len(results), 1))
        coverages.append(min(1.0, len(results) / max(top_k, 1)))
        dcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(gains))
        ideal_gains = sorted(gains, reverse=True)
        idcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(ideal_gains)) or 1.0
        ndcgs.append(round(dcg / idcg, 4))
        rows.append({"question": case["question"], "hit_ranks": hit_ranks, "top_k": len(results), "precision": round(precisions[-1], 4)})
    return {
        "dataset_size": len(dataset),
        "scope": "演示测试集验证结果",
        "warning": "当前样本量较小，仅用于演示检索链路是否命中预期证据，不代表真实大规模评测结论。",
        "MRR": round(sum(reciprocal_ranks) / len(reciprocal_ranks), 4),
        "Recall@K": round(sum(recalls) / len(recalls), 4),
        "NDCG@K": round(sum(ndcgs) / len(ndcgs), 4),
        "Precision@K": round(sum(precisions) / len(precisions), 4),
        "CoverageRate": round(sum(coverages) / len(coverages), 4),
        "mrr": round(sum(reciprocal_ranks) / len(reciprocal_ranks), 4),
        "recall_at_k": round(sum(recalls) / len(recalls), 4),
        "ndcg_at_k": round(sum(ndcgs) / len(ndcgs), 4),
        "precision_at_k": round(sum(precisions) / len(precisions), 4),
        "coverage_rate": round(sum(coverages) / len(coverages), 4),
        "details": rows,
        "mode": "tfidf-or-json-fallback-eval",
    }


def evaluate_retrieval(
    dataset_or_search_fn: Callable[[str, int], list[dict[str, Any]]] | list[dict[str, Any]],
    top_k: int = 5,
    search_fn: Callable[[str, int], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    if callable(dataset_or_search_fn):
        return _metric_rows(dataset_or_search_fn, LOOP_RETRIEVAL_SET, top_k)
    if search_fn is None:
        raise ValueError("dataset 模式必须提供 search_fn")
    return _metric_rows(search_fn, dataset_or_search_fn or LOOP_RETRIEVAL_SET, top_k)


class RetrievalEvalService:
    def evaluate_retrieval(
        self,
        dataset: list[dict[str, Any]] | None = None,
        top_k: int = 5,
        search_fn: Callable[[str, int], list[dict[str, Any]]] | None = None,
    ) -> dict[str, Any]:
        active_dataset = dataset or LOOP_RETRIEVAL_SET
        if search_fn is None:
            from app.services.lightweight_rag_service import LightweightRAGService

            rag = LightweightRAGService()
            search_fn = lambda question, limit: rag.retrieve(question, top_k=limit)["retrieved_chunks"]
        return _metric_rows(search_fn, active_dataset, top_k)

    def recall_at_k(self, details: list[dict[str, Any]]) -> float:
        return round(sum(1 for row in details if row.get("hit_ranks")) / max(len(details), 1), 4)

    def mrr(self, details: list[dict[str, Any]]) -> float:
        values = [1 / row["hit_ranks"][0] for row in details if row.get("hit_ranks")]
        return round(sum(values) / max(len(details), 1), 4)

    def ndcg_at_k(self, result: dict[str, Any]) -> float:
        return float(result.get("ndcg_at_k") or result.get("NDCG@K") or 0)

    def precision_at_k(self, details: list[dict[str, Any]]) -> float:
        return round(sum(float(row.get("precision", 0)) for row in details) / max(len(details), 1), 4)

    def coverage_rate(self, details: list[dict[str, Any]], top_k: int) -> float:
        return round(sum(min(1.0, int(row.get("top_k", 0)) / max(top_k, 1)) for row in details) / max(len(details), 1), 4)

    def export_eval_summary(self, result: dict[str, Any], output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Retrieval Evaluation Summary",
            "",
            f"- Dataset size: {result.get('dataset_size', 0)}",
            f"- Recall@K: {result.get('recall_at_k', result.get('Recall@K', 0))}",
            f"- MRR: {result.get('mrr', result.get('MRR', 0))}",
            f"- NDCG@K: {result.get('ndcg_at_k', result.get('NDCG@K', 0))}",
            f"- Precision@K: {result.get('precision_at_k', result.get('Precision@K', 0))}",
            f"- Coverage rate: {result.get('coverage_rate', result.get('CoverageRate', 0))}",
            "",
            "| Question | Hit ranks | Returned | Precision |",
            "| --- | --- | ---: | ---: |",
        ]
        for row in result.get("details", []):
            lines.append(f"| {row.get('question')} | {row.get('hit_ranks')} | {row.get('top_k')} | {row.get('precision', 0)} |")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path


retrieval_eval_service = RetrievalEvalService()
