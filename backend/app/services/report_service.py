from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Course, LearningReport, StudentProfile
from app.services.json_utils import dumps, loads

try:
    from docx import Document
except ModuleNotFoundError:  # pragma: no cover
    Document = None  # type: ignore[assignment]


class ReportService:
    def __init__(self, db: Session | None = None, report_dir: Path | None = None):
        self.db = db
        self.report_dir = report_dir or settings.path_from_root(settings.report_dir)

    def generate_student_report(
        self,
        profile_id: int | None = None,
        course_id: int | None = None,
        student_id: int | str | None = None,
        profile: StudentProfile | dict[str, Any] | None = None,
        course: Course | dict[str, Any] | None = None,
        quiz_results: list[dict[str, Any]] | dict[str, Any] | None = None,
        learning_path: dict[str, Any] | list[dict[str, Any]] | None = None,
        resource_usage: list[dict[str, Any]] | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        profile_obj = profile or self._query(StudentProfile, profile_id)
        course_obj = course or self._query(Course, course_id)
        profile_data = self._profile_data(profile_obj, student_id)
        course_name = self._get(course_obj, "title", "Python 程序设计")
        sections = self.build_report_sections(profile_data, course_name, quiz_results, learning_path, resource_usage)
        report = {
            "report_id": f"report-{uuid4().hex[:10]}",
            "student_name": profile_data.get("student_name", "李明"),
            "student_id": student_id or profile_data.get("id") or profile_id,
            "course_name": course_name,
            "profile_summary": sections["profile_summary"],
            "mastery_summary": sections["mastery_summary"],
            "weak_concepts": sections["weak_concepts"],
            "learning_path_summary": sections["learning_path_summary"],
            "quiz_summary": sections["quiz_summary"],
            "resource_recommendations": sections["resource_recommendations"],
            "teacher_suggestions": sections["teacher_suggestions"],
            "evidence_items": sections["evidence_items"],
            "generated_at": datetime.utcnow().isoformat(),
        }
        export = self.export_docx(report)
        report.update(export)
        report["download_url"] = f"/api/v1/reports/download/{Path(report['export_path']).name}" if report.get("export_path") else ""
        return report

    def build_report_sections(
        self,
        profile: dict[str, Any],
        course_name: str,
        quiz_results: list[dict[str, Any]] | dict[str, Any] | None = None,
        learning_path: dict[str, Any] | list[dict[str, Any]] | None = None,
        resource_usage: list[dict[str, Any]] | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        weak = profile.get("weak_points") or []
        evidence = profile.get("evidence_items") or []
        return {
            "profile_summary": f"{profile.get('student_name', '学生')} 当前学习目标为 {profile.get('learning_goal') or course_name}，风险等级 {profile.get('risk_level', 'medium')}。",
            "mastery_summary": self.summarize_mastery(profile.get("cognitive_state") or profile.get("dimension_scores") or {}),
            "weak_concepts": weak[:8] or ["while 循环条件更新"],
            "learning_path_summary": self.summarize_learning_path(learning_path),
            "quiz_summary": self.summarize_quiz_result(quiz_results),
            "resource_recommendations": self.summarize_resource_usage(resource_usage),
            "teacher_suggestions": self.build_teacher_suggestions(profile, quiz_results),
            "evidence_items": evidence[:20] or [{"source_type": "profile", "description": "基于画像、测验和资源使用记录生成。", "confidence": 0.72}],
        }

    def summarize_mastery(self, mastery: dict[str, Any]) -> dict[str, Any]:
        concepts = mastery.get("concepts") if isinstance(mastery, dict) else []
        if concepts:
            weak = [item for item in concepts if float(item.get("mastery", 0.55)) < 0.6]
            avg = round(sum(float(item.get("mastery", 0.55)) for item in concepts) / len(concepts), 3)
            return {"average_mastery": avg, "weak_count": len(weak), "status": "需补强" if weak else "稳定"}
        scores = [float(value.get("score", value)) for value in mastery.values()] if isinstance(mastery, dict) else []
        avg = round(sum(scores) / max(len(scores), 1), 1) if scores else 0
        return {"average_score": avg, "status": "需补强" if avg and avg < 70 else "稳定"}

    def summarize_learning_path(self, learning_path: dict[str, Any] | list[dict[str, Any]] | None) -> dict[str, Any]:
        stages = learning_path.get("stages", []) if isinstance(learning_path, dict) else learning_path or []
        return {"stage_count": len(stages), "next_step": stages[0].get("title", stages[0].get("name", "")) if stages and isinstance(stages[0], dict) else "完成循环结构补弱任务"}

    def summarize_quiz_result(self, quiz_results: list[dict[str, Any]] | dict[str, Any] | None) -> dict[str, Any]:
        rows = quiz_results if isinstance(quiz_results, list) else [quiz_results] if quiz_results else []
        scores = [float(row.get("score", 0)) for row in rows if isinstance(row, dict)]
        return {"attempt_count": len(rows), "latest_score": scores[-1] if scores else None, "average_score": round(sum(scores) / max(len(scores), 1), 1) if scores else None}

    def summarize_resource_usage(self, resource_usage: list[dict[str, Any]] | dict[str, Any] | None) -> list[dict[str, Any]]:
        rows = resource_usage if isinstance(resource_usage, list) else resource_usage.get("items", []) if isinstance(resource_usage, dict) else []
        return rows[:5] or [{"title": "while 循环条件更新专项练习", "type": "quiz", "reason": "对应薄弱知识点"}]

    def build_teacher_suggestions(self, profile: dict[str, Any], quiz_results: Any = None) -> list[str]:
        weak = profile.get("weak_points") or ["while 循环条件更新"]
        suggestions = [f"优先安排 {weak[0]} 的课堂追问和代码演示。"]
        if (profile.get("risk_level") or "medium") in {"high", "medium"}:
            suggestions.append("下一次测验后复核 DKVMN 掌握度变化，必要时降低任务难度。")
        return suggestions

    def export_markdown(self, report: dict[str, Any], output_path: str | Path | None = None) -> dict[str, Any]:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        path = Path(output_path) if output_path else self.report_dir / f"{report['report_id']}.md"
        lines = [
            f"# {report['student_name']} - {report['course_name']} 学习诊断报告",
            "",
            f"- 生成时间：{report['generated_at']}",
            f"- 报告 ID：{report['report_id']}",
            "",
            "## 画像摘要",
            str(report["profile_summary"]),
            "",
            "## 掌握度摘要",
            dumps(report["mastery_summary"]),
            "",
            "## 薄弱知识点",
            *[f"- {item}" for item in report["weak_concepts"]],
            "",
            "## 教师建议",
            *[f"- {item}" for item in report["teacher_suggestions"]],
        ]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return {"export_path": str(path), "download_url": f"/api/v1/reports/download/{path.name}", "export_format": "markdown"}

    def export_docx(self, report: dict[str, Any], output_path: str | Path | None = None) -> dict[str, Any]:
        if Document is None:
            result = self.export_markdown(report, output_path)
            result["fallback_reason"] = "python-docx 未安装，已降级导出 markdown。"
            return result
        self.report_dir.mkdir(parents=True, exist_ok=True)
        path = Path(output_path) if output_path else self.report_dir / f"{report['report_id']}.docx"
        doc = Document()
        doc.add_heading(f"{report['student_name']} - {report['course_name']} 学习诊断报告", level=1)
        doc.add_paragraph(f"生成时间：{report['generated_at']}")
        doc.add_heading("画像摘要", level=2)
        doc.add_paragraph(str(report["profile_summary"]))
        doc.add_heading("掌握度摘要", level=2)
        doc.add_paragraph(dumps(report["mastery_summary"]))
        doc.add_heading("薄弱知识点", level=2)
        for item in report["weak_concepts"]:
            doc.add_paragraph(str(item), style="List Bullet")
        doc.add_heading("教师建议", level=2)
        for item in report["teacher_suggestions"]:
            doc.add_paragraph(str(item), style="List Bullet")
        doc.save(path)
        return {"export_path": str(path), "download_url": f"/api/v1/reports/download/{path.name}", "export_format": "docx"}

    def _query(self, model: Any, item_id: int | None) -> Any:
        if not self.db or not item_id:
            return None
        return self.db.query(model).filter(model.id == item_id).first()

    def _profile_data(self, profile: StudentProfile | dict[str, Any] | None, student_id: int | str | None) -> dict[str, Any]:
        if isinstance(profile, dict):
            return profile
        if profile is None:
            return {"id": student_id, "student_name": "李明", "weak_points": ["while 循环条件更新"], "risk_level": "medium"}
        raw = loads(profile.profile_json, {})
        return {
            **raw,
            "id": profile.id,
            "student_name": profile.student_name,
            "learning_goal": profile.learning_goal,
            "weak_points": loads(profile.weak_points, raw.get("weak_points", [])),
            "dimension_scores": loads(getattr(profile, "dimension_scores", None), raw.get("dimension_scores", {})),
            "evidence_items": loads(getattr(profile, "evidence_items", None), raw.get("evidence_items", [])),
            "cognitive_state": loads(getattr(profile, "cognitive_state", None), raw.get("cognitive_state", {})),
            "risk_level": getattr(profile, "risk_level", None) or raw.get("risk_level", "medium"),
        }

    def _get(self, obj: Any, key: str, fallback: Any) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, fallback)
        return getattr(obj, key, fallback) if obj is not None else fallback


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
    dimension_scores = summary.get("dimension_scores") or {}
    cognitive_state = summary.get("cognitive_state") or {}
    citations = summary.get("citations") or summary.get("references") or []
    adjustment_log = summary.get("adjustment_log") or []
    resources = summary.get("resources") or summary.get("recommended_resources") or []
    arbitration = summary.get("teacher_arbitration") or summary.get("audit_records") or []

    if Document:
        doc = Document()
        doc.add_heading(title, level=1)
        doc.add_paragraph(f"课程：{course.title}")
        doc.add_paragraph(f"学生：{profile.student_name}")
        doc.add_paragraph(f"学习目标：{profile.learning_goal or '围绕当前章节完成学习闭环'}")
        doc.add_heading("画像摘要", level=2)
        doc.add_paragraph(str(profile_summary))
        doc.add_heading("6 维度画像", level=2)
        for name, value in (dimension_scores or {}).items():
            doc.add_paragraph(f"{name}：{value.get('score', value)}", style="List Bullet")
        doc.add_heading("DKVMN 知识掌握状态", level=2)
        for item in (cognitive_state.get("concepts") or [])[:10]:
            doc.add_paragraph(f"{item.get('name')}：{round(float(item.get('mastery', 0)) * 100)}%", style="List Bullet")
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
        doc.add_heading("RAG 引用证据", level=2)
        for item in citations or ["学生画像", "学习路径", "测评反馈", "课程知识库"]:
            doc.add_paragraph(str(item), style="List Bullet")
        doc.add_heading("路径调整历史", level=2)
        for item in adjustment_log or ["暂无路径调整记录"]:
            doc.add_paragraph(str(item), style="List Bullet")
        doc.add_heading("资源推荐", level=2)
        for item in resources or ["循环结构讲义、HTML 动画、代码案例和专项练习"]:
            doc.add_paragraph(str(item), style="List Bullet")
        doc.add_heading("审核与教师仲裁", level=2)
        for item in arbitration or ["当前为本地轻量审核记录，外部安全服务未配置时使用 fallback。"]:
            doc.add_paragraph(str(item), style="List Bullet")
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
            "## 6 维度画像",
            *[f"- {name}：{value.get('score', value)}" for name, value in (dimension_scores or {}).items()],
            "",
            "## DKVMN 知识掌握状态",
            *[f"- {item.get('name')}：{round(float(item.get('mastery', 0)) * 100)}%" for item in (cognitive_state.get("concepts") or [])[:10]],
            "",
            "## 薄弱知识点",
            *[f"- {point}" for point in (weak_points or ["循环结构综合应用"])],
            "",
            "## 测评反馈",
            str(evaluation_summary),
            "",
            "## RAG 引用证据",
            *[f"- {item}" for item in (citations or ["学生画像", "学习路径", "测评反馈", "课程知识库"])],
            "",
            "## 路径调整历史",
            *[f"- {item}" for item in (adjustment_log or ["暂无路径调整记录"])],
            "",
            "## 资源推荐",
            *[f"- {item}" for item in (resources or ["循环结构讲义、HTML 动画、代码案例和专项练习"])],
            "",
            "## 审核与教师仲裁",
            *[f"- {item}" for item in (arbitration or ["当前为本地轻量审核记录，外部安全服务未配置时使用 fallback。"])],
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
