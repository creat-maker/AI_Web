from __future__ import annotations

from pathlib import Path

from docx import Document

from app.agents.state import AgentState
from app.core.config import settings


def reporter_agent(state: AgentState) -> AgentState:
    report_dir = settings.path_from_root(settings.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    filename = f"agent_report_course_{state['course_id']}_{state.get('student_name', 'student')}.docx"
    safe_path = report_dir / filename.replace("/", "_").replace("\\", "_")

    doc = Document()
    doc.add_heading("EduAgent Studio 学习报告", level=1)
    doc.add_paragraph(f"学生：{state.get('student_name', '')}")
    doc.add_paragraph(f"课程：{state.get('course_title', '')}")
    doc.add_heading("学生画像", level=2)
    doc.add_paragraph(str(state.get("student_profile", {})))
    doc.add_heading("学习路径", level=2)
    for stage in state.get("learning_path", {}).get("stages", []):
        doc.add_paragraph(f"{stage.get('name')} - {stage.get('target')}", style="List Bullet")
    doc.add_heading("测评结果", level=2)
    doc.add_paragraph(str(state.get("evaluation_result", {})))
    doc.save(safe_path)

    summary = {
        "profile_summary": state.get("student_profile", {}).get("diagnosis", "已生成学生画像。"),
        "stages": state.get("learning_path", {}).get("stages", []),
        "evaluation_summary": state.get("evaluation_result", {}).get("mistake_analysis", ""),
    }
    return {
        **state,
        "report_path": str(Path(safe_path)),
        "report_summary": summary,
        "messages": [*state.get("messages", []), "ReporterAgent 导出 Word 学习报告"],
    }
