from __future__ import annotations

from typing import Any


def chunk_document(parsed: dict[str, Any], chunk_size: int = 500, overlap: int = 50) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    source_file = parsed.get("source_file") or "course-material"
    index = 0
    for section in parsed.get("sections", []) or [{"title": parsed.get("title", "正文"), "paragraphs": parsed.get("paragraphs", [])}]:
        title = section.get("title") or "正文"
        text = "\n".join(str(item) for item in section.get("paragraphs", []) if item)
        if not text:
            continue
        start = 0
        while start < len(text):
            content = text[start : start + chunk_size]
            if content.strip():
                chunks.append(
                    {
                        "citation_id": f"{source_file}-{index + 1:03d}",
                        "source_file": source_file,
                        "section_title": title,
                        "page_number": section.get("page_number"),
                        "chunk_index": index,
                        "content": content.strip(),
                        "metadata": {"chunk_size": chunk_size, "overlap": overlap, "parser_warnings": parsed.get("warnings", [])},
                    }
                )
                index += 1
            if start + chunk_size >= len(text):
                break
            start += max(1, chunk_size - overlap)
    return chunks
