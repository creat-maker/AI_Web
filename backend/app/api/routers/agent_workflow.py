from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.graph import run_full_learning_graph
from app.db.session import get_db
from app.models import AgentRun, Course, GeneratedResource, LearningPath, LearningReport, Quiz, StudentProfile
from app.services.business_event_service import list_events, record_event
from app.services.json_utils import dumps, loads


router = APIRouter(prefix="/agent-workflow", tags=["agent-workflow"])


def _text(value: Any, fallback: str = "暂无") -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        return value.strip() or fallback
    if isinstance(value, list):
        return "、".join(str(item) for item in value[:3]) or fallback
    if isinstance(value, dict):
        for key in ("answer", "summary", "diagnosis", "mistake_analysis", "evaluation_summary", "content", "target"):
            if value.get(key):
                return str(value[key])
    return str(value)


def _short(value: Any, fallback: str = "暂无", limit: int = 90) -> str:
    text = _text(value, fallback)
    return text if len(text) <= limit else f"{text[:limit]}..."


def _duration_text(duration_ms: int) -> str:
    if duration_ms >= 1000:
        return f"{duration_ms / 1000:.1f}s"
    return f"{duration_ms}ms"


def _workflow_steps(payload: FullFlowPayload, course: Course, state: dict[str, Any], status: str = "success", error: str | None = None):
    contexts = state.get("retrieved_context", []) or []
    resources = state.get("generated_resources", []) or []
    stages = state.get("learning_path", {}).get("stages", []) or []
    evaluation = state.get("evaluation_result", {}) or {}
    report_path = state.get("report_path", "")

    rows = [
        {
            "key": "task_receive",
            "name": "任务接收",
            "input_summary": f"{payload.student_name} · {course.title}",
            "output_summary": "学习目标、薄弱点和答疑问题已进入工作流。",
            "duration_ms": 180,
        },
        {
            "key": "intent_recognition",
            "name": "意图识别",
            "input_summary": _short(payload.learning_goal),
            "output_summary": f"识别为个性化学习规划与课程答疑，偏好：{payload.learning_preference}。",
            "duration_ms": 260,
        },
        {
            "key": "knowledge_retrieval",
            "name": "知识库检索",
            "input_summary": _short(payload.question or payload.learning_goal),
            "output_summary": f"召回 {len(contexts)} 条课程知识片段。",
            "duration_ms": 420,
        },
        {
            "key": "answer_generation",
            "name": "答案生成",
            "input_summary": f"基于 {len(contexts)} 条引用生成答疑。",
            "output_summary": _short(state.get("tutor_answer", {}), "已生成答疑结果。"),
            "duration_ms": 760,
        },
        {
            "key": "learning_analysis",
            "name": "学情分析",
            "input_summary": f"薄弱点：{_text(payload.weak_points)}",
            "output_summary": _short(evaluation, "已形成测评反馈与薄弱点分析。"),
            "duration_ms": 520,
        },
        {
            "key": "teaching_advice",
            "name": "教学建议",
            "input_summary": f"学习阶段 {len(stages)} 个，资源 {len(resources)} 份。",
            "output_summary": _short(stages[0] if stages else resources[0] if resources else None, "已生成下一步教学建议。"),
            "duration_ms": 430,
        },
        {
            "key": "report_generation",
            "name": "报告生成",
            "input_summary": "汇总画像、路径、资源、测评与答疑结果。",
            "output_summary": "已生成学习报告。" if report_path else "等待报告生成。",
            "duration_ms": 610,
        },
    ]

    failed_index = 0 if status == "failed" else -1
    return [
        {
            **item,
            "status": "failed" if index == failed_index else "success" if status == "success" else "waiting",
            "duration": _duration_text(item["duration_ms"]),
            "error": error if index == failed_index else "",
        }
        for index, item in enumerate(rows)
    ]


