from __future__ import annotations

import math
from typing import Any, Callable


LOOP_RETRIEVAL_SET = [
    {"question": "for 循环适合什么场景？", "expected_terms": ["for", "range", "遍历"]},
    {"question": "while 循环为什么会死循环？", "expected_terms": ["while", "条件", "更新"]},
    {"question": "break 和 continue 有什么区别？", "expected_terms": ["break", "continue", "跳出", "跳过"]},
    {"question": "循环嵌套怎么跟踪变量？", "expected_terms": ["嵌套", "变量", "内层", "外层"]},
    {"question": "列表遍历常见错误是什么？", "expected_terms": ["列表", "遍历", "下标"]},
]


def evaluate_retrieval(search_fn: Callable[[str, int], list[dict[str, Any]]], top_k: int = 5) -> dict[str, Any]:
    rows = []
    reciprocal_ranks = []
    recalls = []
    ndcgs = []
    for case in LOOP_RETRIEVAL_SET:
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
        dcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(gains))
        ideal_gains = sorted(gains, reverse=True)
        idcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(ideal_gains)) or 1.0
        ndcgs.append(round(dcg / idcg, 4))
        rows.append({"question": case["question"], "hit_ranks": hit_ranks, "top_k": len(results)})
    return {
        "dataset_size": len(LOOP_RETRIEVAL_SET),
        "scope": "演示测试集验证结果",
        "warning": "当前样本量较小，仅用于演示检索链路是否命中预期证据，不代表真实大规模评测结论。",
        "MRR": round(sum(reciprocal_ranks) / len(reciprocal_ranks), 4),
        "Recall@K": round(sum(recalls) / len(recalls), 4),
        "NDCG@K": round(sum(ndcgs) / len(ndcgs), 4),
        "details": rows,
        "mode": "tfidf-or-json-fallback-eval",
    }
