from __future__ import annotations

import re
from typing import Any


DEFAULT_CURRICULUM_TERMS = {
    "python", "循环", "for", "while", "range", "break", "continue", "变量", "列表", "条件", "嵌套", "调试", "代码", "输出", "算法"
}
OUT_OF_SCOPE_HINTS = {"神经网络", "微积分", "量子", "化学", "股票", "法律", "医学", "机器学习训练"}
DEFAULT_LEARNING_OBJECTIVES = [
    "理解 for 循环和 while 循环的适用场景",
    "能够跟踪循环变量变化和终止条件",
    "区分 break 与 continue 的执行效果",
    "能够分析循环嵌套和列表遍历代码输出",
]


def build_constrained_prompt(question: str, curriculum: list[str] | None = None) -> str:
    scope = "、".join(curriculum or sorted(DEFAULT_CURRICULUM_TERMS))
    return f"请只依据课程范围回答。课程范围：{scope}\n学生问题：{question}\n若问题超纲，请先提示边界，再给出回到课程内的建议。"


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z_]+|[\u4e00-\u9fff]{2,}", text.lower())


def _overlap_score(tokens: list[str], terms: set[str]) -> float:
    if not tokens:
        return 0.0
    hits = sum(1 for token in tokens if token in terms or any(term in token for term in terms))
    return round(min(1.0, hits / max(len(tokens), 1) * 2), 3)


def check_curriculum_alignment(
    text: str,
    curriculum: list[str] | None = None,
    learning_objectives: list[str] | None = None,
    evidence_items: list[dict[str, Any]] | None = None,
    target_level: str | None = None,
) -> dict[str, Any]:
    terms = set(item.lower() for item in (curriculum or DEFAULT_CURRICULUM_TERMS))
    objective_texts = learning_objectives or DEFAULT_LEARNING_OBJECTIVES
    objective_terms = set()
    for objective in objective_texts:
        objective_terms.update(_tokens(objective))
    tokens = _tokens(text)
    if not tokens:
        return {
            "is_out_of_curriculum": False,
            "out_of_scope_terms": [],
            "out_of_scope_ratio": 0,
            "curriculum_alignment_score": 0.5,
            "syllabus_terms_overlap": 0,
            "learning_objective_overlap": 0,
            "retrieved_evidence_coverage": 0,
            "out_of_scope_penalty": 0,
            "level_match_score": 0.5,
            "matched_objectives": [],
            "alignment_breakdown": {},
            "evidence_coverage_score": 0,
            "boundary_warning": "",
            "suggested_actions": ["补充课程资料后再生成回答。"],
        }
    out_terms = [token for token in tokens if token in OUT_OF_SCOPE_HINTS or (len(token) >= 4 and token not in terms and not any(term in token for term in terms))]
    ratio = round(len(out_terms) / max(len(tokens), 1), 3)
    syllabus_terms_overlap = _overlap_score(tokens, terms)
    learning_objective_overlap = _overlap_score(tokens, objective_terms)
    evidence_items = evidence_items or []
    evidence_coverage_score = round(min(1.0, len(evidence_items) / 3), 3)
    level_match_score = 0.86
    if target_level and any(token in text for token in ["高等数学", "研究生", "深度学习训练"]):
        level_match_score = 0.45
    out_of_scope_penalty = round(min(0.8, ratio * 1.8 + (0.35 if any(term in OUT_OF_SCOPE_HINTS for term in out_terms) else 0)), 3)
    score = round(max(0.0, min(1.0, syllabus_terms_overlap * 0.36 + learning_objective_overlap * 0.24 + evidence_coverage_score * 0.22 + level_match_score * 0.18 - out_of_scope_penalty)), 3)
    matched_objectives = [
        objective
        for objective in objective_texts
        if any(token in objective.lower() or token in text.lower() for token in _tokens(objective))
    ][:4]
    suggested_actions = [
        "补充课程引用证据。" if evidence_coverage_score < 0.34 else "保留当前引用并标注来源。",
        "将回答限定在 Python 循环结构、变量更新和代码调试范围内。",
    ]
    if score < 0.65:
        suggested_actions.insert(0, "触发边界提示或教师复核。")
    return {
        "is_out_of_curriculum": ratio > 0.25 or any(term in OUT_OF_SCOPE_HINTS for term in out_terms),
        "out_of_scope_terms": list(dict.fromkeys(out_terms))[:8],
        "out_of_scope_ratio": ratio,
        "curriculum_alignment_score": score,
        "syllabus_terms_overlap": syllabus_terms_overlap,
        "learning_objective_overlap": learning_objective_overlap,
        "retrieved_evidence_coverage": evidence_coverage_score,
        "evidence_coverage_score": evidence_coverage_score,
        "out_of_scope_penalty": out_of_scope_penalty,
        "level_match_score": level_match_score,
        "matched_objectives": matched_objectives,
        "alignment_breakdown": {
            "syllabus_terms_overlap": syllabus_terms_overlap,
            "learning_objective_overlap": learning_objective_overlap,
            "retrieved_evidence_coverage": evidence_coverage_score,
            "out_of_scope_penalty": out_of_scope_penalty,
            "level_match_score": level_match_score,
        },
        "boundary_warning": "该问题包含课程范围外内容，建议回到 Python 循环结构、变量变化和代码调试。" if score < 0.65 else "",
        "suggested_actions": suggested_actions,
    }
