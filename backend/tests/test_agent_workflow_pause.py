from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routers import agent_workflow as workflow_router
from app.api.routers.agent_workflow import FullFlowPayload, run_full_learning_flow
from app.db.session import Base
from app.models import AgentRun, Course, GeneratedResource, LearningReport
from app.services.json_utils import loads


def test_full_flow_pauses_before_report_when_teacher_review_is_pending(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'pause.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    course = Course(title="Python 程序设计")
    db.add(course)
    db.commit()
    db.refresh(course)

    def pending_state(initial_state):
        return {
            **initial_state,
            "student_profile": {"diagnosis": "需要教师复核"},
            "knowledge_evidence": {"citation_count": 1, "confidence": 0.7},
            "retrieved_context": [{"citation_id": "c1", "content": "课程证据"}],
            "learning_path": {"stages": []},
            "resource_plan": {"coverage": ["讲义"], "items": []},
            "generated_resources": [{"resource_type": "handout", "title": "待审核讲义", "content": "待审核内容"}],
            "quiz": {"questions": []},
            "tutor_answer": {"answer": "待审核回答"},
            "evaluation_result": {},
            "audit_result": {"review_status": "blocked", "risk_level": "high"},
            "teacher_arbitration_result": {"status": "pending", "decision": None},
            "retry_count": 3,
            "status": "pending_review",
            "current_node": "TeacherArbitration",
        }

    monkeypatch.setattr(workflow_router, "run_full_learning_graph", pending_state)
    output = run_full_learning_flow(
        FullFlowPayload(
            course_id=course.id,
            student_name="张三",
            learning_goal="掌握循环结构",
            current_level="基础",
            weak_points=["while 循环"],
            learning_preference="图文",
            question="为什么会死循环？",
        ),
        db,
    )

    run = db.query(AgentRun).one()
    resource = db.query(GeneratedResource).one()
    assert output["status"] == "pending_review"
    assert output["report_id"] is None
    assert run.status == "pending_review"
    assert run.current_node == "TeacherArbitration"
    assert run.finished_at is None
    assert loads(run.state)["course_id"] == course.id
    assert resource.generation_status == "draft"
    assert resource.audit_status == "pending_review"
    assert db.query(LearningReport).count() == 0
    db.close()
