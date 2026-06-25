from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Course, LearningReport, StudentProfile
from app.services.json_utils import dumps

try:
    from docx import Document
except ModuleNotFoundError:  # pragma: no cover
    Document = None  # type: ignore[assignment]


def create_learning_report(
    db: Session,
    profile: StudentProfile,
    course: Course,
    summary: dict,
) -> LearningReport:
    report_dir = settings.path_from_root(settings.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    filename = f"learning_report_profile_{profile.id}_{course.id}{'.docx' if Document else '.md'}"
    report_path = report_dir / filename

    title = summary.get("title") or f"{profile.student_name} - {course.title} 学习诊断报告"
    profile_summary = summary.get("profile_summary") or summary.get("summary") or "已形成学习诊断摘要。"
    evaluation_summary = summary.get("evaluation_summary") or "结合测验、资源使用和问答记录持续更新。"
    weak_points = summary.get("weak_points") or []
    stages = summary.get("stages") or summary.get("learning_path") or []
    suggestions = summary.get("teaching_suggestions") or summary.get("learning_suggestions") or []

    if Document:
        doc = Document()
        doc.add_heading(title, level=1)
        doc.add_paragraph(f"课程：{course.title}")
        doc.add_paragraph(f"学生：{profile.student_name}")
        doc.add_paragraph(f"学习目标：{profile.learning_goal or '围绕当前章节完成学习闭环'}")
        doc.add_heading("画像摘要", level=2)
        doc.add_paragraph(str(profile_summary))
        doc.add_heading("薄弱知识点", level=2)
        for point in weak_points or ["循环结构综合应用"]:
            doc.add_paragraph(str(point), style="List Bullet")
        doc.add_heading("学习路径", level=2)
        for index, stage in enumerate(stages or [], start=1):
            if isinstance(stage, dict):
                name = stage.get("name") or stage.get("title") or stage.get("step") or f"阶段 {index}"
                target = stage.get("target") or stage.get("goal") or stage.get("content") or "完成当前学习目标"
                doc.add_paragraph(f"{name}：{target}", style="List Bullet")
        doc.add_heading("测评反馈", level=2)
        doc.add_paragraph(str(evaluation_summary))
        doc.add_heading("后续建议", level=2)
        for item in suggestions or ["完成分层练习后更新学习报告。"]:
            content = item.get("content") if isinstance(item, dict) else item
            doc.add_paragraph(str(content), style="List Bullet")
        doc.save(report_path)
    else:
        lines = [
            f"# {title}",
            "",
            f"- 课程：{course.title}",
            f"- 学生：{profile.student_name}",
            f"- 学习目标：{profile.learning_goal or '围绕当前章节完成学习闭环'}",
            "",
            "## 画像摘要",
            str(profile_summary),
            "",
            "## 薄弱知识点",
            *[f"- {point}" for point in (weak_points or ["循环结构综合应用"])],
            "",
            "## 测评反馈",
            str(evaluation_summary),
            "",
            "## 后续建议",
            *[f"- {item.get('content') if isinstance(item, dict) else item}" for item in (suggestions or ["完成分层练习后更新学习报告。"])],
        ]
        report_path.write_text("\n".join(lines), encoding="utf-8")

    report = LearningReport(
        student_profile_id=profile.id,
        course_id=course.id,
        report_title=title,
        report_path=str(report_path),
        report_json=dumps(summary),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def report_exists(report: LearningReport) -> bool:
    return Path(report.report_path).exists()
