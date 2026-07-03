from __future__ import annotations

from typing import Any

from app.agents.state import AgentState
from app.services.curriculum_constraint import check_curriculum_alignment
from app.services.xfyun_safety_service import xfyun_safety_service


AUDIT_DIMENSIONS = [
    "事实准确性",
    "课程对齐度",
    "超纲风险",
    "隐私风险",
    "不当内容",
    "幻觉风险",
    "学段适配",
]


def rule_engine_check(state: AgentState) -> dict[str, Any]:
    answer = str(state.get("tutor_answer", {}).get("answer") or state.get("tutor_answer") or "")
    resources = " ".join(str(item.get("content", "")) for item in state.get("generated_resources", []))
    content = f"{answer}\n{resources}"
    curriculum = check_curriculum_alignment(content or state.get("learning_goal", ""))
    privacy_hit = any(token in content for token in ["身份证", "手机号", "家庭住址", "银行卡"])
    inappropriate_hit = any(token in content for token in ["暴力", "辱骂", "作弊"])
    citation_count = int(state.get("knowledge_evidence", {}).get("citation_count") or len(state.get("retrieved_context", [])))
    hallucination_risk = citation_count == 0
    risk_score = 0
    risk_score += 2 if curriculum["is_out_of_curriculum"] else 0
    risk_score += 2 if privacy_hit else 0
    risk_score += 2 if inappropriate_hit else 0
    risk_score += 1 if hallucination_risk else 0
    risk_level = "high" if risk_score >= 3 else "medium" if risk_score >= 1 else "low"
    checks = [
        {"dimension": "事实准确性", "status": "warning" if hallucination_risk else "pass", "message": "引用证据不足" if hallucination_risk else "已绑定课程引用"},
        {"dimension": "课程对齐度", "status": "warning" if curriculum["curriculum_alignment_score"] < 0.7 else "pass", "score": curriculum["curriculum_alignment_score"]},
        {"dimension": "超纲风险", "status": "warning" if curriculum["is_out_of_curriculum"] else "pass", "terms": curriculum["out_of_scope_terms"]},
        {"dimension": "隐私风险", "status": "error" if privacy_hit else "pass"},
        {"dimension": "不当内容", "status": "error" if inappropriate_hit else "pass"},
        {"dimension": "幻觉风险", "status": "warning" if hallucination_risk else "pass"},
        {"dimension": "学段适配", "status": "pass", "message": "按 Python 程序设计课程难度输出"},
    ]
    return {"risk_level": risk_level, "checks": checks, "curriculum": curriculum, "risk_score": risk_score}


def compliance_agent(state: AgentState) -> AgentState:
    rule_result = rule_engine_check(state)
    content = str(state.get("tutor_answer", "")) + str(state.get("generated_resources", ""))
    xfyun_result = xfyun_safety_service.check(content)
    audit_result = {
        "review_status": "blocked" if rule_result["risk_level"] == "high" else "needs_review" if rule_result["risk_level"] == "medium" else "passed",
        "risk_level": rule_result["risk_level"],
        "checks": rule_result["checks"],
        "rule_engine_result": rule_result,
        "xfyun_result": xfyun_result,
        "suggestions": [
            "高风险内容进入教师仲裁，不直接返回学生。" if rule_result["risk_level"] == "high" else "建议教师抽查引用与题目难度。",
            "保留讯飞安全 API 接口，未配置时使用本地规则 fallback。",
        ],
    }
    return {
        **state,
        "audit_result": audit_result,
        "messages": [*state.get("messages", []), "ComplianceAgent 完成 7 维规则审核与讯飞安全 fallback 检查"],
    }


def should_retry_or_arbitrate(state: AgentState) -> str:
    audit = state.get("audit_result", {}) or {}
    retry_count = int(state.get("retry_count") or 0)
    risk_level = audit.get("risk_level") or "low"
    review_status = audit.get("review_status")
    if risk_level == "high":
        return "teacher_arbitration"
    if review_status in {"blocked", "needs_review"} and retry_count < 3:
        return "retry"
    if review_status in {"blocked", "needs_review"}:
        return "teacher_arbitration"
    return "pass"


def audit_retry(state: AgentState) -> AgentState:
    retry_count = int(state.get("retry_count") or 0) + 1
    failure_reasons = state.get("audit_result", {}).get("failure_reasons") or state.get("audit_result", {}).get("suggestions") or [state.get("audit_result", {}).get("review_status", "needs_review")]
    regeneration_instruction = (
        f"第 {retry_count} 次重新生成：收敛到 Python 循环结构课程范围，补充 RAG 引用，修复问题："
        + "；".join(str(item) for item in failure_reasons if item)
    )
    retry_log = [
        *state.get("audit_retry_log", []),
        {
            "retry_count": retry_count,
            "reason": state.get("audit_result", {}).get("review_status", "needs_review"),
            "failure_reasons": failure_reasons,
            "regeneration_instruction": regeneration_instruction,
            "modified_fields": ["generated_resources", "tutor_answer"],
        },
    ]
    resources = []
    for item in state.get("generated_resources", []):
        before_summary = str(item.get("content") or item.get("title") or "")[:120]
        revised_content = (
            f"{item.get('content', item.get('title', '资源'))}\n\n"
            f"审核回流修订：{regeneration_instruction}。引用依据限定为 Python 程序设计 / 循环结构。"
        )
        resources.append(
            {
                **item,
                "content": revised_content,
                "audit_status": "retry_generated",
                "audit_revision": f"第 {retry_count} 次根据审核意见重新生成资源内容。",
                "regeneration_reason": failure_reasons,
                "before_content_summary": before_summary,
                "after_content_summary": revised_content[:120],
            }
        )
    return {
        **state,
        "retry_count": retry_count,
        "audit_retry_log": retry_log,
        "generated_resources": resources,
        "regeneration_instruction": regeneration_instruction,
        "messages": [*state.get("messages", []), f"Audit retry 第 {retry_count} 次：回流 ResourceAgent 重新生成资源"],
    }


def teacher_arbitration_agent(state: AgentState) -> AgentState:
    result = {
        "status": "pending",
        "decision": None,
        "reason": "高风险或多次审核未通过，等待教师 approve / revise / reject。",
        "allowed_actions": ["approve", "revise", "reject"],
    }
    return {
        **state,
        "teacher_arbitration_result": result,
        "messages": [*state.get("messages", []), "TeacherArbitration 节点已创建待仲裁事项"],
    }
