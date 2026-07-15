from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

from app.services.curriculum_constraint import check_curriculum_alignment
from app.services.demo_learning_service import get_demo_student
from app.services.embedding_interface import TfidfEmbeddingProvider


ROOT_DIR = Path(__file__).resolve().parents[3]
COURSE_KB_PATH = ROOT_DIR / "docs" / "course_kb" / "python_programming.json"
INSUFFICIENT_EVIDENCE_MESSAGE = "当前课程知识库依据不足，建议先查看循环结构章节或请教师复核。"


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z_]+|\d+|[\u4e00-\u9fff]{2,}", text.lower())
    important_terms = [
        "for",
        "while",
        "break",
        "continue",
        "循环",
        "循环结构",
        "循环嵌套",
        "死循环",
        "变量更新",
        "条件更新",
        "终止条件",
        "输出结果",
    ]
    lowered = text.lower()
    for term in important_terms:
        if term.lower() in lowered:
            tokens.append(term.lower())
    return list(dict.fromkeys(tokens))


def _score_chunk(question_tokens: list[str], chunk: dict[str, Any]) -> float:
    haystack = " ".join(
        [
            chunk.get("chapter", ""),
            chunk.get("section", ""),
            chunk.get("lecture", ""),
            chunk.get("labTask", ""),
            " ".join(chunk.get("knowledgePoints", [])),
            " ".join(chunk.get("exercises", [])),
        ]
    ).lower()
    score = 0.0
    for token in question_tokens:
        if token and token in haystack:
            score += 2.0 if len(token) >= 2 else 1.0
    for point in chunk.get("knowledgePoints", []):
        point_text = str(point).lower()
        if any(token in point_text for token in question_tokens):
            score += 1.5
    return score


def _hybrid_score(question: str, question_tokens: list[str], chunk: dict[str, Any], provider: TfidfEmbeddingProvider) -> dict[str, float]:
    lexical = _score_chunk(question_tokens, chunk)
    vector = provider.similarity(question, chunk.get("content", ""))
    is_exercise = bool(chunk.get("exercises"))
    non_practice_query = not any(token in question for token in ["练习", "题", "作业", "测验"])
    penalty = 0.82 if is_exercise and non_practice_query else 1.0
    fused = (lexical * 0.65 + vector * 8 * 0.35) * penalty
    return {"lexical_score": round(lexical, 4), "vector_score": round(vector, 4), "fusion_score": round(fused, 4)}


def _risk_from_confidence(confidence: float) -> str:
    if confidence >= 0.8:
        return "低"
    if confidence >= 0.5:
        return "中"
    return "高"


def _next_step(related_points: list[str], confidence: float) -> str:
    if confidence < 0.5:
        return "先查看循环结构章节，重点复习 while 循环条件更新，再请教师确认当前问题是否需要补充资料。"
    if any("while" in point.lower() or "条件" in point for point in related_points):
        return "建议优先完成 while 循环条件更新专项练习，并写出前三轮变量变化。"
    if any("嵌套" in point for point in related_points):
        return "建议用变量变化表复盘循环嵌套，再完成一个九九乘法表补全练习。"
    if any("break" in point.lower() or "continue" in point.lower() for point in related_points):
        return "建议完成 break / continue 输出判断题，重点区分跳出循环和跳过本轮。"
    return "建议先完成循环结构基础讲解，再进入代码实操练习。"


