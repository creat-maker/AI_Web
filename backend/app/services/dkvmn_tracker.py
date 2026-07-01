from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from sqlalchemy.orm import Session

from app.models import StudentProfile
from app.services.json_utils import dumps, loads


CONCEPT_REGISTRY: dict[str, dict[str, Any]] = {
    "python_basics": {"name": "Python 基础语法", "vector": [1.0, 0.2, 0.1, 0.1]},
    "variables": {"name": "变量与表达式", "vector": [0.9, 0.4, 0.2, 0.1]},
    "conditionals": {"name": "条件分支", "vector": [0.6, 0.8, 0.2, 0.2]},
    "for_loop": {"name": "for 循环", "vector": [0.3, 1.0, 0.5, 0.3]},
    "while_loop": {"name": "while 循环", "vector": [0.3, 0.9, 0.8, 0.3]},
    "break_continue": {"name": "break/continue", "vector": [0.2, 0.7, 0.9, 0.4]},
    "nested_loop": {"name": "循环嵌套", "vector": [0.2, 0.6, 1.0, 0.6]},
    "list_iteration": {"name": "列表遍历", "vector": [0.4, 0.7, 0.8, 0.5]},
    "algorithmic_thinking": {"name": "简单算法思维", "vector": [0.1, 0.5, 0.9, 0.9]},
    "debug_reading": {"name": "调试与代码阅读", "vector": [0.3, 0.4, 0.7, 1.0]},
}

CONCEPT_ALIASES = {
    "Python 基础语法": "python_basics",
    "变量与表达式": "variables",
    "条件分支": "conditionals",
    "for 循环": "for_loop",
    "for_loop": "for_loop",
    "while 循环": "while_loop",
    "while_loop": "while_loop",
    "break/continue": "break_continue",
    "break / continue": "break_continue",
    "循环嵌套": "nested_loop",
    "列表遍历": "list_iteration",
    "简单算法思维": "algorithmic_thinking",
    "调试与代码阅读": "debug_reading",
}


class DKVMNModelInterface(Protocol):
    def update(self, state: dict[str, Any], concept_id: str, is_correct: bool, score_delta: float) -> dict[str, Any]:
        ...

    def predict(self, state: dict[str, Any], concept_id: str) -> float:
        ...


@dataclass
class LightweightDKVMNModel:
    learn_rate: float = 0.12
    forget_rate: float = 0.08

    def update(self, state: dict[str, Any], concept_id: str, is_correct: bool, score_delta: float) -> dict[str, Any]:
        value_memory = state.setdefault("value_memory", {})
        row = value_memory.setdefault(
            concept_id,
            {"mastery": 0.55, "attempts": 0, "correct_streak": 0, "wrong_streak": 0, "last_updated": None},
        )
        current = float(row.get("mastery", 0.55))
        delta = abs(score_delta) if score_delta else (self.learn_rate if is_correct else self.forget_rate)
        if is_correct:
            current += (1 - current) * min(0.28, self.learn_rate + delta * 0.4)
            row["correct_streak"] = int(row.get("correct_streak", 0)) + 1
            row["wrong_streak"] = 0
        else:
            current -= current * min(0.24, self.forget_rate + delta * 0.35)
            row["wrong_streak"] = int(row.get("wrong_streak", 0)) + 1
            row["correct_streak"] = 0
        row["mastery"] = round(max(0.05, min(0.99, current)), 3)
        row["attempts"] = int(row.get("attempts", 0)) + 1
        row["last_updated"] = datetime.utcnow().isoformat()
        return state

    def predict(self, state: dict[str, Any], concept_id: str) -> float:
        row = state.get("value_memory", {}).get(concept_id, {})
        return round(float(row.get("mastery", 0.55)), 3)