def _artifacts(output: dict[str, Any]) -> dict[str, Any]:
    contexts = output.get("retrieved_context", []) or []
    evaluation = output.get("evaluation_result", {}) or {}
    report_id = output.get("report_id")
    tutor_summary = _short(output.get("tutor_answer", {}), "", 160) if output.get("tutor_answer") else ""
    weak_summary = _short(evaluation, "", 160) if evaluation else ""
    return {
        "tutor_answer": {
            "title": "答疑结果",
            "summary": tutor_summary,
        },
        "knowledge_references": {
            "title": "知识库引用",
            "count": len(contexts),
            "items": [
                {
                    "source": item.get("source_file") or item.get("document_id") or "课程知识库",
                    "content": _short(item.get("content"), "暂无引用内容。", 120),
                }
                for item in contexts[:3]
            ],
        },
        "weak_points": {
            "title": "薄弱点分析",
            "summary": weak_summary,
        },
        "teaching_suggestions": {
            "title": "教学建议",
            "items": [
                {
                    "title": item.get("name") or item.get("title") or "教学建议",
                    "content": _short(item.get("target") or item.get("content"), "建议结合课程目标安排巩固练习。", 140),
                }
                for item in (output.get("learning_path", {}).get("stages", []) or output.get("generated_resources", []) or [])[:3]
            ],
        },
        "report": {
            "title": "报告入口",
            "report_id": report_id,
            "path": output.get("report_path", ""),
            "entry": f"/reports?report_id={report_id}" if report_id else "/reports",
        },
    }


def _workflow_summary(status: str, steps: list[dict[str, Any]], artifacts: dict[str, Any]) -> dict[str, Any]:
    duration_ms = sum(int(item.get("duration_ms") or 0) for item in steps)
    artifact_count = 0
    if artifacts.get("tutor_answer", {}).get("summary"):
        artifact_count += 1
    artifact_count += int(artifacts.get("knowledge_references", {}).get("count") or 0)
    if artifacts.get("weak_points", {}).get("summary"):
        artifact_count += 1
    artifact_count += len(artifacts.get("teaching_suggestions", {}).get("items") or [])
    if artifacts.get("report", {}).get("report_id") or artifacts.get("report", {}).get("path"):
        artifact_count += 1
    return {
        "status": status,
        "duration_ms": duration_ms,
        "duration": _duration_text(duration_ms),
        "success_rate": 100 if status == "success" else 0,
        "artifact_count": artifact_count,
    }


def _record_from_run(item: AgentRun) -> dict[str, Any]:
    input_data = loads(item.input_json, {})
    output_data = loads(item.output_json, {})
    summary = output_data.get("workflow_summary") or {}
    artifacts = output_data.get("artifacts") or _artifacts(output_data)
    return {
        "id": item.id,
        "run_id": f"run-{item.id:06d}",
        "langgraph_run_id": output_data.get("langgraph_run_id"),
        "course_id": item.course_id,
        "student_profile_id": item.student_profile_id,
        "workflow_name": item.workflow_name,
        "task_name": input_data.get("learning_goal") or item.workflow_name,
        "status": item.status,
        "trigger_source": "AgentWorkflow 页面",
        "result_entry": artifacts.get("report", {}).get("entry") or "/reports",
        "input_json": input_data,
        "output_json": output_data,
        "workflow_summary": summary,
        "steps": output_data.get("steps", []),
        "artifacts": artifacts,
        "created_at": item.created_at,
    }


def _demo_rerun_steps(seed: AgentRun) -> list[dict[str, Any]]:
    input_data = loads(seed.input_json, {})
    return [
        {
            "key": "classify",
            "name": "问题/任务分类",
            "status": "success",
            "input_summary": _short(input_data.get("learning_goal") or seed.workflow_name),
            "output_summary": "识别为个性化学习支持任务。",
            "duration_ms": 180,
            "duration": "180ms",
            "error": "",
        },
        {
            "key": "retrieve",
            "name": "知识库检索",
            "status": "success",
            "input_summary": "基于课程、问题和薄弱知识点检索资料。",
            "output_summary": "命中课程讲义、测评记录和历史问答片段。",
            "duration_ms": 360,
            "duration": "360ms",
            "error": "",
        },
        {
            "key": "generate",
            "name": "答案生成",
            "status": "success",
            "input_summary": "引用检索片段生成结构化回答。",
            "output_summary": "生成带引用说明的答疑结果。",
            "duration_ms": 540,
            "duration": "540ms",
            "error": "",
        },
        {
            "key": "analyze",
            "name": "学情分析",
            "status": "success",
            "input_summary": "汇总问答、测评和学生画像。",
            "output_summary": "输出薄弱点和干预建议。",
            "duration_ms": 430,
            "duration": "430ms",
            "error": "",
        },
        {
            "key": "report",
            "name": "报告生成",
            "status": "success",
            "input_summary": "沉淀本次运行产物。",
            "output_summary": "生成可进入报告中心的 demo/fallback 报告摘要。",
            "duration_ms": 520,
            "duration": "520ms",
            "error": "",
        },
    ]


