from __future__ import annotations

import math
import re
from collections import Counter
from typing import Protocol


class BaseEmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    def similarity(self, query: str, document: str) -> float:
        ...


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z_]+|\d+|[\u4e00-\u9fff]{2,}", text.lower())


class TfidfEmbeddingProvider:
    def embed(self, texts: list[str]) -> list[list[float]]:
        vocabulary = sorted({token for text in texts for token in _tokens(text)})
        if not vocabulary:
            return [[] for _ in texts]
        doc_freq = Counter(token for token in vocabulary for text in texts if token in set(_tokens(text)))
        vectors = []
        for text in texts:
            counts = Counter(_tokens(text))
            total = sum(counts.values()) or 1
            vectors.append([
                (counts[token] / total) * math.log((1 + len(texts)) / (1 + doc_freq[token]) + 1)
                for token in vocabulary
            ])
        return vectors

    def similarity(self, query: str, document: str) -> float:
        vectors = self.embed([query, document])
        if not vectors or not vectors[0] or not vectors[1]:
            return 0.0
        left, right = vectors
        dot = sum(a * b for a, b in zip(left, right))
        norm_left = math.sqrt(sum(a * a for a in left))
        norm_right = math.sqrt(sum(b * b for b in right))
        return round(dot / max(norm_left * norm_right, 1e-9), 4)


class SentenceTransformerEmbeddingProvider:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
            except ModuleNotFoundError as exc:
                raise RuntimeError("sentence-transformers 未安装，当前使用 TF-IDF fallback。") from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [list(row) for row in self._load().encode(texts)]

    def similarity(self, query: str, document: str) -> float:
        vectors = self.embed([query, document])
        left, right = vectors
        dot = sum(a * b for a, b in zip(left, right))
        norm_left = math.sqrt(sum(a * a for a in left))
        norm_right = math.sqrt(sum(b * b for b in right))
        return round(dot / max(norm_left * norm_right, 1e-9), 4)
