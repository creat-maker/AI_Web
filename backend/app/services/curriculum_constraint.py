from __future__ import annotations

import re
from typing import Any


DEFAULT_CURRICULUM_TERMS = {
    "python", "循环", "for", "while", "range", "break", "continue", "变量", "列表", "条件", "嵌套", "调试", "代码", "输出", "算法"
}
OUT_OF_SCOPE_HINTS = {"神经网络", "微积分", "量子", "化学", "股票", "法律", "医学", "机器学习训练"}


def build_constrained_prompt(question: str, curriculum: list[str] | None = None) -> str:
    scope = "、".join(curriculum or sorted(DEFAULT_CURRICULUM_TERMS))
    return f"请只依据课程范围回答。课程范围：{scope}\n学生问题：{question}\n若问题超纲，请先提示边界，再给出回到课程内的建议。"


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z_]+|[\u4e00-\u9fff]{2,}", text.lower())


def check_curriculum_alignment(text: str, curriculum: list[str] | None = None) -> dict[str, Any]:
    terms = set(item.lower() for item in (curriculum or DEFAULT_CURRICULUM_TERMS))
    tokens = _tokens(text)
    if not tokens:
        return {
            "is_out_of_curriculum": False,
            "out_of_scope_terms": [],
            "out_of_scope_ratio": 0,
            "curriculum_alignment_score": 0.5,
            "boundary_warning": "",
        }
    out_terms = [token for token in tokens if token in OUT_OF_SCOPE_HINTS or (len(token) >= 4 and token not in terms and not any(term in token for term in terms))]
    ratio = round(len(out_terms) / max(len(tokens), 1), 3)
    score = round(max(0.0, min(1.0, 1 - ratio * 1.8)), 3)
    return {
        "is_out_of_curriculum": ratio > 0.25 or any(term in OUT_OF_SCOPE_HINTS for term in out_terms),
        "out_of_scope_terms": list(dict.fromkeys(out_terms))[:8],
        "out_of_scope_ratio": ratio,
        "curriculum_alignment_score": score,
        "boundary_warning": "该问题包含课程范围外内容，建议回到 Python 循环结构、变量变化和代码调试。" if score < 0.65 else "",
    }
