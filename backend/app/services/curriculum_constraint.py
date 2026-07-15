from __future__ import annotations

import re
from typing import Any

from app.services.embedding_interface import TfidfEmbeddingProvider


DEFAULT_CURRICULUM_TERMS = {
    "python", "循环", "for", "while", "range", "break", "continue", "变量", "列表", "条件", "嵌套", "调试", "代码", "输出", "算法"
}
OUT_OF_SCOPE_HINTS = {"神经网络", "微积分", "量子", "化学", "股票", "法律", "医学", "机器学习训练"}
SEMANTIC_CONCEPTS = {
    "loop": {"循环", "迭代", "遍历", "重复执行"},
    "termination": {"终止条件", "退出条件", "条件更新", "死循环", "无限循环"},
    "branch_control": {"break", "continue", "跳出循环", "跳过本轮", "流程控制"},
    "nested_loop": {"循环嵌套", "嵌套循环", "内层循环", "外层循环"},
    "debugging": {"调试", "排错", "变量跟踪", "代码阅读", "输出分析"},
}
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
    lowered = text.lower()
    tokens = re.findall(r"[a-z_]+", lowered)
    for segment in re.findall(r"[\u4e00-\u9fff]+", lowered):
        if len(segment) <= 4:
            tokens.append(segment)
        tokens.extend(segment[index : index + 2] for index in range(len(segment) - 1))
        tokens.extend(segment[index : index + 3] for index in range(len(segment) - 2))
    return list(dict.fromkeys(tokens))


def _semantic_features(text: str) -> list[str]:
    lowered = text.lower()
    features = _tokens(text)
    for concept, aliases in SEMANTIC_CONCEPTS.items():
        if any(alias.lower() in lowered for alias in aliases):
            features.append(f"concept_{concept}")
    return list(dict.fromkeys(features))


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
    course: str | None = None,
    chapter: str | None = None,
    section: str | None = None,
    learning_objective: str | None = None,
    prerequisite: str | None = None,
) -> dict[str, Any]:
    terms = set(item.lower() for item in (curriculum or DEFAULT_CURRICULUM_TERMS))
    hierarchy_terms = [item for item in [course, chapter, section, learning_objective, prerequisite] if item]
    objective_texts = learning_objectives or ([learning_objective] if learning_objective else DEFAULT_LEARNING_OBJECTIVES)
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
            "alignment_breakdown": {
                "keyword_overlap_score": 0,
                "semantic_similarity_score": 0,
                "objective_match_score": 0,
                "prerequisite_match_score": 0,
                "out_of_scope_penalty": 0,
                "final_alignment_score": 0.5,
            },
            "evidence_coverage_score": 0,
            "boundary_warning": "",
            "suggested_rewrite": "",
            "suggested_actions": ["补充课程资料后再生成回答。"],
        }
    lowered_text = text.lower()
    out_terms = [term for term in OUT_OF_SCOPE_HINTS if term.lower() in lowered_text]
    ratio = round(len(out_terms) / max(len(tokens), 1), 3)
    syllabus_terms_overlap = _overlap_score(tokens, terms)
    learning_objective_overlap = _overlap_score(tokens, objective_terms)
    semantic_reference = " ".join([*sorted(terms), *objective_texts, *hierarchy_terms])
    query_features = _semantic_features(text)
    target_features = _semantic_features(semantic_reference)
    semantic_query = " ".join(query_features)
    semantic_target = " ".join(target_features)
    tfidf_similarity = TfidfEmbeddingProvider().similarity(semantic_query, semantic_target)
    query_concepts = {item for item in query_features if item.startswith("concept_")}
    target_concepts = {item for item in target_features if item.startswith("concept_")}
    concept_similarity = len(query_concepts & target_concepts) / max(len(query_concepts), 1) if query_concepts else 0.0
    semantic_similarity_score = round(max(tfidf_similarity, concept_similarity * 0.9), 4)
    prerequisite_match_score = _overlap_score(tokens, set(_tokens(prerequisite or ""))) if prerequisite else 0.8
    evidence_items = evidence_items or []
    evidence_coverage_score = round(min(1.0, len(evidence_items) / 3), 3)
    level_match_score = 0.86
    if target_level and any(token in text for token in ["高等数学", "研究生", "深度学习训练"]):
        level_match_score = 0.45
    out_of_scope_penalty = round(min(0.8, ratio * 1.8 + (0.35 if out_terms else 0)), 3)
    objective_match_score = max(learning_objective_overlap, _overlap_score(tokens, set(_tokens(learning_objective or ""))) if learning_objective else 0)
    score = round(
        max(
            0.0,
            min(
                1.0,
                syllabus_terms_overlap * 0.3
                + semantic_similarity_score * 0.22
                + objective_match_score * 0.18
                + prerequisite_match_score * 0.1
                + evidence_coverage_score * 0.12
                + level_match_score * 0.08
                - out_of_scope_penalty,
            ),
        ),
        3,
    )
    text_features = set(query_features)
    matched_objectives = [
        objective
        for objective in objective_texts
        if (
            text_features.intersection({item for item in _semantic_features(objective) if item.startswith("concept_")})
            or len(text_features.intersection({item for item in _semantic_features(objective) if not item.startswith("concept_")})) >= 2
        )
    ][:4]
    unmatched_terms = [
        token
        for token in tokens
        if len(token) >= 2
        and token not in terms
        and token not in objective_terms
        and not any(term in token or token in term for term in terms)
    ][:8]
    semantic_out_of_scope = (
        not out_terms
        and score < 0.35
        and syllabus_terms_overlap < 0.1
        and semantic_similarity_score < 0.1
    )
    is_out_of_curriculum = bool(out_terms) or semantic_out_of_scope
    suggested_actions = [
        "补充课程引用证据。" if evidence_coverage_score < 0.34 else "保留当前引用并标注来源。",
        "将回答限定在 Python 循环结构、变量更新和代码调试范围内。",
    ]
    if is_out_of_curriculum:
        suggested_actions.insert(0, "触发课程边界提示并转回课程内问题，必要时由教师复核。")
    elif score < 0.65:
        suggested_actions.insert(0, "触发边界提示或教师复核。")
    suggested_rewrite = ""
    if score < 0.65:
        suggested_rewrite = "请将内容改写为 Python 循环结构、变量更新、终止条件、break/continue 或列表遍历范围内的示例。"
    return {
        "is_out_of_curriculum": is_out_of_curriculum,
        "out_of_scope_terms": list(dict.fromkeys(out_terms or (unmatched_terms if semantic_out_of_scope else [])))[:8],
        "unmatched_terms": unmatched_terms,
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
            "keyword_overlap_score": syllabus_terms_overlap,
            "semantic_similarity_score": semantic_similarity_score,
            "objective_match_score": objective_match_score,
            "prerequisite_match_score": prerequisite_match_score,
            "final_alignment_score": score,
            "syllabus_terms_overlap": syllabus_terms_overlap,
            "learning_objective_overlap": learning_objective_overlap,
            "retrieved_evidence_coverage": evidence_coverage_score,
            "out_of_scope_penalty": out_of_scope_penalty,
            "level_match_score": level_match_score,
        },
        "boundary_warning": (
            "该问题包含课程范围外内容，建议回到 Python 循环结构、变量变化和代码调试。"
            if is_out_of_curriculum
            else "课程目标或引用证据对齐度不足，建议补充资料后由教师复核。"
            if score < 0.65
            else ""
        ),
        "suggested_rewrite": suggested_rewrite,
        "suggested_actions": suggested_actions,
    }
