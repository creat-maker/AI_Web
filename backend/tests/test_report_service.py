from pathlib import Path

from app.services.report_service import ReportService


def test_report_service_generates_required_shape(tmp_path: Path):
    service = ReportService(report_dir=tmp_path)
    report = service.generate_student_report(
        profile={"student_name": "李明", "learning_goal": "掌握循环结构", "weak_points": ["while 循环"], "risk_level": "medium"},
        course={"title": "Python 程序设计"},
        quiz_results={"score": 72},
    )
    required = {
        "report_id",
        "student_name",
        "course_name",
        "profile_summary",
        "mastery_summary",
        "weak_concepts",
        "learning_path_summary",
        "quiz_summary",
        "resource_recommendations",
        "teacher_suggestions",
        "evidence_items",
        "generated_at",
        "export_path",
        "download_url",
    }
    assert required <= set(report)
    assert Path(report["export_path"]).exists()


def test_report_service_markdown_export_fallback(tmp_path: Path, monkeypatch):
    import app.services.report_service as module

    monkeypatch.setattr(module, "Document", None)
    service = module.ReportService(report_dir=tmp_path)
    report = service.generate_student_report(profile={"student_name": "李明"}, course={"title": "Python 程序设计"})
    assert report["fallback_reason"]
    assert report["export_format"] == "markdown"