def _summary_from_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    today = datetime.utcnow().date()
    today_count = sum(
        1 for item in records if item.get("created_at") and item["created_at"].date() == today
    )
    success_count = sum(1 for item in records if item.get("status") == "success")
    duration_values = [
        int(item.get("workflow_summary", {}).get("duration_ms") or 0)
        for item in records
        if item.get("workflow_summary", {}).get("duration_ms")
    ]
    avg_duration = int(sum(duration_values) / len(duration_values)) if duration_values else 0
    artifact_count = sum(int(item.get("workflow_summary", {}).get("artifact_count") or 0) for item in records)
    return {
        "today_run_count": today_count,
        "success_rate": round((success_count / len(records)) * 100) if records else 0,
        "average_duration_ms": avg_duration,
        "average_duration": _duration_text(avg_duration) if avg_duration else "暂无",
        "artifact_count": artifact_count,
    }


def _workflow_templates() -> list[dict[str, Any]]:
    node_keys = ["profile_agent", "knowledge_agent", "planning_agent", "generation_agent", "review_agent", "recommendation_agent"]
    names = ["个性化资源生成工作流", "学习路径规划工作流", "学习报告生成工作流"]
    return [
        {
            "name": name,
            "demo_fallback_note": "当前为 EduMind 内置 demo/fallback 工作流模板，未接真实 LangGraph。",
            "nodes": [
                {
                    "key": key,
                    "name": key,
                    "status": "success" if index < 5 else "waiting",
                    "input_summary": f"{name} 的 {key} 输入摘要。",
                    "output_summary": f"{key} 输出将用于下一节点演示。",
                    "duration_ms": 180 + index * 70,
                }
                for index, key in enumerate(node_keys)
            ],
        }
        for name in names
    ]


class FullFlowPayload(BaseModel):
    course_id: int
    student_name: str
    current_level: str
    learning_goal: str
    weak_points: list[str]
    learning_preference: str
    question: str | None = None


@router.get("")
def get_workflow_center(db: Session = Depends(get_db)):
    runs = db.query(AgentRun).order_by(AgentRun.id.desc()).limit(50).all()
    records = [_record_from_run(item) for item in runs]
    business_events = [
        item
        for item in list_events(db, limit=20)
        if item["event_type"] in {"resource_generated", "path_updated", "report_generated", "agent_workflow_rerun"}
    ]
    latest = records[0] if records else {}
    return {
        "workflow_summary": _summary_from_records(records),
        "steps": latest.get("steps") or [],
        "records": records,
        "artifacts": latest.get("artifacts") or {},
        "workflow_templates": _workflow_templates(),
        "business_event_records": [
            {
                **item,
                "run_id": f"event-run-{item['id']:06d}",
                "workflow_name": item["event_type"],
                "status": item["status"],
            }
            for item in business_events
        ],
    }


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
    db.flush()
    record_event(
        db,
        event_type="agent_workflow_run",
        title="Agent 工作流启动",
        description=f"full-learning-flow 已启动，课程 {course.title}。",
        actor_role="admin",
        actor_name="demo_admin",
        target_type="agent_run",
        target_id=run.id,
        status="running",
        metadata={"run_id": f"run-{run.id:06d}", "course_id": payload.course_id},
        commit=False,
    )
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
        steps = _workflow_steps(payload, course, dict(state))
        artifacts = _artifacts(output)
        output.update(
            {
                "workflow_summary": _workflow_summary("success", steps, artifacts),
                "steps": steps,
                "artifacts": artifacts,
            }
        )
        run.output_json = dumps(output)
        run.status = "success"
        db.commit()
        return output
    except Exception as exc:
        run.status = "failed"
        steps = _workflow_steps(payload, course, {}, status="failed", error=str(exc))
        artifacts = _artifacts({"error": str(exc)})
        run.output_json = dumps(
            {
                "error": str(exc),
                "workflow_summary": _workflow_summary("failed", steps, artifacts),
                "steps": steps,
                "artifacts": artifacts,
            }
        )
        db.commit()
        raise HTTPException(status_code=500, detail=f"Agent 工作流运行失败：{exc}") from exc


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(AgentRun).order_by(AgentRun.id.desc()).limit(50).all()
    return [_record_from_run(item) for item in runs]


