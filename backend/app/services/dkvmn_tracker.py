from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from sqlalchemy.orm import Session

from app.models import StudentProfile
from app.services.json_utils import dumps, loads


ROOT_DIR = Path(__file__).resolve().parents[3]
FALLBACK_STATE_PATH = ROOT_DIR / "backend" / "storage" / "dkvmn_memory.json"


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
        memory_dim = int(state.get("memory_dim") or 4)
        row = value_memory.setdefault(
            concept_id,
            {
                "mastery": 0.55,
                "value_vector": [0.55] * memory_dim,
                "attempts": 0,
                "correct_streak": 0,
                "wrong_streak": 0,
                "last_updated": None,
            },
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
        value_vector = row.get("value_vector")
        if not isinstance(value_vector, list) or len(value_vector) != memory_dim:
            value_vector = [float(row["mastery"])] * memory_dim
        target = 1.0 if is_correct else 0.05
        gate = min(0.32, 0.1 + abs(score_delta) * 0.5)
        row["value_vector"] = [
            round(max(0.05, min(0.99, float(value) + (target - float(value)) * gate)), 3)
            for value in value_vector
        ]
        row["attempts"] = int(row.get("attempts", 0)) + 1
        row["last_updated"] = datetime.utcnow().isoformat()
        return state

    def predict(self, state: dict[str, Any], concept_id: str) -> float:
        row = state.get("value_memory", {}).get(concept_id, {})
        vector = row.get("value_vector")
        if isinstance(vector, list) and vector:
            return round((float(row.get("mastery", 0.55)) * 0.6) + (sum(float(item) for item in vector) / len(vector) * 0.4), 3)
        return round(float(row.get("mastery", 0.55)), 3)


class DKVMNTracker:
    def __init__(self, model: DKVMNModelInterface | None = None):
        self.model = model or LightweightDKVMNModel()
        self.concept_registry = CONCEPT_REGISTRY
        self.key_memory = CONCEPT_REGISTRY
        self.memory_dim = len(next(iter(CONCEPT_REGISTRY.values()))["vector"])
        self.key_matrix = [meta["vector"] for meta in CONCEPT_REGISTRY.values()]

    def normalize_concept(self, concept_id: str | None) -> str:
        if not concept_id:
            return "for_loop"
        text = str(concept_id).strip()
        return CONCEPT_ALIASES.get(text, text if text in CONCEPT_REGISTRY else "for_loop")

    def initial_state(self) -> dict[str, Any]:
        return {
            "model": "lightweight-key-value-memory-dkvmn",
            "memory_dim": self.memory_dim,
            "concept_registry": self.concept_registry,
            "key_matrix": self.key_matrix,
            "key_memory": self.key_memory,
            "value_memory": {
                concept_id: {
                    "mastery": 0.58 if concept_id in {"for_loop", "list_iteration"} else 0.48 if concept_id in {"while_loop", "break_continue", "nested_loop"} else 0.55,
                    "value_vector": [0.58 if concept_id in {"for_loop", "list_iteration"} else 0.48 if concept_id in {"while_loop", "break_continue", "nested_loop"} else 0.55] * self.memory_dim,
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
        state.setdefault("model", "lightweight-key-value-memory-dkvmn")
        state.setdefault("memory_dim", self.memory_dim)
        state.setdefault("concept_registry", self.concept_registry)
        state.setdefault("key_matrix", self.key_matrix)
        state.setdefault("key_memory", self.key_memory)
        state.setdefault("value_memory", {})
        for concept_id in self.key_memory:
            row = state["value_memory"].setdefault(
                concept_id,
                {
                    "mastery": 0.55,
                    "value_vector": [0.55] * self.memory_dim,
                    "attempts": 0,
                    "correct_streak": 0,
                    "wrong_streak": 0,
                    "last_updated": None,
                },
            )
            if not isinstance(row.get("value_vector"), list) or len(row["value_vector"]) != self.memory_dim:
                row["value_vector"] = [float(row.get("mastery", 0.55))] * self.memory_dim
        state.setdefault("update_log", [])
        return state

    def _load_fallback_states(self) -> dict[str, Any]:
        if not FALLBACK_STATE_PATH.exists():
            return {}
        return loads(FALLBACK_STATE_PATH.read_text(encoding="utf-8"), {})

    def _save_fallback_states(self, states: dict[str, Any]) -> None:
        FALLBACK_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        FALLBACK_STATE_PATH.write_text(dumps(states), encoding="utf-8")

    def state_from_fallback(self, student_id: int | str) -> dict[str, Any]:
        states = self._load_fallback_states()
        state = states.get(str(student_id))
        return self._ensure_state(state if isinstance(state, dict) else self.initial_state())

    def persist_fallback_state(self, student_id: int | str, state: dict[str, Any]) -> None:
        states = self._load_fallback_states()
        states[str(student_id)] = state
        self._save_fallback_states(states)

    def _ensure_state(self, state: dict[str, Any] | None) -> dict[str, Any]:
        profile = type("_ProfileLike", (), {"cognitive_state": dumps(state), "profile_json": "{}"})()
        return self.state_from_profile(profile) if isinstance(state, dict) else self.initial_state()

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
        state = self._ensure_state(state) if state else self.initial_state()
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
                "mastery_before": before,
                "mastery_after": after,
                "score_delta": score_delta,
                "update_reason": "答题正确，value memory 向掌握状态靠近。" if is_correct else "答题错误，value memory 降低并记录薄弱轨迹。",
                "evidence_items": [
                    {
                        "source_type": "quiz",
                        "description": f"{self.key_memory[concept]['name']} 作答{'正确' if is_correct else '错误'}",
                        "confidence": 0.84,
                    }
                ],
                "confidence": 0.84,
            }
        )
        state["update_log"] = state["update_log"][-60:]
        return state

    def update_memory(
        self,
        student_id: int | str,
        concept_id: str,
        is_correct: bool,
        difficulty: float = 0.5,
        response_time: float = 0.0,
        score: float | None = None,
        state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        active_state = state or self.state_from_fallback(student_id)
        concept = self.normalize_concept(concept_id)
        before = self.predict_mastery(student_id, concept, active_state)
        difficulty_factor = max(0.05, min(float(difficulty or 0.5), 1.0))
        time_penalty = 0.04 if response_time and response_time > 90 else 0.0
        score_factor = ((float(score) / 100) - 0.5) * 0.2 if score is not None else 0.0
        score_delta = (0.1 + difficulty_factor * 0.08 + score_factor) * (1 if is_correct else -1)
        if not is_correct:
            score_delta -= time_penalty
        next_state = self.update(student_id, concept, is_correct, score_delta=score_delta, state=active_state)
        after = self.predict_mastery(student_id, concept, next_state)
        evidence = {
            "mastery_before": before,
            "mastery_after": after,
            "update_reason": "正确作答提升掌握概率。" if is_correct else "错误作答和响应时长共同降低掌握概率。",
            "evidence_items": [
                {"source_type": "quiz", "description": f"difficulty={difficulty_factor}; response_time={response_time}; score={score}", "confidence": 0.82}
            ],
            "confidence": 0.82,
        }
        next_state.setdefault("last_update_explanation", evidence)
        self.persist_fallback_state(student_id, next_state)
        return {**evidence, "state": next_state, "concept_id": concept}

    def predict(self, student_id: int | str, concept_id: str, state: dict[str, Any] | None = None) -> float:
        return self.model.predict(self._ensure_state(state) if state else self.initial_state(), self.normalize_concept(concept_id))

    def predict_mastery(self, student_id: int | str, concept_id: str, state: dict[str, Any] | None = None) -> float:
        active_state = state or self.state_from_fallback(student_id)
        return self.predict(student_id, concept_id, active_state)

    def get_cognitive_state(self, student_id: int | str, state: dict[str, Any] | None = None) -> dict[str, Any]:
        active_state = self._ensure_state(state) if state else self.state_from_fallback(student_id)
        return {
            "student_id": student_id,
            "model": active_state.get("model"),
            "memory_dim": active_state.get("memory_dim", self.memory_dim),
            "concepts": [
                {
                    "concept_id": concept_id,
                    "name": meta["name"],
                    "key_vector": meta["vector"],
                    **active_state.get("value_memory", {}).get(concept_id, {}),
                }
                for concept_id, meta in self.key_memory.items()
            ],
            "weak_concepts": self.get_weak_concepts_from_state(active_state),
            "strong_concepts": self.get_strong_concepts_from_state(active_state),
            "update_log": active_state.get("update_log", [])[-20:],
        }

    def get_mastery_distribution(self, student_id: int | str, state: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.get_mastery_distribution_from_state(self._ensure_state(state) if state else self.state_from_fallback(student_id))

    def get_mastery_vector(self, student_id: int | str, state: dict[str, Any] | None = None) -> dict[str, float]:
        active_state = self._ensure_state(state) if state else self.state_from_fallback(student_id)
        return {
            concept_id: self.model.predict(active_state, concept_id)
            for concept_id in self.key_memory
        }

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
        return self.get_weak_concepts_from_state(self._ensure_state(state) if state else self.state_from_fallback(student_id))

    def get_weak_concepts_from_state(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        rows = []
        for concept_id, row in state.get("value_memory", {}).items():
            mastery = float(row.get("mastery", 0.55))
            if mastery < 0.5 or int(row.get("wrong_streak", 0)) >= 2:
                rows.append({"concept_id": concept_id, "name": self.key_memory.get(concept_id, {}).get("name", concept_id), "mastery": round(mastery, 3), "wrong_streak": row.get("wrong_streak", 0)})
        return sorted(rows, key=lambda item: item["mastery"])[:5]

    def get_strong_concepts(self, student_id: int | str, state: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.get_strong_concepts_from_state(self._ensure_state(state) if state else self.state_from_fallback(student_id))

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
