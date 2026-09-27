from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models import AgentRun, AuditLog, Course, GeneratedResource, LearningReport, StudentProfile
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
        current_user={"user_id": "teacher_001", "name": "王老师", "role": "teacher"},
        decision="revise",
        teacher_comment="请回到课程范围重写",
        decision_request_id="contract-request-0001",
        arbitration_item_id="arb-run-contract-2-0",
    )

    db.refresh(run)
    assert result["next_node"] == "ResourceAgent"
    assert run.current_node == "ResourceAgent"
    assert loads(run.state)["teacher_decision_log"][0]["retry_count"] == 2
    log = db.query(AuditLog).first()
    assert log.action == "teacher_arbitration_decision"
    assert log.status == "revise"
    db.close()


def test_teacher_decision_resumes_and_persists_artifacts(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'resume.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    course = Course(title="Python 程序设计")
    db.add(course)
    db.commit()
    db.refresh(course)
    profile = StudentProfile(student_name="张三", course_id=course.id, profile_json="{}")
    db.add(profile)
    db.commit()
    db.refresh(profile)
    resource = GeneratedResource(
        course_id=course.id,
        student_profile_id=profile.id,
        resource_type="handout",
        title="原资源",
        content="原内容",
        source_agent="ResourceAgent",
    )
    db.add(resource)
    run = AgentRun(
        course_id=course.id,
        student_profile_id=profile.id,
        workflow_name="full-learning-flow",
        input_json=dumps({"student_name": "张三"}),
        output_json=dumps({}),
        state=dumps(
            {
                "run_id": "run-resume-db",
                "course_id": course.id,
                "student_name": "张三",
                "generated_resources": [{"resource_type": "handout", "title": "原资源", "content": "原内容"}],
                "audit_result": {"risk_level": "medium", "review_status": "needs_review"},
                "teacher_arbitration_result": {"status": "pending"},
                "retry_count": 3,
                "messages": [],
            }
        ),
        status="pending_review",
        current_node="TeacherArbitration",
        run_id="run-resume-db",
        retry_count=3,
        audit_result=dumps({"risk_level": "medium"}),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    def complete(state):
        return {
            **state,
            "status": "success",
            "current_node": "ReporterAgent",
            "generated_resources": [{"resource_type": "handout", "title": "修订资源", "content": "教师意见驱动的重写内容"}],
            "report_path": str(tmp_path / "agent-report.docx"),
            "report_summary": {"audit_status": "passed"},
        }

    monkeypatch.setattr("app.agents.graph.continue_after_teacher_arbitration", complete)
    result = apply_teacher_arbitration_decision(
        db,
        item=run,
        item_id=run.run_id,
        current_user={"user_id": "teacher_001", "name": "王老师", "role": "teacher"},
        decision="revise",
        teacher_comment="补充课程引用后重写",
        decision_request_id="contract-request-0002",
        arbitration_item_id="arb-run-resume-db-3-0",
    )

    db.refresh(run)
    db.refresh(resource)
    assert result["run_status"] == "success"
    assert run.status == "success"
    assert run.current_node == "ReporterAgent"
    assert run.finished_at is not None
    assert resource.content == "教师意见驱动的重写内容"
    assert resource.audit_status == "passed"
    assert db.query(LearningReport).count() == 1
    db.close()
