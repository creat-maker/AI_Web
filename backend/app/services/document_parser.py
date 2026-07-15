from __future__ import annotations

from pathlib import Path
from typing import Any


def _section_from_text(text: str) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    current = {"title": "正文", "paragraphs": []}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            if current["paragraphs"]:
                sections.append(current)
            current = {"title": stripped.lstrip("#").strip() or "未命名章节", "paragraphs": []}
        else:
            current["paragraphs"].append(stripped)
    if current["paragraphs"]:
        sections.append(current)
    return sections or [{"title": "正文", "paragraphs": [text[:800]] if text else []}]


def _parse_pdf(path: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        try:
            from pypdf import PdfReader  # type: ignore
        except ModuleNotFoundError:
            from PyPDF2 import PdfReader  # type: ignore
    except ModuleNotFoundError:
        return "", ["PDF 解析依赖 pypdf/PyPDF2 未安装，已保留上传记录；扫描 PDF OCR 为预留能力。"]
    try:
        reader = PdfReader(str(path))
    except Exception as exc:  # noqa: BLE001
        return "", [f"PDF 读取失败：{exc}；扫描 PDF OCR 为预留能力。"]
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            pages.append(page.extract_text() or "")
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"第 {index} 页文本提取失败：{exc}")
    if not "".join(pages).strip():
        warnings.append("未提取到可用文本，可能是扫描 PDF；OCR 接口已预留但当前未启用。")
    return "\n\n".join(pages), warnings


def _parse_docx(path: Path) -> tuple[str, list[dict[str, Any]], list[str]]:
    try:
        from docx import Document  # type: ignore
    except ModuleNotFoundError:
        return "", [], ["DOCX 解析依赖 python-docx 未安装，已返回友好 fallback。"]
    doc = Document(str(path))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    tables = []
    for table in doc.tables:
        tables.append([[cell.text.strip() for cell in row.cells] for row in table.rows])
    return "\n".join(paragraphs), tables, []


def parse_document(file_path: str) -> dict[str, Any]:
    path = Path(file_path)
    suffix = path.suffix.lower().lstrip(".") or "txt"
    warnings: list[str] = []
    tables: list[Any] = []
    text = ""
    if not path.exists():
        warnings.append("文件不存在，已返回空解析结果。")
    elif suffix == "pdf":
        text, warnings = _parse_pdf(path)
    elif suffix == "docx":
        text, tables, warnings = _parse_docx(path)
    elif suffix in {"txt", "md", "markdown"}:
        text = path.read_text(encoding="utf-8", errors="ignore")
    else:
        warnings.append(f"暂不支持 {suffix} 解析，已按纯文本尝试读取。")
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except UnicodeDecodeError:
            warnings.append("纯文本读取失败。")
    sections = _section_from_text(text)
    paragraphs = [paragraph for section in sections for paragraph in section.get("paragraphs", [])]
    return {
        "source_file": path.name,
        "file_type": suffix,
        "title": path.stem,
        "sections": sections,
        "paragraphs": paragraphs,
        "tables": tables,
        "warnings": warnings,
        "ocr_reserved": suffix == "pdf",
    }