class DKVMNTracker:
    def __init__(self, model: DKVMNModelInterface | None = None):
        self.model = model or LightweightDKVMNModel()
        self.key_memory = CONCEPT_REGISTRY

    def normalize_concept(self, concept_id: str | None) -> str:
        if not concept_id:
            return "for_loop"
        text = str(concept_id).strip()
        return CONCEPT_ALIASES.get(text, text if text in CONCEPT_REGISTRY else "for_loop")

    def initial_state(self) -> dict[str, Any]:
        return {
            "model": "lightweight-dkvmn-fallback",
            "key_memory": self.key_memory,
            "value_memory": {
                concept_id: {
                    "mastery": 0.58 if concept_id in {"for_loop", "list_iteration"} else 0.48 if concept_id in {"while_loop", "break_continue", "nested_loop"} else 0.55,
                    "attempts": 0,
                    "correct_streak": 0,
                    "wrong_streak": 0,
                    "last_updated": None,
                }
                for concept_id in self.key_memory
            },
            "update_log": [],
        }

    def state_from_profile(self, profile: StudentProfile | None) -> dict[str, Any]:
        if not profile:
            return self.initial_state()
        state = loads(profile.cognitive_state, None) if hasattr(profile, "cognitive_state") else None
        if not isinstance(state, dict):
            raw_profile = loads(profile.profile_json, {})
            state = raw_profile.get("cognitive_state") if isinstance(raw_profile, dict) else None
        if not isinstance(state, dict):
            state = self.initial_state()
        state.setdefault("key_memory", self.key_memory)
        state.setdefault("value_memory", {})
        for concept_id in self.key_memory:
            state["value_memory"].setdefault(
                concept_id,
                {"mastery": 0.55, "attempts": 0, "correct_streak": 0, "wrong_streak": 0, "last_updated": None},
            )
        state.setdefault("update_log", [])
        return state

    def persist_profile_state(self, db: Session, profile: StudentProfile, state: dict[str, Any], evidence: dict[str, Any] | None = None) -> None:
        distribution = self.get_mastery_distribution_from_state(state)
        weak = self.get_weak_concepts_from_state(state)
        strong = self.get_strong_concepts_from_state(state)
        dimensions = self.map_to_profile_dimensions(state)
        evidence_items = loads(profile.evidence_items, []) if hasattr(profile, "evidence_items") else []
        if not isinstance(evidence_items, list):
            evidence_items = []
        if evidence:
            evidence_items.append(evidence)
        profile_history = loads(profile.profile_history, []) if hasattr(profile, "profile_history") else []
        if not isinstance(profile_history, list):
            profile_history = []
        profile_history.append(
            {
                "time": datetime.utcnow().isoformat(),
                "trigger": "dkvmn_update",
                "mastery_average": distribution["average_mastery"],
                "weak_concepts": weak,
                "strong_concepts": strong,
            }
        )
        risk_level = self.risk_level(distribution["average_mastery"], weak)
        profile.cognitive_state = dumps(state)
        profile.dimension_scores = dumps(dimensions)
        profile.evidence_items = dumps(evidence_items[-30:])
        profile.profile_history = dumps(profile_history[-30:])
        profile.risk_level = risk_level
        raw_profile = loads(profile.profile_json, {})
        if isinstance(raw_profile, dict):
            raw_profile.update(
                {
                    "cognitive_state": state,
                    "dimension_scores": dimensions,
                    "evidence_items": evidence_items[-30:],
                    "profile_history": profile_history[-30:],
                    "risk_level": risk_level,
                    "weak_points": [item["name"] for item in weak] or loads(profile.weak_points, []),
                }
            )
            profile.profile_json = dumps(raw_profile)
        profile.weak_points = dumps([item["name"] for item in weak] or loads(profile.weak_points, []))
        db.commit()
        db.refresh(profile)

    def update(self, student_id: int | str, concept_id: str, is_correct: bool, score_delta: float = 0.0, state: dict[str, Any] | None = None) -> dict[str, Any]:
        concept = self.normalize_concept(concept_id)
        state = state or self.initial_state()
        before = self.model.predict(state, concept)
        state = self.model.update(state, concept, is_correct, score_delta)
        after = self.model.predict(state, concept)
        state.setdefault("update_log", []).append(
            {
                "time": datetime.utcnow().isoformat(),
                "student_id": student_id,
                "concept_id": concept,
                "concept_name": self.key_memory[concept]["name"],
                "is_correct": is_correct,
                "before": before,
                "after": after,
                "score_delta": score_delta,
            }
        )
        state["update_log"] = state["update_log"][-60:]
        return state

    def predict(self, student_id: int | str, concept_id: str, state: dict[str, Any] | None = None) -> float:
        return self.model.predict(state or self.initial_state(), self.normalize_concept(concept_id))

    def get_cognitive_state(self, student_id: int | str, state: dict[str, Any] | None = None) -> dict[str, Any]:
        active_state = state or self.initial_state()
        return {
            "student_id": student_id,
            "concepts": [
                {
                    "concept_id": concept_id,
                    "name": meta["name"],
                    **active_state.get("value_memory", {}).get(concept_id, {}),
                }
                for concept_id, meta in self.key_memory.items()
            ],
            "weak_concepts": self.get_weak_concepts_from_state(active_state),
            "strong_concepts": self.get_strong_concepts_from_state(active_state),
            "update_log": active_state.get("update_log", [])[-20:],
        }

    def get_mastery_distribution(self, student_id: int | str, state: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.get_mastery_distribution_from_state(state or self.initial_state())

    def get_mastery_distribution_from_state(self, state: dict[str, Any]) -> dict[str, Any]:
        rows = state.get("value_memory", {})
        values = [float(row.get("mastery", 0.55)) for row in rows.values()]
        average = round(sum(values) / max(len(values), 1), 3)
        return {
            "average_mastery": average,
            "high": sum(1 for value in values if value >= 0.85),
            "medium": sum(1 for value in values if 0.6 <= value < 0.85),
            "low": sum(1 for value in values if value < 0.6),
        }

    def get_weak_concepts(self, student_id: int | str, state: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.get_weak_concepts_from_state(state or self.initial_state())

    def get_weak_concepts_from_state(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        rows = []
        for concept_id, row in state.get("value_memory", {}).items():
            mastery = float(row.get("mastery", 0.55))
            if mastery < 0.5 or int(row.get("wrong_streak", 0)) >= 2:
                rows.append({"concept_id": concept_id, "name": self.key_memory.get(concept_id, {}).get("name", concept_id), "mastery": round(mastery, 3), "wrong_streak": row.get("wrong_streak", 0)})
        return sorted(rows, key=lambda item: item["mastery"])[:5]

    def get_strong_concepts(self, student_id: int | str, state: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.get_strong_concepts_from_state(state or self.initial_state())

    def get_strong_concepts_from_state(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        rows = []
        for concept_id, row in state.get("value_memory", {}).items():
            mastery = float(row.get("mastery", 0.55))
            if mastery > 0.9 or int(row.get("correct_streak", 0)) >= 3:
                rows.append({"concept_id": concept_id, "name": self.key_memory.get(concept_id, {}).get("name", concept_id), "mastery": round(mastery, 3), "correct_streak": row.get("correct_streak", 0)})
        return sorted(rows, key=lambda item: item["mastery"], reverse=True)[:5]

    def map_to_profile_dimensions(self, state: dict[str, Any]) -> dict[str, dict[str, Any]]:
        distribution = self.get_mastery_distribution_from_state(state)
        weak = self.get_weak_concepts_from_state(state)
        value_memory = state.get("value_memory", {})
        code_concepts = ["for_loop", "while_loop", "break_continue", "nested_loop", "list_iteration", "debug_reading"]
        code_score = sum(float(value_memory.get(key, {}).get("mastery", 0.55)) for key in code_concepts) / len(code_concepts)
        risk = max(0.1, min(1.0, 1 - distribution["average_mastery"] + len(weak) * 0.06))
        dimensions = {
            "知识基础": distribution["average_mastery"],
            "学习节奏": 0.68 if distribution["average_mastery"] >= 0.6 else 0.48,
            "学习偏好": 0.82,
            "代码实操能力": code_score,
            "易错知识点": max(0.1, 1 - len(weak) / 6),
            "学习风险": 1 - risk,
        }
        return {
            name: {
                "score": round(value * 100),
                "label": self.dimension_label(name, value),
                "explanation": self.dimension_explanation(name, value, weak),
                "evidence_items": [item["name"] for item in weak[:3]] if name in {"易错知识点", "学习风险", "知识基础"} else ["画像对话", "资源使用偏好", "测验作答记录"],
                "confidence": 0.78 if state.get("update_log") else 0.62,
            }
            for name, value in dimensions.items()
        }

    def dimension_label(self, name: str, value: float) -> str:
        if name == "学习风险":
            return "低风险" if value >= 0.75 else "中风险" if value >= 0.52 else "高风险"
        return "优势" if value >= 0.82 else "稳定" if value >= 0.62 else "需补强"

    def dimension_explanation(self, name: str, value: float, weak: list[dict[str, Any]]) -> str:
        if name in {"知识基础", "易错知识点", "学习风险"} and weak:
            return f"知识追踪显示 {weak[0]['name']} 掌握度偏低，需要优先补弱。"
        if name == "代码实操能力":
            return "根据循环、调试和列表遍历相关题目的掌握度估算代码实操能力。"
        return "结合画像对话、测验和资源行为形成的轻量估计。"

    def risk_level(self, average_mastery: float, weak: list[dict[str, Any]]) -> str:
        if average_mastery < 0.55 or len(weak) >= 4:
            return "high"
        if average_mastery < 0.72 or weak:
            return "medium"
        return "low"


dkvmn_tracker = DKVMNTracker()
