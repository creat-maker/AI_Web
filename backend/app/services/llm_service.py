from __future__ import annotations

import json
from typing import Any

from app.core.config import settings
from app.services.mock_llm import MockLLM


class LLMService:
    def __init__(self) -> None:
        self.mock = MockLLM()

    @property
    def runtime_mode(self) -> str:
        return "mock" if settings.is_mock_mode else settings.llm_provider

    def generate_json(self, task: str, payload: dict[str, Any]) -> dict[str, Any] | list[dict[str, Any]]:
        if settings.is_mock_mode:
            return self._mock(task, payload)
        try:
            return self._call_openai_compatible(task, payload)
        except Exception:
            return self._mock(task, payload)

    def _mock(self, task: str, payload: dict[str, Any]) -> dict[str, Any] | list[dict[str, Any]]:
        if task == "profile":
            return self.mock.generate_profile(payload)
        if task == "learning_path":
            return self.mock.generate_learning_path(
                payload["profile"],
                payload["course_title"],
                payload.get("contexts", []),
                payload.get("knowledge_evidence", {}),
            )
        if task == "resource_plan":
            return self.mock.generate_resource_plan(
                payload["profile"],
                payload["learning_path"],
                payload.get("contexts", []),
                payload.get("knowledge_evidence", {}),
                payload.get("course_title", "课程"),
            )
        if task == "resources":
            return self.mock.generate_resources(
                payload["profile"],
                payload["learning_path"],
                payload.get("resource_plan", {}),
                payload.get("contexts", []),
                payload.get("knowledge_evidence", {}),
            )
        if task == "quiz":
            return self.mock.generate_quiz(payload["course_title"])
        if task == "tutor":
            return self.mock.answer_tutor(payload["question"], payload.get("contexts", []))
        if task == "evaluate":
            return self.mock.evaluate(payload["quiz"], payload["answers"], payload["profile"])
        if task == "audit":
            return self.mock.audit_generation(payload)
        return {"message": "mock result"}

    def _call_openai_compatible(self, task: str, payload: dict[str, Any]) -> dict[str, Any] | list[dict[str, Any]]:
        from openai import OpenAI

        if settings.llm_provider == "deepseek":
            client = OpenAI(api_key=settings.deepseek_api_key, base_url="https://api.deepseek.com")
            model = "deepseek-chat"
        else:
            api_key = settings.qwen_api_key or settings.dashscope_api_key
            client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
            model = "qwen-plus"

        system_prompt = (
            "你是 EduAgent Studio 的教学多智能体节点。"
            "必须只输出 JSON，不要输出 Markdown，不要编造不存在的课程资料引用。"
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps({"task": task, "payload": payload}, ensure_ascii=False)},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)


llm_service = LLMService()
