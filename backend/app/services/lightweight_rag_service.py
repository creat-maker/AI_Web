from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from app.services.demo_learning_service import get_demo_student


ROOT_DIR = Path(__file__).resolve().parents[3]
COURSE_KB_PATH = ROOT_DIR / "docs" / "course_kb" / "python_programming.json"


def _load_kb() -> dict[str, Any]:
    return json.loads(COURSE_KB_PATH.read_text(encoding="utf-8"))


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z_]+|\d+|[\u4e00-\u9fff]{2,}", text.lower())
    chinese_terms = [
        "递归",
        "文件",
        "异常",
        "函数",
        "列表",
        "字典",
        "集合",
        "栈",
        "队列",
        "循环",
        "分支",
        "输入",
        "输出",
        "编码",
        "csv",
        "复杂度",
        "调用栈",
        "边界",
        "练习",
        "实验",
    ]
    for term in chinese_terms:
        if term.lower() in text.lower():
            words.append(term.lower())
    return list(dict.fromkeys(words))


def _chunks() -> list[dict[str, Any]]:
    kb = _load_kb()
    rows: list[dict[str, Any]] = []
    for chapter in kb.get("chapters", []):
        for section in chapter.get("sections", []):
            content = "\n".join(
                [
                    section.get("lecture", ""),
                    " ".join(section.get("knowledgePoints", [])),
                    " ".join(section.get("exercises", [])),
                    section.get("labTask", ""),
                ]
            )
            rows.append(
                {
                    "courseId": kb.get("courseId"),
                    "courseName": kb.get("courseName"),
                    "sourceFile": section.get("sourceFile"),
                    "chapter": chapter.get("chapter"),
                    "section": section.get("section"),
                    "knowledgePoints": section.get("knowledgePoints", []),
                    "lecture": section.get("lecture", ""),
                    "exercises": section.get("exercises", []),
                    "labTask": section.get("labTask", ""),
                    "content": content,
                }
            )
    return rows


def _score_chunk(question_tokens: list[str], chunk: dict[str, Any]) -> float:
    haystack = " ".join(
        [
            chunk.get("section", ""),
            chunk.get("lecture", ""),
            chunk.get("labTask", ""),
            " ".join(chunk.get("knowledgePoints", [])),
            " ".join(chunk.get("exercises", [])),
        ]
    ).lower()
    score = 0.0
    for token in question_tokens:
        if token in haystack:
            score += 2.0 if len(token) >= 2 else 1.0
    for point in chunk.get("knowledgePoints", []):
        if point.lower() in haystack and any(token in point.lower() for token in question_tokens):
            score += 1.5
    return score


def ask_rag(question: str, course_id: str | int | None = None, student_id: str | int | None = None) -> dict[str, Any]:
    student = get_demo_student(student_id)
    profile_hint = " ".join(student.get("weak_points", [])[:3])
    tokens = _tokenize(f"{question} {profile_hint}")
    scored = []
    for chunk in _chunks():
        score = _score_chunk(tokens, chunk)
        if score > 0:
            scored.append((score, chunk))
    if not scored:
        scored = [(0.5, item) for item in _chunks()[:3]]
    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[:3]
    max_score = max(score for score, _ in top) if top else 1
    matched = [
        {
            "score": round(score / max(max_score, 1), 3),
            "sourceFile": chunk["sourceFile"],
            "chapter": chunk["chapter"],
            "section": chunk["section"],
            "snippet": chunk["lecture"][:180],
            "knowledgePoints": chunk["knowledgePoints"],
        }
        for score, chunk in top
    ]
    related_points = []
    exercises = []
    for _, chunk in top:
        for point in chunk.get("knowledgePoints", []):
            if point not in related_points:
                related_points.append(point)
        for exercise in chunk.get("exercises", []):
            if exercise not in exercises:
                exercises.append(exercise)
        if chunk.get("labTask") and chunk["labTask"] not in exercises:
            exercises.append(chunk["labTask"])
    confidence = round(min(0.95, 0.45 + math.log1p(sum(score for score, _ in top)) / 3), 2)
    primary = top[0][1]
    answer = (
        f"根据《Python 程序设计》{primary['chapter']}“{primary['section']}”的资料，"
        f"建议先抓住 {related_points[0] if related_points else '核心概念'}：{primary['lecture']} "
        f"结合{student['student_name']}的{student['profile_type']}画像，当前应优先关注"
        f"{'、'.join(student['weak_points'][:2])}。如果是在做题，先写最小可运行步骤，再检查边界条件，并用推荐练习巩固。"
    )
    citations = [
        {
            "sourceFile": item["sourceFile"],
            "chapter": item["chapter"],
            "section": item["section"],
            "snippet": item["snippet"],
        }
        for item in matched
    ]
    return {
        "question": question,
        "courseId": course_id or "python-programming",
        "studentId": student_id or "demo-student-zhangsan",
        "studentName": student["student_name"],
        "profileType": student["profile_type"],
        "answer": answer,
        "citations": citations,
        "matchedChunks": matched,
        "confidence": confidence,
        "recommendedExercises": exercises[:5],
        "relatedKnowledgePoints": related_points[:8],
        "retrievalMode": "keyword-rule-rank",
        "dataset": str(COURSE_KB_PATH.relative_to(ROOT_DIR)),
    }
