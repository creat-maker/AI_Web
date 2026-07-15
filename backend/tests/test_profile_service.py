from types import SimpleNamespace

from app.services.json_utils import dumps
from app.services.profile_service import (
    build_profile_visualization,
    calculate_risk_level,
    merge_profile_evidence,
    update_profile_dimensions,
)


def test_profile_update_visualization_and_risk():
    profile = {
        "student_name": "李明",
        "dimension_scores": {"知识基础": {"score": 60}},
        "evidence_items": [{"source_type": "quiz", "description": "首次测验"}],
        "profile_history": [],
    }
    result = update_profile_dimensions(profile, {"代码实操能力": 52}, [{"source_type": "quiz", "description": "while 错题"}])
    assert result["risk_level"] in {"high", "medium"}
    assert result["visualization"]["radar_chart"]
    assert result["profile_history"]


def test_profile_evidence_merge_and_risk_level():
    merged = merge_profile_evidence(
        [{"source_type": "quiz", "description": "a"}],
        [{"source_type": "quiz", "description": "a"}, {"source_type": "rag", "description": "b"}],
    )
    assert len(merged) == 2
    assert calculate_risk_level({"知识基础": {"score": 50}}, {"score": 58}) == "high"


def test_profile_visualization_from_object():
    profile = SimpleNamespace(
        id=1,
        student_name="李明",
        course_id=1,
        current_level="基础",
        learning_goal="循环",
        weak_points=dumps(["while"]),
        learning_preference="代码",
        profile_json=dumps({}),
        dimension_scores=dumps({"知识基础": {"score": 66}}),
        evidence_items=dumps([{"source_type": "quiz", "description": "e"}]),
        cognitive_state=dumps({"weak_concepts": [{"name": "while"}]}),
        profile_history=dumps([]),
        risk_level="medium",
        created_at=None,
        updated_at=None,
    )
    viz = build_profile_visualization(profile)
    assert viz["evidence_chain"]
    assert "while" in viz["cognitive_state_description"]
