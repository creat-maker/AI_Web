from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.graph import run_full_learning_graph
from app.db.session import get_db
from app.models import AgentRun, Course, GeneratedResource, LearningPath, LearningReport, Quiz, StudentProfile
from app.services.json_utils import dumps, loads


router = APIRouter(prefix="/agent-workflow", tags=["agent-workflow"])


class FullFlowPayload(BaseModel):
    course_id: int
    student_name: str
    current_level: str
    learning_goal: str
    weak_points: list[str]
    learning_preference: str
    question: str | None = None


@router.post("/run-full-learning-flow")
def run_full_learning_flow(payload: FullFlowPayload, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    run = AgentRun(
        course_id=payload.course_id,
        workflow_name="full-learning-flow",
        input_json=payload.model_dump_json(),
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        state = run_full_learning_graph(
            {
                **payload.model_dump(),
                "course_title": course.title,
                "messages": [],
                "errors": [],
            }
        )

        profile = StudentProfile(
            student_name=payload.student_name,
            course_id=payload.course_id,
            current_level=payload.current_level,
            learning_goal=payload.learning_goal,
            weak_points=dumps(payload.weak_points),
            learning_preference=payload.learning_preference,
            profile_json=dumps(state.get("student_profile", {})),
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

        path = LearningPath(
            student_profile_id=profile.id,
            course_id=payload.course_id,
            path_json=dumps(state.get("learning_path", {})),
        )
        db.add(path)

        resources = []
        for item in state.get("generated_resources", []):
            resource = GeneratedResource(
                course_id=payload.course_id,
                student_profile_id=profile.id,
                resource_type=item.get("resource_type", "resource"),
                title=item.get("title", "学习资源"),
                content=item.get("content", ""),
                difficulty=item.get("difficulty"),
                source_agent="ResourceAgent",
            )
            db.add(resource)
            resources.append(resource)

        quiz = Quiz(
            course_id=payload.course_id,
            student_profile_id=profile.id,
            quiz_json=dumps(state.get("quiz", {})),
        )
        db.add(quiz)

        report = LearningReport(
            student_profile_id=profile.id,
            course_id=payload.course_id,
            report_title=f"{payload.student_name} - {course.title} 学习报告",
            report_path=state.get("report_path", ""),
            report_json=dumps(state.get("report_summary", {})),
        )
        db.add(report)
        db.commit()
        for resource in resources:
            db.refresh(resource)
        db.refresh(quiz)
        db.refresh(report)

        run.student_profile_id = profile.id
        output = {
            "student_profile": state.get("student_profile", {}),
            "learning_path": state.get("learning_path", {}),
            "generated_resources": state.get("generated_resources", []),
            "quiz": state.get("quiz", {}),
            "quiz_id": quiz.id,
            "tutor_answer": state.get("tutor_answer", {}),
            "retrieved_context": state.get("retrieved_context", []),
            "evaluation_result": state.get("evaluation_result", {}),
            "report_path": state.get("report_path", ""),
            "report_id": report.id,
            "agent_run_id": run.id,
            "messages": state.get("messages", []),
        }
        run.output_json = dumps(output)
        run.status = "success"
        db.commit()
        return output
    except Exception as exc:
        run.status = "failed"
        run.output_json = dumps({"error": str(exc)})
        db.commit()
        raise HTTPException(status_code=500, detail=f"Agent 工作流运行失败：{exc}") from exc


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(AgentRun).order_by(AgentRun.id.desc()).limit(50).all()
    return [
        {
            "id": item.id,
            "course_id": item.course_id,
            "student_profile_id": item.student_profile_id,
            "workflow_name": item.workflow_name,
            "status": item.status,
            "input_json": loads(item.input_json, {}),
            "output_json": loads(item.output_json, {}),
            "created_at": item.created_at,
        }
        for item in runs
    ]
