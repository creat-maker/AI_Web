import json
import zipfile
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree

OCR_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}
_OCR_ENGINE = None


def _clean_lines(lines: Iterable[str]) -> str:
    cleaned = [line.strip() for line in lines if line and line.strip()]
    return "\n".join(cleaned)


def _get_ocr_engine():
    global _OCR_ENGINE
    if _OCR_ENGINE is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
        except Exception as exc:
            raise ValueError("当前环境未安装图片 OCR 依赖，暂时无法解析图片附件") from exc

        try:
            _OCR_ENGINE = RapidOCR()
        except Exception as exc:
            raise ValueError("图片 OCR 引擎初始化失败，请检查 rapidocr_onnxruntime 运行环境") from exc
    return _OCR_ENGINE


def _extract_ocr_result(image_input: str | bytes) -> str:
    engine = _get_ocr_engine()
    result, _ = engine(image_input)
    if not result:
        return ""

    lines: list[str] = []
    for item in result:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        candidate = item[1]
        if isinstance(candidate, str):
            lines.append(candidate)
            continue
        if isinstance(candidate, (list, tuple)) and candidate and isinstance(candidate[0], str):
            lines.append(candidate[0])
    return _clean_lines(lines)


def _extract_pdf_text(file_path: str) -> str:
    try:
        import fitz
    except Exception as exc:
        raise ValueError("当前环境未安装 PDF 解析依赖，暂时无法解析 PDF 附件") from exc

    with fitz.open(file_path) as document:
        page_texts: list[str] = []
        for index, page in enumerate(document, start=1):
            page_text = page.get_text("text").strip()
            normalized = "".join(page_text.split())
            if len(normalized) < 20:
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                ocr_text = _extract_ocr_result(pixmap.tobytes("png"))
                combined = "\n".join(part for part in [page_text, ocr_text] if part.strip())
            else:
                combined = page_text

            if combined.strip():
                page_texts.append(f"【第{index}页】\n{combined.strip()}")
        return "\n\n".join(page_texts)


def _extract_docx_text(file_path: str) -> str:
    try:
        from docx import Document
    except Exception as exc:
        raise ValueError("当前环境未安装 DOCX 解析依赖，暂时无法解析 Word 附件") from exc

    document = Document(file_path)
    lines: list[str] = [paragraph.text for paragraph in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                lines.append(" | ".join(cells))
    return _clean_lines(lines)


def _extract_plain_text(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8", errors="ignore").strip()


def _extract_json_text(file_path: str) -> str:
    raw = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    try:
        return json.dumps(json.loads(raw), ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return raw.strip()


def _extract_pptx_text(file_path: str) -> str:
    slide_texts: list[str] = []
    with zipfile.ZipFile(file_path) as archive:
        slide_names = sorted(
            name for name in archive.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        )
        for slide_name in slide_names:
            with archive.open(slide_name) as handle:
                root = ElementTree.fromstring(handle.read())
            texts = [
                node.text.strip()
                for node in root.iter()
                if node.tag.endswith('}t') and node.text and node.text.strip()
            ]
            if texts:
                slide_texts.append("\n".join(texts))
    return "\n\n".join(slide_texts)


def _extract_image_text(file_path: str) -> str:
    return _extract_ocr_result(file_path)


def extract_text_from_file(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf_text(file_path)
    if suffix == ".docx":
        return _extract_docx_text(file_path)
    if suffix == ".pptx":
        return _extract_pptx_text(file_path)
    if suffix in {".txt", ".md", ".csv"}:
        return _extract_plain_text(file_path)
    if suffix == ".json":
        return _extract_json_text(file_path)
    if suffix in OCR_IMAGE_SUFFIXES:
        return _extract_image_text(file_path)

    raise ValueError(f"暂不支持解析 {suffix or '未知'} 类型文件")
