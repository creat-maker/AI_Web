from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.routers import reports as reports_router
from app.main import app
from app.services import report_service
from app.services.report_service import create_learning_report, report_exists


client = TestClient(app)


class FakeDB:
    def __init__(self):
        self.added = None

    def add(self, item):
        self.added = item

    def commit(self):
        return None

    def refresh(self, item):
        if not getattr(item, "id", None):
            item.id = 1


def test_report_exists_fallback(tmp_path: Path):
    path = tmp_path / "report.md"
    path.write_text("# report", encoding="utf-8")
    report = SimpleNamespace(report_path=str(path))
    assert report_exists(report)


def test_report_missing_is_false(tmp_path: Path):
    report = SimpleNamespace(report_path=str(tmp_path / "missing.docx"))
    assert not report_exists(report)


def test_markdown_report_generation_when_word_unavailable(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(report_service, "Document", None)
    monkeypatch.setattr(report_service.settings.__class__, "path_from_root", lambda _self, _path: tmp_path)
    db = FakeDB()
    profile = SimpleNamespace(id=1, student_name="李明", learning_goal="掌握循环结构")
    course = SimpleNamespace(id=2, title="Python 程序设计")
    report = create_learning_report(
        db,
        profile,
        course,
        {
            "profile_summary": "基础薄弱，适合代码案例。",
            "dimension_scores": {"知识基础": {"score": 62}},
            "cognitive_state": {"concepts": [{"name": "while 循环", "mastery": 0.48}]},
            "citations": ["Python 程序设计 / 循环结构章节"],
            "resources": ["while 循环讲义"],
            "teacher_arbitration": ["高风险进入教师仲裁"],
        },
    )
    content = Path(report.report_path).read_text(encoding="utf-8")
    assert report.report_path.endswith(".md")
    assert "DKVMN 知识掌握状态" in content
    assert "RAG 引用证据" in content
    assert "审核与教师仲裁" in content


def test_report_to_dict_contains_download_entry(monkeypatch):
    item = SimpleNamespace(
        id=7,
        student_profile_id=1,
        course_id=2,
        report_title="李明学习报告",
        report_path="report.md",
        report_json='{"weak_points":["while 循环"],"references":["DKVMN","RAG"],"teacher_arbitration":["pending"]}',
        created_at=None,
    )
    monkeypatch.setattr(reports_router, "report_exists", lambda _item: True)
    data = reports_router.report_to_dict(item, "Python 程序设计", "李明")
    assert data["download_enabled"]
    assert data["download_url"] == "/api/v1/reports/7/download"
    assert "evidence_chain" in data["summary"]


def test_download_missing_report_returns_404():
    response = client.get("/api/v1/reports/999999/download")
    assert response.status_code == 404
