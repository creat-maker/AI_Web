from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Course, LearningReport, StudentProfile
from app.services.json_utils import dumps

try:
    from docx import Document
except ModuleNotFoundError:  # pragma: no cover - depends on local optional dependency
    Document = None  # type: ignore[assignment]


def create_learning_report(
    db: Session,
    profile: StudentProfile,
    course: Course,
    summary: dict,
) -> LearningReport:
    report_dir = settings.path_from_root(settings.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    filename = f"learning_report_profile_{profile.id}{'.docx' if Document else '.md'}"
    report_path = report_dir / filename

    if Document:
        doc = Document()
        doc.add_heading("EduAgent Studio 个性化学习报告", level=1)
        doc.add_paragraph(f"课程：{course.title}")
        doc.add_paragraph(f"学生：{profile.student_name}")
        doc.add_paragraph(f"学习目标：{profile.learning_goal or ''}")
        doc.add_heading("画像摘要", level=2)
        doc.add_paragraph(summary.get("profile_summary", "已生成学生画像。"))
        doc.add_heading("学习路径", level=2)
        for stage in summary.get("stages", []):
            doc.add_paragraph(f"{stage.get('name')}：{stage.get('target')}", style="List Bullet")
        doc.add_heading("测评反馈", level=2)
        doc.add_paragraph(summary.get("evaluation_summary", "等待测评结果持续更新。"))
        doc.save(report_path)
    else:
        lines = [
            "# EduAgent Studio 个性化学习报告",
            "",
            f"- 课程：{course.title}",
            f"- 学生：{profile.student_name}",
            f"- 学习目标：{profile.learning_goal or ''}",
            "",
            "## 画像摘要",
            summary.get("profile_summary", "已生成学生画像。"),
            "",
            "## 学习路径",
            *[f"- {stage.get('name')}：{stage.get('target')}" for stage in summary.get("stages", [])],
            "",
            "## 测评反馈",
            summary.get("evaluation_summary", "等待测评结果持续更新。"),
        ]
        report_path.write_text("\n".join(lines), encoding="utf-8")

    report = LearningReport(
        student_profile_id=profile.id,
        course_id=course.id,
        report_title=f"{profile.student_name} - {course.title} 学习报告",
        report_path=str(report_path),
        report_json=dumps(summary),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def report_exists(report: LearningReport) -> bool:
    return Path(report.report_path).exists()
