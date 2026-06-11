from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any

from app.core.config import settings


class HashEmbeddingFunction:
    def __call__(self, input: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in input]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * 64
        for token in tokenize_text(text):
            digest = hashlib.md5(token.encode("utf-8")).digest()
            index = digest[0] % len(vector)
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


def tokenize_text(text: str) -> list[str]:
    lowered = text.lower()
    ascii_terms = re.findall(r"[a-z0-9_]+", lowered)
    cjk_chars = re.findall(r"[\u4e00-\u9fff]", lowered)
    cjk_terms = cjk_chars[:]
    cjk_terms.extend("".join(cjk_chars[index : index + 2]) for index in range(len(cjk_chars) - 1))
    cjk_terms.extend("".join(cjk_chars[index : index + 3]) for index in range(len(cjk_chars) - 2))
    return [term for term in [*ascii_terms, *cjk_terms] if term.strip()]


def _safe_float(value: object, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _section_title(content: str, filename: str | None = None) -> str:
    for line in content.splitlines():
        text = line.strip().strip("#").strip()
        if not text:
            continue
        if len(text) <= 60:
            return text
        break
    return filename or "课程资料片段"


def _knowledge_point(query: str, content: str, section_title: str) -> str:
    query_terms = [term for term in tokenize_text(query) if len(term) >= 2]
    content_text = content.lower()
    for term in query_terms:
        if term in content_text:
            return term
    return section_title


def _reason(query: str, content: str, score: float) -> str:
    query_terms = {term for term in tokenize_text(query) if len(term) >= 2}
    content_terms = set(tokenize_text(content))
    overlap = list(query_terms & content_terms)[:4]
    if overlap:
        return f"命中查询关键词：{'、'.join(overlap)}"
    if score >= 0.45:
        return "与问题语义向量相近，作为候选引用片段。"
    return "低相关度候选片段，仅作为补充参考。"


def _citation_key(metadata: dict[str, Any]) -> str:
    return f"{metadata.get('document_id', 'unknown')}::{metadata.get('chunk_index', 0)}"


def _normalize_item(
    *,
    course_id: int,
    query: str,
    content: str,
    metadata: dict[str, Any],
    score: float,
    rank: int,
) -> dict[str, Any]:
    filename = metadata.get("source_file")
    chunk_index = metadata.get("chunk_index", rank - 1)
    section = metadata.get("section_title") or _section_title(content, filename)
    confidence = round(_clamp(score), 4)
    citation_id = f"course-{course_id}-doc-{metadata.get('document_id', 'unknown')}-chunk-{chunk_index}"
    return {
        "rank": rank,
        "content": content,
        "snippet": content[:260],
        "source_file": filename,
        "document_id": metadata.get("document_id"),
        "chunk_index": chunk_index,
        "section_title": section,
        "knowledge_point": metadata.get("knowledge_point") or _knowledge_point(query, content, section),
        "score": round(score, 4),
        "confidence": confidence,
        "citation_id": citation_id,
        "reason": _reason(query, content, score),
    }


def _prefer_teaching_material(item: dict[str, Any], query: str) -> dict[str, Any]:
    source = str(item.get("source_file") or "")
    query_text = query.lower()
    is_question_bank = any(token in source for token in ("题库", "question_bank"))
    wants_practice = any(token in query_text for token in ("题", "练习", "测验", "考试", "quiz", "practice"))
    if is_question_bank and not wants_practice:
        adjusted_score = min(float(item.get("score") or 0), 0.52)
        item = {
            **item,
            "score": round(adjusted_score, 4),
            "confidence": round(adjusted_score, 4),
            "reason": f"{item.get('reason', '候选引用')}；题库片段作为补充证据降权。",
        }
    return item


class CourseVectorStore:
    def __init__(self) -> None:
        self.persist_dir = settings.path_from_root(settings.chroma_persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_function = HashEmbeddingFunction()

    def _collection(self, course_id: int):
        import chromadb

        client = chromadb.PersistentClient(path=str(self.persist_dir))
        return client.get_or_create_collection(
            name=f"eduagent_course_{course_id}",
            embedding_function=self.embedding_function,
            metadata={"course_id": str(course_id)},
        )

    def _fallback_path(self, course_id: int):
        return self.persist_dir / f"fallback_course_{course_id}.json"

    def _load_fallback(self, course_id: int) -> list[dict[str, Any]]:
        path = self._fallback_path(course_id)
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def _save_fallback(self, course_id: int, items: list[dict[str, Any]]) -> None:
        path = self._fallback_path(course_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    def delete_document(self, course_id: int, document_id: int) -> None:
        try:
            collection = self._collection(course_id)
            collection.delete(where={"document_id": document_id})
        except Exception:
            pass

        items = [
            item
            for item in self._load_fallback(course_id)
            if int(item.get("document_id") or -1) != int(document_id)
        ]
        self._save_fallback(course_id, items)

    def add_chunks(self, course_id: int, document_id: int, filename: str, chunks: list[str]) -> int:
        if not chunks:
            return 0
        self.delete_document(course_id, document_id)
        ids = [f"course-{course_id}-doc-{document_id}-chunk-{index}" for index in range(len(chunks))]
        metadatas = [
            {
                "course_id": course_id,
                "document_id": document_id,
                "source_file": filename,
                "chunk_index": index,
                "section_title": _section_title(chunk, filename),
            }
            for index, chunk in enumerate(chunks)
        ]
        try:
            collection = self._collection(course_id)
            if hasattr(collection, "upsert"):
                collection.upsert(ids=ids, documents=chunks, metadatas=metadatas)
            else:
                collection.add(ids=ids, documents=chunks, metadatas=metadatas)
        except Exception:
            pass
        self._upsert_fallback(course_id, document_id, filename, chunks)
        return len(chunks)

    def _upsert_fallback(self, course_id: int, document_id: int, filename: str, chunks: list[str]) -> None:
        items = [
            item
            for item in self._load_fallback(course_id)
            if int(item.get("document_id") or -1) != int(document_id)
        ]
        for index, chunk in enumerate(chunks):
            items.append(
                {
                    "content": chunk,
                    "document_id": document_id,
                    "source_file": filename,
                    "chunk_index": index,
                    "section_title": _section_title(chunk, filename),
                }
            )
        self._save_fallback(course_id, items)

    def _fallback_search(self, course_id: int, query: str, top_k: int) -> list[dict[str, Any]]:
        scored = []
        for item in self._load_fallback(course_id):
            score = self._lexical_score(query, item["content"])
            if score > 0:
                scored.append((score, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            _normalize_item(
                course_id=course_id,
                query=query,
                content=item["content"],
                metadata=item,
                score=score,
                rank=index + 1,
            )
            for index, (score, item) in enumerate(scored[: max(1, top_k)])
        ]

    def _lexical_score(self, query: str, content: str) -> float:
        query_terms = {term for term in tokenize_text(query) if len(term) >= 2}
        if not query_terms:
            return 0.0
        content_terms = set(tokenize_text(content))
        overlap = len(query_terms & content_terms)
        score = overlap / max(len(query_terms), 1)
        normalized_content = re.sub(r"\s+", "", content.lower())
        normalized_query = re.sub(r"\s+", "", query.lower())
        if normalized_query and normalized_query in normalized_content:
            score += 0.45
        for term in query_terms:
            if len(term) >= 3 and term in normalized_content:
                score += 0.04
        return round(_clamp(score), 4)

    def search(self, course_id: int, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        candidates: dict[str, dict[str, Any]] = {}
        try:
            collection = self._collection(course_id)
            result = collection.query(query_texts=[query], n_results=max(1, top_k * 6))
            documents = result.get("documents", [[]])[0]
            metadatas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]
            for rank, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances), start=1):
                score = 1 / (1 + _safe_float(distance))
                item = _normalize_item(
                    course_id=course_id,
                    query=query,
                    content=doc,
                    metadata=metadata or {},
                    score=score,
                    rank=rank,
                )
                key = _citation_key(item)
                item["vector_score"] = item["score"]
                candidates[key] = item
        except Exception:
            pass

        for item in self._fallback_search(course_id, query, top_k * 6):
            key = _citation_key(item)
            lexical_score = item["score"]
            if key in candidates:
                merged_score = round(_clamp(max(candidates[key].get("vector_score", 0), lexical_score) * 0.55 + lexical_score * 0.45), 4)
                candidates[key].update(
                    {
                        "score": merged_score,
                        "confidence": merged_score,
                        "lexical_score": lexical_score,
                        "reason": item.get("reason"),
                    }
                )
            else:
                item["lexical_score"] = lexical_score
                candidates[key] = item

        adjusted = [_prefer_teaching_material(item, query) for item in candidates.values()]
        ranked = sorted(adjusted, key=lambda item: item.get("score", 0), reverse=True)
        for index, item in enumerate(ranked, start=1):
            item["rank"] = index
        return ranked[: max(1, top_k)]


vector_store = CourseVectorStore()
