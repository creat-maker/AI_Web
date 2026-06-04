from __future__ import annotations

from app.rag.vector_store import vector_store


def retrieve_course_context(course_id: int, query: str, top_k: int = 5) -> list[dict]:
    return vector_store.search(course_id=course_id, query=query, top_k=top_k)
