import re
from io import BytesIO
from typing import Any


def _load_docx_modules():
    try:
        from docx import Document
        from docx.oxml.ns import qn
        from docx.shared import Inches, Pt
    except Exception as exc:
        raise ValueError("当前环境未安装 DOCX 导出依赖，暂时无法导出 Word 文件") from exc

    return Document, qn, Inches, Pt


def _load_pptx_modules():
    try:
        from pptx import Presentation
        from pptx.util import Pt as PptPt
    except Exception as exc:
        raise ValueError("当前环境未安装 PPT 导出依赖，暂时无法导出 PPT 文件") from exc

    return Presentation, PptPt


class ExportService:
    @staticmethod
    def _to_text_list(value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in re.split(r"\n+|[；;]+", value) if item.strip()]

        if isinstance(value, list):
            items: list[str] = []
            for item in value:
                items.extend(ExportService._to_text_list(item))
            return items

        return []

    @staticmethod
    def _normalize_slides(data: Any) -> list[dict[str, Any]]:
        candidate = data.get("slides") if isinstance(data, dict) else data
        if not isinstance(candidate, list):
            return []

        slides: list[dict[str, Any]] = []
        for index, item in enumerate(candidate):
            if not isinstance(item, dict):
                continue

            title = str(item.get("title") or f"幻灯片 {index + 1}").strip()
            bullets = ExportService._to_text_list(item.get("bullets"))
            slides.append({
                "title": title or f"幻灯片 {index + 1}",
                "bullets": bullets or ["AI 已根据当前项目生成本页内容"],
            })

        return slides

    @staticmethod
    def _add_markdown_runs(paragraph, text: str) -> None:
        for part in re.split(r"(\*\*.*?\*\*|__.*?__)", text):
            if not part:
                continue

            is_bold = (part.startswith("**") and part.endswith("**")) or (part.startswith("__") and part.endswith("__"))
            content = part[2:-2] if is_bold else part
            if not content:
                continue

            run = paragraph.add_run(content.replace("`", ""))
            if is_bold:
                run.bold = True

    @staticmethod
    def _normalize_markdown(data: Any) -> str:
        if not isinstance(data, str):
            return ""

        normalized = data.replace("\r\n", "\n").replace("\r", "\n").strip()
        if normalized.startswith("```") and normalized.endswith("```"):
            normalized = re.sub(r"^```(?:markdown)?\s*", "", normalized)
            normalized = re.sub(r"\s*```$", "", normalized)
        return normalized.strip()

    @staticmethod
    def generate_pptx(data: Any, title: str = "织课 AI 课件") -> BytesIO:
        slides = ExportService._normalize_slides(data)
        if not slides:
            raise ValueError("当前项目暂无可导出的 PPT 内容")

        Presentation, PptPt = _load_pptx_modules()
        presentation = Presentation()
        presentation.core_properties.title = title

        for slide_data in slides:
            slide = presentation.slides.add_slide(presentation.slide_layouts[1])
            slide.shapes.title.text = slide_data["title"]

            title_frame = slide.shapes.title.text_frame.paragraphs[0]
            title_frame.font.size = PptPt(28)
            title_frame.font.bold = True

            text_frame = slide.placeholders[1].text_frame
            text_frame.clear()

            for index, bullet in enumerate(slide_data["bullets"]):
                paragraph = text_frame.paragraphs[0] if index == 0 else text_frame.add_paragraph()
                paragraph.text = bullet
                paragraph.level = 0
                paragraph.font.size = PptPt(20)

        output = BytesIO()
        presentation.save(output)
        output.seek(0)
        return output

    @staticmethod
    def generate_docx(data: Any, title: str = "织课 AI 教案") -> BytesIO:
        markdown = ExportService._normalize_markdown(data)
        if not markdown:
            raise ValueError("当前项目暂无可导出的教案内容")

        Document, qn, Inches, Pt = _load_docx_modules()
        document = Document()
        section = document.sections[0]
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.95)
        section.right_margin = Inches(0.95)

        normal_style = document.styles["Normal"]
        normal_style.font.name = "Microsoft YaHei"
        normal_style.font.size = Pt(11)
        normal_style._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")

        title_paragraph = document.add_paragraph()
        title_paragraph.style = document.styles["Title"]
        ExportService._add_markdown_runs(title_paragraph, title)

        for raw_line in markdown.split("\n"):
            line = raw_line.strip()
            if not line or line.startswith("```"):
                continue

            if line.startswith("### "):
                paragraph = document.add_heading(level=3)
                ExportService._add_markdown_runs(paragraph, line[4:].strip())
                continue

            if line.startswith("## "):
                paragraph = document.add_heading(level=2)
                ExportService._add_markdown_runs(paragraph, line[3:].strip())
                continue

            if line.startswith("# "):
                heading_text = line[2:].strip()
                if heading_text != title:
                    paragraph = document.add_heading(level=1)
                    ExportService._add_markdown_runs(paragraph, heading_text)
                continue

            bullet_match = re.match(r"^[-*+]\s+(.*)$", line)
            if bullet_match:
                paragraph = document.add_paragraph(style="List Bullet")
                ExportService._add_markdown_runs(paragraph, bullet_match.group(1).strip())
                continue

            number_match = re.match(r"^\d+[.)、]\s+(.*)$", line)
            if number_match:
                paragraph = document.add_paragraph(style="List Number")
                ExportService._add_markdown_runs(paragraph, number_match.group(1).strip())
                continue

            paragraph = document.add_paragraph()
            ExportService._add_markdown_runs(paragraph, line)

        output = BytesIO()
        document.save(output)
        output.seek(0)
        return output
