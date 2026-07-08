from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models import AgentRun, AuditLog, Course
from app.services.governance_service import apply_teacher_arbitration_decision
from app.services.json_utils import dumps, loads


def test_teacher_decision_updates_agent_run_and_audit_log(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    course = Course(title="Python 程序设计")
    db.add(course)
    db.commit()
    db.refresh(course)
    run = AgentRun(
        course_id=course.id,
        workflow_name="demo",
        input_json=dumps({"topic": "循环结构"}),
        output_json=dumps({}),
        state=dumps({"run_id": "run-contract", "retry_count": 2, "messages": []}),
        status="pending_review",
        current_node="TeacherArbitration",
        run_id="run-contract",
        retry_count=2,
        audit_result=dumps({"risk_level": "medium"}),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    result = apply_teacher_arbitration_decision(
        db,
        item=run,
        item_id="run-contract",
        decision="revise",
        teacher_comment="请回到课程范围重写",
    )

    db.refresh(run)
    assert result["next_node"] == "ResourceAgent"
    assert run.current_node == "ResourceAgent"
    assert loads(run.state)["teacher_decision_log"][0]["retry_count"] == 2
    log = db.query(AuditLog).first()
    assert log.action == "teacher_arbitration_decision"
    assert log.status == "revise"
    db.close()