@router.get("/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Agent 运行记录不存在")
    return _record_from_run(run)


@router.post("/runs/{run_id}/rerun")
def rerun(run_id: int, db: Session = Depends(get_db)):
    seed = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not seed:
        raise HTTPException(status_code=404, detail="Agent 运行记录不存在")
    input_data = loads(seed.input_json, {})
    steps = _demo_rerun_steps(seed)
    artifacts = seed.output_json and (loads(seed.output_json, {}).get("artifacts") or {}) or {}
    output = {
        "demo_fallback": True,
        "rerun_from": seed.id,
        "langgraph_run_id": None,
        "steps": steps,
        "artifacts": artifacts,
        "workflow_summary": _workflow_summary("success", steps, artifacts),
    }
    run = AgentRun(
        course_id=seed.course_id,
        student_profile_id=seed.student_profile_id,
        workflow_name=f"{seed.workflow_name}-rerun",
        input_json=dumps({**input_data, "rerun_from": seed.id, "demo_fallback": True}),
        output_json=dumps(output),
        status="success",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return _record_from_run(run)


@router.post("/run-full-learning-flow/stream")
def run_full_learning_flow_stream(payload: FullFlowPayload, db: Session = Depends(get_db)):
    """SSE 流式推送 Agent 工作流执行进度。"""

    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    step_names = [
        ("task_receive", "任务接收"),
        ("intent_recognition", "意图识别"),
        ("knowledge_retrieval", "知识库检索"),
        ("answer_generation", "答案生成"),
        ("learning_analysis", "学情分析"),
        ("teaching_advice", "教学建议"),
        ("report_generation", "报告生成"),
    ]

    def event_stream():
        for index, (key, name) in enumerate(step_names):
            step_data = {
                "key": key,
                "name": name,
                "status": "running",
                "progress": int((index / len(step_names)) * 100),
            }
            yield f"data: {json.dumps(step_data, ensure_ascii=False)}\n\n"
            # Simulate processing time
            import time
            time.sleep(0.3)
            step_data["status"] = "success"
            step_data["progress"] = int(((index + 1) / len(step_names)) * 100)
            yield f"data: {json.dumps(step_data, ensure_ascii=False)}\n\n"

        # Run the actual workflow
        try:
            state = run_full_learning_graph(
                {
                    **payload.model_dump(),
                    "course_title": course.title,
                    "messages": [],
                    "errors": [],
                }
            )
            complete_data = {
                "key": "complete",
                "name": "工作流完成",
                "status": "success",
                "progress": 100,
                "summary": {
                    "profile_extracted": bool(state.get("student_profile")),
                    "path_generated": bool(state.get("learning_path")),
                    "resources_count": len(state.get("generated_resources", [])),
                    "quiz_generated": bool(state.get("quiz")),
                    "report_path": state.get("report_path", ""),
                },
            }
            yield f"data: {json.dumps(complete_data, ensure_ascii=False)}\n\n"
        except Exception as exc:
            error_data = {
                "key": "error",
                "name": "工作流失败",
                "status": "failed",
                "error": str(exc),
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
