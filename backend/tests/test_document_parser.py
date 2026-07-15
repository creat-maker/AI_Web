from pathlib import Path

from app.services.chunk_strategy import chunk_document
from app.services.document_parser import parse_document


def test_parse_txt_and_markdown(tmp_path: Path):
    txt = tmp_path / "loop.txt"
    txt.write_text("while 循环\n变量更新", encoding="utf-8")
    md = tmp_path / "loop.md"
    md.write_text("# 循环结构\nfor 循环\n\n## while 循环\n条件更新", encoding="utf-8")

    txt_result = parse_document(str(txt))
    md_result = parse_document(str(md))

    assert txt_result["file_type"] == "txt"
    assert "变量更新" in "\n".join(txt_result["paragraphs"])
    assert md_result["sections"][0]["title"] == "循环结构"
    assert chunk_document(md_result)[0]["citation_id"]


def test_parse_markdown_sections(tmp_path: Path):
    md = tmp_path / "sections.md"
    md.write_text("# 循环结构\nfor 循环\n\n## while 循环\n条件更新", encoding="utf-8")
    result = parse_document(str(md))
    assert [section["title"] for section in result["sections"]] == ["循环结构", "while 循环"]
    assert result["paragraphs"] == ["for 循环", "条件更新"]


def test_parse_missing_docx_fallback(tmp_path: Path):
    missing = parse_document(str(tmp_path / "missing.docx"))
    assert missing["file_type"] == "docx"
    assert missing["warnings"]
    assert missing["sections"][0]["title"] == "正文"


def test_parse_invalid_pdf_fallback(tmp_path: Path):
    pdf = tmp_path / "bad.pdf"
    pdf.write_text("not a real pdf", encoding="utf-8")
    result = parse_document(str(pdf))
    assert result["file_type"] == "pdf"
    assert result["warnings"]
    assert result["ocr_reserved"]


def test_parse_empty_file_returns_stable_shape(tmp_path: Path):
    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")
    result = parse_document(str(empty))
    assert result["file_type"] == "txt"
    assert result["paragraphs"] == []
    assert result["tables"] == []
    assert result["warnings"] == []


def test_parse_unknown_extension_text_fallback(tmp_path: Path):
    raw = tmp_path / "notes.xyz"
    raw.write_text("循环变量更新", encoding="utf-8")
    result = parse_document(str(raw))
    assert result["file_type"] == "xyz"
    assert "暂不支持 xyz 解析" in result["warnings"][0]
    assert "循环变量更新" in result["paragraphs"]
