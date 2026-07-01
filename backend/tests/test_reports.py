from pathlib import Path
from types import SimpleNamespace

from app.services.report_service import report_exists


def test_report_exists_fallback(tmp_path: Path):
    path = tmp_path / "report.md"
    path.write_text("# report", encoding="utf-8")
    report = SimpleNamespace(report_path=str(path))
    assert report_exists(report)


def test_report_missing_is_false(tmp_path: Path):
    report = SimpleNamespace(report_path=str(tmp_path / "missing.docx"))
    assert not report_exists(report)
