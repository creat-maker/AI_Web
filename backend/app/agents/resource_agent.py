from __future__ import annotations

from app.agents.state import AgentState
from app.services.llm_service import llm_service


def resource_agent(state: AgentState) -> AgentState:
    retry_context = state.get("retry_context") or {}
    resources = llm_service.generate_json(
        "resources",
        {
            "profile": state.get("student_profile", {}),
            "learning_path": state.get("learning_path", {}),
            "resource_plan": state.get("resource_plan", {}),
            "contexts": state.get("retrieved_context", []),
            "knowledge_evidence": state.get("knowledge_evidence", {}),
            "retry_context": retry_context,
        },
    )
    resource_items = resources if isinstance(resources, list) else resources.get("items", [])
    if retry_context:
        retry_count = int(state.get("retry_count") or 0)
        previous_versions = state.get("resource_version_history", [])
        resource_items = [
            {
                **item,
                "content_version": retry_count + 1,
                "revised_resource": True,
                "retry_context": retry_context,
                "version_history": previous_versions,
                "revision_note": "根据审核失败原因重新生成，限定课程范围并补充引用。",
            }
            for item in resource_items
        ]
    quiz = llm_service.generate_json("quiz", {"course_title": state.get("course_title", "课程")})
    return {
        **state,
        "generated_resources": resource_items,
        "resource_version_history": [
            *state.get("resource_version_history", []),
            {
                "content_version": int(state.get("retry_count") or 0) + 1,
                "retry_context": retry_context,
                "items": resource_items,
            },
        ][-10:],
        "quiz": quiz,
        "messages": [*state.get("messages", []), f"ResourceAgent 生成 {len(resource_items)} 个个性化学习资源"],
    }
