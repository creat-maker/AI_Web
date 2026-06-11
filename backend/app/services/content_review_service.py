from __future__ import annotations

from datetime import datetime
from typing import Any

from app.services.demo_learning_service import build_content_review_items


REVIEW_RECORDS: list[dict[str, Any]] = []


RISKY_PHRASES = ["保证", "一定", "百分百", "完全掌握", "永远不会", "无需练习", "最强", "绝对"]


def check_content(payload: dict[str, Any]) -> dict[str, Any]:
    content = str(payload.get("content") or payload.get("answer") or "")
    citations = payload.get("citations") or payload.get("references") or []
    if not isinstance(citations, list):
        citations = []
    course_id = payload.get("courseId") or payload.get("course_id") or "python-programming"
    has_risky_claim = any(phrase in content for phrase in RISKY_PHRASES)
    citation_count = len(citations)
    citation_coverage = 0 if not content else min(1.0, citation_count / 3)
    suggestions: list[str] = []
    hallucination_warning = ""
    risk_level = "low"
    review_status = "pass"
    if citation_count == 0:
        risk_level = "medium"
        review_status = "warning"
        suggestions.append("补充至少 1 条课程资料引用来源。")
    if citation_coverage < 0.67:
        risk_level = "medium" if risk_level == "low" else risk_level
        review_status = "warning"
        suggestions.append("引用覆盖不足，建议关联到章节、讲义片段或练习题。")
    if has_risky_claim:
        risk_level = "high"
        review_status = "blocked"
        hallucination_warning = "内容包含夸张承诺或无依据结论，需要改写为可验证表述。"
        suggestions.append("删除“保证、一定、百分百”等绝对化表达。")
    confidence = round(0.92 - (0.22 if citation_count == 0 else 0) - (0.18 if citation_coverage < 0.67 else 0) - (0.26 if has_risky_claim else 0), 2)
    confidence = max(0.2, confidence)
    record = {
        "id": len(REVIEW_RECORDS) + 1,
        "courseId": course_id,
        "riskLevel": risk_level,
        "confidence": confidence,
        "citationCoverage": round(citation_coverage, 2),
        "hallucinationWarning": hallucination_warning,
        "reviewStatus": review_status,
        "suggestions": suggestions or ["内容引用充分，表达相对稳健，可用于演示。"],
        "citationCount": citation_count,
        "createdAt": datetime.utcnow().isoformat(timespec="seconds"),
        "contentPreview": content[:120],
    }
    REVIEW_RECORDS.insert(0, record)
    del REVIEW_RECORDS[50:]
    return record


def list_review_records(limit: int = 20) -> list[dict[str, Any]]:
    if REVIEW_RECORDS:
        return REVIEW_RECORDS[: max(1, min(limit, 50))]
    return build_content_review_items()["items"][: max(1, min(limit, 50))]
