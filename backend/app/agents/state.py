from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    course_id: int
    student_name: str
    learning_goal: str
    current_level: str
    weak_points: list[str]
    learning_preference: str
    student_profile: dict[str, Any]
    retrieved_context: list[dict[str, Any]]
    knowledge_query: str
    knowledge_evidence: dict[str, Any]
    resource_plan: dict[str, Any]
    learning_path: dict[str, Any]
    generated_resources: list[dict[str, Any]]
    audit_result: dict[str, Any]
    quiz: dict[str, Any]
    quiz_submission: dict[str, Any]
    evaluation_result: dict[str, Any]
    report_path: str
    report_summary: dict[str, Any]
    messages: list[str]
    errors: list[str]
    course_title: str
    question: str
