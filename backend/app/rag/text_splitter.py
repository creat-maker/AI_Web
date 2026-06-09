from __future__ import annotations

import re


def split_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """递归字符分块：优先按 markdown 标题 → 双换行 → 单换行 → 句号切分，再按字符数兜底。"""
    if not text or not text.strip():
        return []

    # Step 1: 按 markdown 标题拆分
    sections = _split_by_headers(text)

    # Step 2: 对每个 section 递归拆分
    chunks: list[str] = []
    for section in sections:
        if len(section) <= chunk_size:
            chunks.append(section)
        else:
            chunks.extend(_recursive_split(section, chunk_size, overlap))

    # Step 3: 合并过短的块
    return _merge_short_chunks(chunks, chunk_size)


def _split_by_headers(text: str) -> list[str]:
    """按 markdown 标题（# ~ ####）拆分，保留标题行。"""
    header_pattern = re.compile(r"^(#{1,4}\s+.+)$", re.MULTILINE)
    splits = header_pattern.split(text)

    if len(splits) <= 1:
        return [text.strip()] if text.strip() else []

    sections: list[str] = []
    current = splits[0].strip()
    i = 1
    while i < len(splits):
        header = splits[i].strip()
        content = splits[i + 1].strip() if i + 1 < len(splits) else ""
        section = f"{header}\n{content}".strip() if content else header
        if section:
            sections.append(section)
        i += 2

    if current:
        sections.insert(0, current)

    return sections if sections else [text.strip()]


def _recursive_split(text: str, chunk_size: int, overlap: int) -> list[str]:
    """递归按分隔符层级拆分：双换行 → 单换行 → 句号 → 字符切分。"""
    separators = ["\n\n", "\n", "。", "；", ".", ";"]

    for sep in separators:
        if sep not in text:
            continue
        parts = text.split(sep)
        chunks: list[str] = []
        current = ""
        for part in parts:
            candidate = f"{current}{sep}{part}" if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current.strip())
                if len(part) > chunk_size:
                    chunks.extend(_char_split(part, chunk_size, overlap))
                    current = ""
                else:
                    current = part
        if current:
            chunks.append(current.strip())
        return [c for c in chunks if c]

    return _char_split(text, chunk_size, overlap)


def _char_split(text: str, chunk_size: int, overlap: int) -> list[str]:
    """按字符数切分，带重叠。"""
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def _merge_short_chunks(chunks: list[str], min_size: int = 100) -> list[str]:
    """合并过短的相邻块。"""
    if not chunks:
        return []
    merged: list[str] = [chunks[0]]
    for chunk in chunks[1:]:
        if len(merged[-1]) < min_size and len(merged[-1]) + len(chunk) + 1 <= min_size * 4:
            merged[-1] = f"{merged[-1]}\n{chunk}"
        else:
            merged.append(chunk)
    return merged
