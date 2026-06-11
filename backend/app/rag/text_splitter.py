from __future__ import annotations

import re


def split_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    lines = _normalize_lines(text)
    if not lines:
        return []

    sections = _sections_from_lines(lines)
    chunks: list[str] = []
    current = ""

    for section in sections:
        if len(section) > chunk_size:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_split_oversized(section, chunk_size, overlap))
            continue

        candidate = f"{current}\n\n{section}" if current else section
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            chunks.append(current)
            current = section

    if current:
        chunks.append(current)

    return [chunk.strip() for chunk in chunks if chunk.strip()]


def _normalize_lines(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return [line.strip() for line in normalized.split("\n") if line.strip()]


def _sections_from_lines(lines: list[str]) -> list[str]:
    sections: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        if _is_heading(line) and current:
            sections.append(current)
            current = [line]
        else:
            current.append(line)

    if current:
        sections.append(current)

    return ["\n".join(section) for section in sections]


def _is_heading(line: str) -> bool:
    if re.match(r"^#{1,6}\s+\S+", line):
        return True
    if re.match(r"^(第[一二三四五六七八九十0-9]+[章节讲]|[0-9]+(\.[0-9]+){0,3})[、.．\s]", line):
        return True
    return len(line) <= 40 and line.endswith(("：", ":"))


def _split_oversized(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    safe_overlap = min(max(overlap, 0), max(chunk_size // 3, 1))
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(0, end - safe_overlap)
    return chunks
