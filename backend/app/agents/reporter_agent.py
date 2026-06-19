from __future__ import annotations

from pathlib import Path
from typing import Any

from app.agents.state import AgentState
from app.core.config import settings

try:
    from docx import Document
except ModuleNotFoundError:  # pragma: no cover - depends on local optional dependency
    Document = None  # type: ignore[assignment]


def _clip(value: Any, limit: int = 500) -> str:
    text = "" if value is None else str(value)
    return text if len(text) <= limit else f"{text[:limit]}..."


def _add_json_like_paragraph(doc: Any, value: Any, limit: int = 900) -> None:
    doc.add_paragraph(_clip(value, limit))


def _summary_from_state(
    profile: dict[str, Any],
    evidence: dict[str, Any],
    learning_path: dict[str, Any],
    resources: list[dict[str, Any]],
    evaluation: dict[str, Any],
    audit: dict[str, Any],
) -> dict[str, Any]:
    return {
        "profile_summary": profile.get("diagnosis", "已生成学生画像。"),
        "evidence_summary": {
            "citation_count": evidence.get("citation_count", 0),
            "confidence": evidence.get("confidence", 0),
            "unsupported_answer_risk": evidence.get("unsupported_answer_risk", False),
        },
        "stages": learning_path.get("stages", []),
        "resource_count": len(resources),
        "resource_types": sorted({str(item.get("resource_type", "resource")) for item in resources}),
        "evaluation_summary": evaluation.get("mistake_analysis", ""),
        "audit_status": audit.get("review_status", "未审核"),
        "audit_risk_level": audit.get("risk_level", "unknown"),
    }


def reporter_agent(state: AgentState) -> AgentState:
    report_dir = settings.path_from_root(settings.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    profile = state.get("student_profile", {}) or {}
    evidence = state.get("knowledge_evidence", {}) or {}
    learning_path = state.get("learning_path", {}) or {}
    resource_plan = state.get("resource_plan", {}) or {}
    resources = state.get("generated_resources", []) or []
    tutor_answer = state.get("tutor_answer", {}) or {}
    evaluation = state.get("evaluation_result", {}) or {}
    audit = state.get("audit_result", {}) or {}
    summary = _summary_from_state(profile, evidence, learning_path, resources, evaluation, audit)

    suffix = ".docx" if Document else ".md"
    filename = f"agent_report_course_{state['course_id']}_{state.get('student_name', 'student')}{suffix}"
    safe_path = report_dir / filename.replace("/", "_").replace("\\", "_")

    if Document is None:
        markdown = [
            "# EduAgent Studio 学习报告",
            "",
            f"- 学生：{state.get('student_name', '')}",
            f"- 课程：{state.get('course_title', '')}",
            f"- 画像诊断：{profile.get('diagnosis', '已生成学生画像。')}",
            f"- RAG 证据：{evidence.get('citation_count', 0)} 条，置信度 {evidence.get('confidence', 0)}",
            f"- 资源数量：{len(resources)}",
            f"- 审核状态：{audit.get('review_status', '未审核')}，风险等级：{audit.get('risk_level', 'unknown')}",
            "",
            "## 智能答疑",
            _clip(tutor_answer.get("answer", ""), 1200),
            "",
            "## 资源清单",
            *[
                f"- {item.get('resource_type')} | {item.get('title')} | {item.get('difficulty', '未标注')}"
                for item in resources[:7]
            ],
        ]
        safe_path.write_text("\n".join(markdown), encoding="utf-8")
        return {
            **state,
            "report_path": str(Path(safe_path)),
            "report_summary": summary,
            "messages": [
                *state.get("messages", []),
                "ReporterAgent 未检测到 python-docx，已导出 Markdown 学习报告",
            ],
        }

    doc = Document()
    doc.add_heading("EduAgent Studio 学习报告", level=1)
    doc.add_paragraph(f"学生：{state.get('student_name', '')}")
    doc.add_paragraph(f"课程：{state.get('course_title', '')}")

    doc.add_heading("学生画像", level=2)
    doc.add_paragraph(profile.get("diagnosis", "已生成学生画像。"))
    for dimension in profile.get("dimensions", [])[:8]:
        doc.add_paragraph(
            f"{dimension.get('name')}：{dimension.get('value')}（依据：{dimension.get('evidence', '对话输入')}）",
            style="List Bullet",
        )

    doc.add_heading("RAG 检索证据", level=2)
    doc.add_paragraph(f"检索问题：{evidence.get('query', state.get('question') or state.get('learning_goal', ''))}")
    doc.add_paragraph(
        f"命中证据：{evidence.get('citation_count', 0)} 条；平均置信度：{evidence.get('confidence', 0)}；"
        f"低依据风险：{'是' if evidence.get('unsupported_answer_risk') else '否'}"
    )
    for item in evidence.get("items", [])[:5]:
        doc.add_paragraph(
            f"{item.get('citation_id') or '-'} | {item.get('source')} | {item.get('section') or item.get('knowledge_point') or '未标注章节'}",
            style="List Bullet",
        )

    doc.add_heading("个性化学习路径", level=2)
    doc.add_paragraph(learning_path.get("latest_adjustment_reason", "已根据画像和课程资料生成学习路径。"))
    for stage in learning_path.get("stages", []):
        doc.add_paragraph(f"{stage.get('name')} - {stage.get('target')}", style="List Bullet")

    doc.add_heading("资源生成计划", level=2)
    doc.add_paragraph(f"覆盖类型：{'、'.join(resource_plan.get('coverage', []))}")
    for item in resource_plan.get("items", [])[:7]:
        doc.add_paragraph(
            f"{item.get('resource_type')}：{item.get('title')}；目标短板：{item.get('target_weak_point')}",
            style="List Bullet",
        )

    doc.add_heading("生成资源包", level=2)
    for resource in resources[:7]:
        doc.add_paragraph(
            f"{resource.get('resource_type')} | {resource.get('title')} | 难度：{resource.get('difficulty', '未标注')}",
            style="List Bullet",
        )
        doc.add_paragraph(_clip(resource.get("recommendation_reason") or resource.get("recommend_reason", ""), 240))

    doc.add_heading("智能答疑", level=2)
    doc.add_paragraph(_clip(tutor_answer.get("answer", ""), 900))

    doc.add_heading("测评结果", level=2)
    _add_json_like_paragraph(doc, evaluation)

    doc.add_heading("内容审核", level=2)
    doc.add_paragraph(
        f"审核状态：{audit.get('review_status', '未审核')}；风险等级：{audit.get('risk_level', 'unknown')}；"
        f"资源数：{audit.get('resource_count', len(resources))}；引用数：{audit.get('citation_count', evidence.get('citation_count', 0))}"
    )
    for check in audit.get("checks", [])[:6]:
        doc.add_paragraph(f"{check.get('name')}：{check.get('status')} - {check.get('detail')}", style="List Bullet")

    doc.save(safe_path)

    return {
        **state,
        "report_path": str(Path(safe_path)),
        "report_summary": summary,
        "messages": [*state.get("messages", []), "ReporterAgent 导出包含 RAG 证据和审核结果的 Word 学习报告"],
    }
