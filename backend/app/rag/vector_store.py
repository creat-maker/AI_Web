from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
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


class TFIDFEmbeddingFunction:
    """基于 TF-IDF 的轻量语义向量，无需外部模型依赖。

    - 中文按字符 bigram 分词，英文按空格分词
    - 使用 IDF 加权，区分常见词和关键词
    - 向量维度 128，比 HashEmbedding 更具区分度
    """

    DIM = 128
    _idf: dict[str, float] = {}
    _doc_count: int = 0

    def name(self) -> str:
        return "tfidf_embedding"

    def __call__(self, input: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in input]

    def embed_query(self, input: list[str]) -> list[list[float]]:
        return self(input)

    def embed_documents(self, input: list[str]) -> list[list[float]]:
        self._update_idf(input)
        return self(input)

    def _tokenize(self, text: str) -> list[str]:
        tokens: list[str] = []
        # 英文单词
        for word in re.findall(r"[a-zA-Z]{2,}", text.lower()):
            tokens.append(word)
        # 中文 bigram
        chinese = re.findall(r"[\u4e00-\u9fff]+", text)
        for segment in chinese:
            for i in range(len(segment) - 1):
                tokens.append(segment[i : i + 2])
        return tokens

    def _update_idf(self, documents: list[str]) -> None:
        doc_freq: dict[str, int] = {}
        for doc in documents:
            seen = set(self._tokenize(doc))
            for token in seen:
                doc_freq[token] = doc_freq.get(token, 0) + 1
        n = self._doc_count + len(documents)
        for token, freq in doc_freq.items():
            existing_idf = self._idf.get(token, 0)
            new_idf = math.log((n + 1) / (freq + 1)) + 1
            self._idf[token] = max(existing_idf, new_idf)
        self._doc_count = n

    def _embed(self, text: str) -> list[float]:
        tokens = self._tokenize(text)
        tf = Counter(tokens)
        total = len(tokens) or 1
        vector = [0.0] * self.DIM

        for token, count in tf.items():
            tf_val = count / total
            idf_val = self._idf.get(token, math.log(self._doc_count + 1) + 1)
            weight = tf_val * idf_val
            digest = hashlib.md5(token.encode("utf-8")).digest()
            for byte_offset in range(0, min(len(digest), 8), 2):
                index = (digest[byte_offset] * 256 + digest[byte_offset + 1]) % self.DIM
                vector[index] += weight

        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class CourseVectorStore:
    def __init__(self) -> None:
        self.persist_dir = settings.path_from_root(settings.chroma_persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        # 优先使用 TF-IDF 向量，回退到 HashEmbedding
        self.embedding_function = TFIDFEmbeddingFunction()

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
