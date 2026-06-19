from __future__ import annotations

import json
from pathlib import Path


def load_document_text(path: str) -> str:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix in {".txt", ".md", ".markdown", ".py", ".sql", ".csv"}:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".ipynb":
        return _load_ipynb(file_path)
    if suffix == ".pdf":
        return _load_pdf(file_path)
    if suffix in {".docx", ".doc"}:
        return _load_docx(file_path)
    if suffix in {".pptx", ".ppt"}:
        return _load_pptx(file_path)
    return file_path.read_text(encoding="utf-8", errors="ignore")


def _load_ipynb(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:
        return f"Notebook 解析失败：{exc}"

    texts: list[str] = [f"# {path.stem}"]
    for index, cell in enumerate(data.get("cells", []), start=1):
        cell_type = cell.get("cell_type", "cell")
        source = cell.get("source", "")
        if isinstance(source, list):
            source_text = "".join(str(item) for item in source)
        else:
            source_text = str(source)
        source_text = source_text.strip()
        if not source_text:
            continue
        if cell_type == "code":
            texts.append(f"## 代码单元 {index}\n```python\n{source_text}\n```")
        else:
            texts.append(f"## 讲解单元 {index}\n{source_text}")
    return "\n\n".join(texts)


def _load_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        return f"PDF 解析失败：{exc}"


def _load_docx(path: Path) -> str:
    try:
        from docx import Document

        doc = Document(str(path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    except Exception as exc:
        return f"Word 解析失败：{exc}"


def _load_pptx(path: Path) -> str:
    try:
        from pptx import Presentation

        prs = Presentation(str(path))
        texts: list[str] = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    texts.append(shape.text)
        return "\n".join(texts)
    except Exception as exc:
        return f"PPT 解析失败：{exc}"