class LightweightRAGService:
    def __init__(
        self,
        kb_path: Path | None = None,
        course_retriever: Callable[[int, str, int], list[dict[str, Any]]] | None = None,
    ):
        self.kb_path = kb_path or COURSE_KB_PATH
        self.embedding_provider = TfidfEmbeddingProvider()
        self.course_retriever = course_retriever
        self._index: list[dict[str, Any]] = []
        self.parser_warnings: list[str] = []

    @staticmethod
    def _numeric_course_id(course_id: str | int | None) -> int | None:
        try:
            value = int(str(course_id))
        except (TypeError, ValueError):
            return None
        return value if value > 0 else None

    def _retrieve_course_vectors(
        self,
        query: str,
        top_k: int,
        course_id: str | int | None,
    ) -> list[dict[str, Any]]:
        numeric_course_id = self._numeric_course_id(course_id)
        if numeric_course_id is None:
            return []
        retriever = self.course_retriever
        if retriever is None:
            from app.rag.retriever import retrieve_course_context

            retriever = retrieve_course_context
        try:
            raw_items = retriever(numeric_course_id, query, top_k)
        except Exception as exc:  # pragma: no cover - external vector backend varies by environment
            self.parser_warnings.append(f"course vector retrieval failed: {exc}")
            return []

        normalized: list[dict[str, Any]] = []
        for rank, item in enumerate(raw_items, start=1):
            content = str(item.get("content") or item.get("snippet") or "")
            if not content.strip():
                continue
            score = max(0.0, min(1.0, float(item.get("confidence", item.get("score", 0)) or 0)))
            source_file = str(item.get("source_file") or item.get("sourceFile") or "课程知识库")
            section = str(item.get("section_title") or item.get("section") or source_file)
            knowledge_point = str(item.get("knowledge_point") or section)
            normalized.append(
                {
                    **item,
                    "rank": rank,
                    "score": score,
                    "confidence": score,
                    "fusion_score": score,
                    "vector_score": float(item.get("vector_score", score) or score),
                    "lexical_score": float(item.get("lexical_score", 0) or 0),
                    "sourceFile": source_file,
                    "source_file": source_file,
                    "chapter": str(item.get("chapter") or section),
                    "section": section,
                    "section_title": section,
                    "page_number": item.get("page_number"),
                    "citation_id": item.get("citation_id") or f"course-{numeric_course_id}-chunk-{rank}",
                    "snippet": str(item.get("snippet") or content[:260]),
                    "content": content,
                    "knowledgePoints": item.get("knowledgePoints") or [knowledge_point],
                    "exercises": item.get("exercises") or [],
                    "retrieval_source": "course_vector_store",
                }
            )
        return normalized

    def load_course_kb(self, course_id: str | int | None = None) -> dict[str, Any]:
        if not self.kb_path.exists():
            self.parser_warnings = [f"knowledge base not found: {self.kb_path}"]
            return {"courseId": course_id or "python-programming", "courseName": "Python 程序设计", "chapters": []}
        kb = json.loads(self.kb_path.read_text(encoding="utf-8"))
        self.parser_warnings = kb.get("parser_warnings", []) if isinstance(kb.get("parser_warnings"), list) else []
        return kb

    def build_index(self, course_id: str | int | None = None) -> list[dict[str, Any]]:
        kb = self.load_course_kb(course_id)
        rows: list[dict[str, Any]] = []
        for chapter in kb.get("chapters", []):
            for section in chapter.get("sections", []):
                knowledge_points = section.get("knowledgePoints", [])
                exercises = section.get("exercises", [])
                content = "\n".join(
                    [
                        section.get("lecture", ""),
                        " ".join(knowledge_points),
                        " ".join(exercises),
                        section.get("labTask", ""),
                    ]
                )
                rows.append(
                    {
                        "courseId": kb.get("courseId", "python-programming"),
                        "courseName": kb.get("courseName", "Python 程序设计"),
                        "sourceFile": section.get("sourceFile", self.kb_path.name),
                        "chapter": chapter.get("chapter", ""),
                        "section": section.get("section", ""),
                        "learning_objective": section.get("learningObjective") or section.get("objective") or "",
                        "prerequisite": section.get("prerequisite") or chapter.get("prerequisite") or "",
                        "knowledgePoints": knowledge_points,
                        "lecture": section.get("lecture", ""),
                        "exercises": exercises,
                        "labTask": section.get("labTask", ""),
                        "content": content,
                    }
                )
        self._index = rows
        return rows

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        course_id: str | int | None = None,
        topic: str | None = None,
    ) -> dict[str, Any]:
        search_text = f"{query} {topic or ''}"
        vector_items = self._retrieve_course_vectors(search_text, top_k, course_id)
        if vector_items:
            aligned = self.rerank_by_curriculum_constraint(search_text, vector_items)
            return {
                "query": query,
                "retrieved_chunks": aligned,
                "matchedChunks": aligned,
                "citations": self._citations(aligned),
                "parser_warnings": self.parser_warnings,
                "retrieval_mode": "course-vector-hybrid",
                "fallback_used": False,
            }

        rows = self._index or self.build_index(course_id)
        tokens = _tokenize(search_text)
        scored = []
        for chunk in rows:
            if course_id and str(chunk.get("courseId")) != str(course_id):
                continue
            scores = _hybrid_score(search_text, tokens, chunk, self.embedding_provider)
            if scores["fusion_score"] > 0:
                scored.append((scores["fusion_score"], chunk, scores))
        scored.sort(key=lambda item: item[0], reverse=True)
        top = scored[:top_k]
        if not top and rows:
            top = [(0.1, item, {"lexical_score": 0.1, "vector_score": 0.0, "fusion_score": 0.1}) for item in rows[:top_k]]
        max_score = max((score for score, _, _ in top), default=1)
        retrieved = [
            {
                "score": round(score / max(max_score, 1), 3),
                "confidence": round(score / max(max_score, 1), 3),
                **scores,
                "sourceFile": chunk["sourceFile"],
                "source_file": chunk["sourceFile"],
                "chapter": chunk["chapter"],
                "section": chunk["section"],
                "section_title": chunk["section"],
                "page_number": None,
                "citation_id": f"{chunk['sourceFile']}-{index + 1:03d}",
                "snippet": chunk["lecture"][:180],
                "content": chunk["content"][:500],
                "knowledgePoints": chunk["knowledgePoints"],
                "learning_objective": chunk.get("learning_objective", ""),
                "prerequisite": chunk.get("prerequisite", ""),
            }
            for index, (score, chunk, scores) in enumerate(top)
        ]
        aligned = self.rerank_by_curriculum_constraint(search_text, retrieved)
        return {
            "query": query,
            "retrieved_chunks": aligned,
            "matchedChunks": aligned,
            "citations": self._citations(aligned),
            "parser_warnings": self.parser_warnings,
            "retrieval_mode": "hybrid-tfidf-json-fallback",
            "fallback_used": True,
        }

    def rerank_by_curriculum_constraint(self, query: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        checked = []
        for chunk in chunks:
            alignment = check_curriculum_alignment(
                f"{query} {chunk.get('content', '')}",
                evidence_items=[{"citation_id": chunk.get("citation_id")}],
                course=str(chunk.get("courseName") or "Python 程序设计"),
                chapter=str(chunk.get("chapter") or ""),
                section=str(chunk.get("section") or chunk.get("section_title") or ""),
                learning_objective=str(chunk.get("learning_objective") or ""),
                prerequisite=str(chunk.get("prerequisite") or ""),
            )
            checked.append({**chunk, "curriculum_alignment": alignment})
        return sorted(
            checked,
            key=lambda item: (
                float(item["curriculum_alignment"].get("curriculum_alignment_score", 0)),
                float(item.get("fusion_score", 0)),
            ),
            reverse=True,
        )

    def answer_with_citations(
        self,
        query: str,
        top_k: int = 5,
        course_id: str | int | None = None,
        topic: str | None = None,
    ) -> dict[str, Any]:
        retrieval = self.retrieve(query, top_k=top_k, course_id=course_id, topic=topic)
        chunks = retrieval["retrieved_chunks"]
        if not chunks:
            return self.fallback_answer(query, "no_retrieved_chunks")
        confidence_values = [max(0.0, min(1.0, float(item.get("confidence", item.get("score", 0)) or 0))) for item in chunks]
        top_confidence = max(confidence_values, default=0.0)
        mean_confidence = sum(confidence_values[:3]) / max(len(confidence_values[:3]), 1)
        confidence = round(min(0.95, 0.15 + top_confidence * 0.55 + mean_confidence * 0.2 + min(len(chunks), 5) * 0.02), 2)
        primary = chunks[0]
        points = []
        exercises = []
        for chunk in chunks:
            for point in chunk.get("knowledgePoints", []):
                if point not in points:
                    points.append(point)
            for exercise in chunk.get("exercises", []):
                if exercise not in exercises:
                    exercises.append(exercise)
        answer = (
            f"根据《Python 程序设计》{primary.get('chapter')}「{primary.get('section')}」的资料，"
            f"建议先理解 {points[0] if points else '循环结构'}。{primary.get('snippet') or primary.get('content', '')[:160]}"
        )
        alignment = check_curriculum_alignment(f"{query} {answer}", evidence_items=retrieval["citations"])
        if alignment["is_out_of_curriculum"]:
            answer = (
                f"{alignment['boundary_warning']} 当前知识库仅支持 Python 程序设计课程答疑，"
                "你可以改问循环、条件、列表遍历或代码调试相关问题。"
            )
            fallback_reason = "out_of_curriculum"
        elif confidence < 0.5:
            answer = INSUFFICIENT_EVIDENCE_MESSAGE
            fallback_reason = "low_retrieval_confidence"
        else:
            fallback_reason = None
        return {
            "answer": answer,
            "citations": retrieval["citations"],
            "retrieved_chunks": chunks,
            "matchedChunks": chunks,
            "confidence": confidence,
            "parser_warnings": retrieval["parser_warnings"],
            "curriculum_alignment": alignment,
            "curriculum_alignment_score": alignment["curriculum_alignment_score"],
            "alignment_breakdown": alignment["alignment_breakdown"],
            "fallback_reason": fallback_reason,
            "recommendedExercises": exercises[:5],
            "relatedKnowledgePoints": points[:8],
            "retrieval_mode": retrieval["retrieval_mode"],
            "fallback_used": retrieval["fallback_used"],
        }

    def fallback_answer(self, query: str, fallback_reason: str = "insufficient_evidence") -> dict[str, Any]:
        alignment = check_curriculum_alignment(query, evidence_items=[])
        return {
            "answer": INSUFFICIENT_EVIDENCE_MESSAGE,
            "citations": [],
            "retrieved_chunks": [],
            "matchedChunks": [],
            "confidence": 0.0,
            "parser_warnings": self.parser_warnings,
            "curriculum_alignment": alignment,
            "curriculum_alignment_score": alignment["curriculum_alignment_score"],
            "alignment_breakdown": alignment["alignment_breakdown"],
            "fallback_reason": fallback_reason,
            "retrieval_mode": "hybrid-tfidf-json-fallback",
            "fallback_used": True,
        }

    def _citations(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "citation_id": item.get("citation_id"),
                "sourceFile": item.get("sourceFile") or item.get("source_file"),
                "source_file": item.get("source_file") or item.get("sourceFile"),
                "chapter": item.get("chapter"),
                "section": item.get("section") or item.get("section_title"),
                "section_title": item.get("section_title") or item.get("section"),
                "page_number": item.get("page_number"),
                "confidence": item.get("confidence", item.get("score", 0)),
                "snippet": item.get("snippet") or str(item.get("content", ""))[:260],
                "document_id": item.get("document_id"),
                "chunk_index": item.get("chunk_index"),
            }
            for item in chunks
        ]


