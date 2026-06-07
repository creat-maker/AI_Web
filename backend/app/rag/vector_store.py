from __future__ import annotations

import hashlib
import json
import math
from typing import Any

from app.core.config import settings


class HashEmbeddingFunction:
    def name(self) -> str:
        return "hash_embedding"

    def __call__(self, input: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in input]

    def embed_query(self, input: list[str]) -> list[list[float]]:
        return self(input)

    def embed_documents(self, input: list[str]) -> list[list[float]]:
        return self(input)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * 64
        for token in text.lower().split():
            digest = hashlib.md5(token.encode("utf-8")).digest()
            index = digest[0] % len(vector)
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


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

    def add_chunks(self, course_id: int, document_id: int, filename: str, chunks: list[str]) -> int:
        if not chunks:
            return 0
        try:
            collection = self._collection(course_id)
            ids = [f"course-{course_id}-doc-{document_id}-chunk-{index}" for index in range(len(chunks))]
            metadatas = [
                {"course_id": course_id, "document_id": document_id, "source_file": filename, "chunk_index": index}
                for index in range(len(chunks))
            ]
            collection.add(ids=ids, documents=chunks, metadatas=metadatas)
        except ModuleNotFoundError:
            items = self._load_fallback(course_id)
            for index, chunk in enumerate(chunks):
                items.append(
                    {
                        "content": chunk,
                        "document_id": document_id,
                        "source_file": filename,
                        "chunk_index": index,
                    }
                )
            self._save_fallback(course_id, items)
        return len(chunks)

    def search(self, course_id: int, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        try:
            collection = self._collection(course_id)
            result = collection.query(query_texts=[query], n_results=max(1, top_k))
            documents = result.get("documents", [[]])[0]
            metadatas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]
            items: list[dict[str, Any]] = []
            for doc, metadata, distance in zip(documents, metadatas, distances):
                items.append(
                    {
                        "content": doc,
                        "source_file": metadata.get("source_file"),
                        "document_id": metadata.get("document_id"),
                        "score": round(1 / (1 + float(distance)), 4),
                    }
                )
            return items
        except ModuleNotFoundError:
            query_tokens = set(query.lower().split())
            scored = []
            for item in self._load_fallback(course_id):
                content_tokens = set(item["content"].lower().split())
                overlap = len(query_tokens & content_tokens)
                if query in item["content"]:
                    overlap += 3
                scored.append((overlap, item))
            scored.sort(key=lambda pair: pair[0], reverse=True)
            return [
                {
                    "content": item["content"],
                    "source_file": item["source_file"],
                    "document_id": item["document_id"],
                    "score": round(score / max(len(query_tokens), 1), 4),
                }
                for score, item in scored[:top_k]
            ]


vector_store = CourseVectorStore()
