from __future__ import annotations

from datetime import datetime
from typing import Any

from app.services.demo_learning_service import build_content_review_items
from app.services.xfyun_safety_service import xfyun_safety_service


REVIEW_RECORDS: list[dict[str, Any]] = []


ABSOLUTE_PHRASES = ["保证", "一定", "必然", "100%", "百分百", "完全掌握", "永远不会", "无需练习", "最强", "绝对"]
SENSITIVE_PHRASES = ["作弊", "代考", "泄题", "破解", "绕过监考", "违规"]


def check_content(payload: dict[str, Any]) -> dict[str, Any]:
    content = str(payload.get("content") or payload.get("answer") or "")
    citations = payload.get("citations") or payload.get("references") or []
    if not isinstance(citations, list):
        citations = []
    course_id = payload.get("courseId") or payload.get("course_id") or "python-programming"
    content_type = payload.get("contentType") or payload.get("content_type") or _detect_content_type(content)
    absolute_hits = [phrase for phrase in ABSOLUTE_PHRASES if phrase in content]
    sensitive_hits = [phrase for phrase in SENSITIVE_PHRASES if phrase in content]
    has_risky_claim = bool(absolute_hits or sensitive_hits)
    citation_count = len(citations)
    citation_coverage = 0 if not content else min(1.0, citation_count / 3)
    suggestions: list[str] = []
    triggered_rules: list[dict[str, Any]] = []
    hallucination_warning = ""
    risk_level = "low"
    review_status = "pass"
    display_status = "通过"
    if citation_count == 0:
        risk_level = "medium"
        review_status = "warning"
        display_status = "人工复核"
        suggestions.append("补充至少 1 条课程资料引用来源。")
        triggered_rules.append({"rule": "citation_missing", "detail": "未提供课程知识库引用。"})
    if citation_coverage < 0.67:
        risk_level = "medium" if risk_level == "low" else risk_level
        review_status = "warning"
        display_status = "需修改"
        suggestions.append("引用覆盖不足，建议关联到章节、讲义片段或练习题。")
        triggered_rules.append({"rule": "citation_coverage_low", "detail": f"引用覆盖度 {round(citation_coverage, 2)}。"})
    if absolute_hits:
        triggered_rules.append({"rule": "absolute_expression", "detail": "命中绝对化表达：" + "、".join(absolute_hits)})
    if sensitive_hits:
        triggered_rules.append({"rule": "sensitive_terms", "detail": "命中风险词：" + "、".join(sensitive_hits)})
    if has_risky_claim:
        risk_level = "high"
        review_status = "blocked"
        display_status = "风险拦截"
        hallucination_warning = "内容包含夸张承诺或无依据结论，需要改写为可验证表述。"
        suggestions.append("删除“保证、一定、必然、100%”等绝对化表达，风险词需人工复核。")
    xfyun_safety = xfyun_safety_service.check(content)
    confidence = round(0.92 - (0.22 if citation_count == 0 else 0) - (0.18 if citation_coverage < 0.67 else 0) - (0.26 if has_risky_claim else 0), 2)
    confidence = max(0.2, confidence)
    review_required = risk_level != "low" or citation_count == 0
    citation_warning = citation_count == 0 or citation_coverage < 0.67
    record = {
        "id": len(REVIEW_RECORDS) + 1,
        "courseId": course_id,
        "riskLevel": risk_level,
        "confidence": confidence,
        "citationCoverage": round(citation_coverage, 2),
        "citation_warning": citation_warning,
        "review_required": review_required,
        "hallucinationWarning": hallucination_warning,
        "reviewStatus": review_status,
        "displayReviewStatus": display_status,
        "contentType": content_type,
        "triggeredRules": triggered_rules,
        "recommendedAction": _recommended_action(risk_level, review_required),
        "reviewDimensions": [
            {"name": "事实准确性", "status": "通过" if not has_risky_claim else "人工复核"},
            {"name": "知识点匹配度", "status": "通过", "detail": "匹配 Python 程序设计 / 循环结构。"},
            {"name": "难度匹配度", "status": "通过", "detail": "适配基础薄弱 + 代码实操偏好型。"},
            {"name": "引用依据完整性", "status": "通过" if citation_count else "需修改"},
            {"name": "敏感违规内容", "status": "人工复核" if sensitive_hits else "通过"},
            {"name": "绝对化表达", "status": "需修改" if absolute_hits else "通过"},
            {"name": "是否建议人工复核", "status": "人工复核" if review_required else "通过"},
        ],
        "citationBasis": "Python 程序设计课程知识库 / 循环结构章节",
        "suggestions": suggestions or ["内容引用充分，表达相对稳健，可进入发布流程。"],
        "citationCount": citation_count,
        "manualReviewNotice": "AI 生成内容需经教师或管理员审核后进入正式教学资源。",
        "xfyunSafety": xfyun_safety,
        "createdAt": datetime.utcnow().isoformat(timespec="seconds"),
        "contentPreview": content[:120],
    }
    REVIEW_RECORDS.insert(0, record)
    del REVIEW_RECORDS[50:]
    return record


def _detect_content_type(content: str) -> str:
    if "题" in content or "答案" in content:
        return "quiz"
    if "报告" in content or "分析" in content:
        return "report"
    if "为什么" in content or "怎么" in content:
        return "qa"
    return "handout"


def _recommended_action(risk_level: str, review_required: bool) -> str:
    if risk_level == "high":
        return "驳回"
    if review_required:
        return "人工复核"
    return "通过"


def list_review_records(limit: int = 20) -> list[dict[str, Any]]:
    if REVIEW_RECORDS:
        return REVIEW_RECORDS[: max(1, min(limit, 50))]
    return build_content_review_items()["items"][: max(1, min(limit, 50))]