def ask_rag(
    question: str,
    course_id: str | int | None = None,
    student_id: str | int | None = None,
    *,
    course_retriever: Callable[[int, str, int], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    student = get_demo_student(student_id)
    profile_hint = " ".join(student.get("weak_points", [])[:3])
    service = LightweightRAGService(course_retriever=course_retriever)
    result = service.answer_with_citations(question, top_k=5, course_id=course_id, topic=profile_hint)
    confidence = float(result.get("confidence", 0))
    low_evidence_risk = _risk_from_confidence(confidence)
    citations = result.get("citations", [])
    matched = result.get("retrieved_chunks", [])
    related_points = result.get("relatedKnowledgePoints", [])
    exercises = result.get("recommendedExercises", [])
    curriculum_check = result.get("curriculum_alignment") or check_curriculum_alignment(
        f"{question} {result.get('answer', '')}",
        evidence_items=citations,
        target_level=student.get("current_level") or "基础补弱",
    )
    answer = result.get("answer", INSUFFICIENT_EVIDENCE_MESSAGE)
    if curriculum_check.get("is_out_of_curriculum"):
        low_evidence_risk = "高"
    if confidence >= 0.5 and not curriculum_check.get("is_out_of_curriculum"):
        answer = (
            f"{answer} 结合{student['student_name']}当前学习情况，"
            f"下一步可以围绕{'、'.join(student['weak_points'][:2])}进行专项巩固。"
        )
    primary = matched[0] if matched else {"chapter": "循环结构", "section": "循环结构"}
    evidence_summary = (
        f"已匹配 {len(citations)} 条课程资料，主要来自《Python 程序设计》{primary.get('chapter')} / {primary.get('section')}。"
        if confidence >= 0.5 and citations and not curriculum_check.get("is_out_of_curriculum")
        else INSUFFICIENT_EVIDENCE_MESSAGE
    )
    suggested_actions = [
        _next_step(related_points, confidence),
        "查看引用片段并完成 2 道循环结构巩固题。",
    ]
    if curriculum_check["is_out_of_curriculum"]:
        suggested_actions.insert(0, "问题可能超出本课程范围，请先回到 Python 循环结构章节。")
    return {
        "question": question,
        "courseId": course_id or "python-programming",
        "studentId": student_id or "demo-basic",
        "studentName": student["student_name"],
        "profileType": student["profile_type"],
        "answer": answer,
        "citations": citations,
        "matchedChunks": matched,
        "retrieved_chunks": matched,
        "confidence": confidence,
        "parser_warnings": result.get("parser_warnings", []),
        "curriculum_alignment": curriculum_check,
        "fallback_reason": result.get("fallback_reason"),
        "curriculum_alignment_score": curriculum_check["curriculum_alignment_score"],
        "alignment_breakdown": curriculum_check["alignment_breakdown"],
        "matched_objectives": curriculum_check["matched_objectives"],
        "out_of_scope_terms": curriculum_check["out_of_scope_terms"],
        "evidence_coverage_score": curriculum_check["evidence_coverage_score"],
        "retrieved_evidence_coverage": curriculum_check["retrieved_evidence_coverage"],
        "is_out_of_curriculum": curriculum_check["is_out_of_curriculum"],
        "boundary_warning": curriculum_check["boundary_warning"],
        "suggested_actions": list(dict.fromkeys([*suggested_actions, *curriculum_check.get("suggested_actions", [])])),
        "retrieval_debug": {
            "top_k": 5,
            "retrieval_mode": result.get("retrieval_mode", "hybrid-tfidf-json-fallback"),
            "chroma_status": "course_vector_store" if result.get("retrieval_mode") == "course-vector-hybrid" else "fallback_json_keyword",
            "scores": [
                {
                    "citation_id": item["citation_id"],
                    "vector_score": item["vector_score"],
                    "lexical_score": item["lexical_score"],
                    "fusion_score": item["fusion_score"],
                }
                for item in matched
            ],
            "curriculum_check": curriculum_check,
            "json_fallback": bool(result.get("fallback_used", True)),
        },
        "lowEvidenceRisk": low_evidence_risk,
        "evidenceSummary": evidence_summary,
        "reviewSuggestion": "依据不足，建议教师补充循环结构章节资料或复核回答。" if low_evidence_risk == "高" else "依据相对充分，可结合课堂要求复核后使用。",
        "recommendedExercises": exercises[:5],
        "relatedKnowledgePoints": related_points[:8] or ["while 循环条件更新", "循环嵌套变量变化", "break / continue 区分"],
        "nextStep": _next_step(related_points, confidence),
        "retrievalMode": result.get("retrieval_mode", "hybrid-tfidf-json-fallback"),
        "fallbackUsed": bool(result.get("fallback_used", True)),
        "dataset": str(COURSE_KB_PATH.relative_to(ROOT_DIR)),
    }
