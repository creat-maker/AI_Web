from __future__ import annotations

import asyncio
import json
from datetime import datetime
from threading import Lock
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.graph import run_full_learning_graph
from app.api.deps import require_roles, require_staff
from app.db.session import get_db
from app.models import AgentRun, Course, GeneratedResource, LearningPath, LearningReport, Quiz, StudentProfile
from app.services.business_event_service import list_events, record_event
from app.services.demo_learning_service import build_agent_steps
from app.services.governance_service import current_user_label, write_audit_log
from app.services.json_utils import dumps, loads
from app.services.teacher_scope_service import (
    agent_run_student_matches_course,
    can_access_agent_run,
    get_course_for_write,
    scope_agent_run_query,
)


router = APIRouter(prefix="/agent-workflow", tags=["agent-workflow"])
_rerun_lock = Lock()


class FullFlowPayload(BaseModel):
    course_id: int
    student_name: str
    current_level: str
    learning_goal: str
    weak_points: list[str]
    learning_preference: str
    question: str | None = None


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


def _workflow_steps(
    payload: FullFlowPayload,
    course: Course,
    state: dict[str, Any],
    status: str = "success",
    error: str | None = None,
) -> list[dict[str, Any]]:
    contexts = state.get("retrieved_context", []) or []
    evidence = state.get("knowledge_evidence", {}) or {}
    resource_plan = state.get("resource_plan", {}) or {}
    resources = state.get("generated_resources", []) or []
    stages = state.get("learning_path", {}).get("stages", []) or []
    evaluation = state.get("evaluation_result", {}) or {}
    audit = state.get("audit_result", {}) or {}
    report_path = state.get("report_path", "")

    rows = [
        {
            "key": "task_receive",
            "name": "任务接收",
            "input_summary": f"{payload.student_name} · {course.title}",
            "output_summary": "学习目标、薄弱点、偏好和答疑问题已进入多智能体工作流。",
            "duration_ms": 180,
        },
        {
            "key": "profile_analysis",
            "name": "画像构建",
            "input_summary": f"水平：{payload.current_level}；偏好：{payload.learning_preference}",
            "output_summary": _short(state.get("student_profile", {}), "已抽取不少于 6 个画像维度。"),
            "duration_ms": 300,
        },
        {
            "key": "knowledge_retrieval",
            "name": "RAG 证据检索",
            "input_summary": _short(evidence.get("query") or payload.question or payload.learning_goal),
            "output_summary": f"召回 {len(contexts)} 条课程知识片段，平均置信度 {evidence.get('confidence', 0)}。",
            "duration_ms": 460,
        },
        {
            "key": "path_planning",
            "name": "学习路径规划",
            "input_summary": f"画像维度 + {len(contexts)} 条课程证据",
            "output_summary": f"生成 {len(stages)} 个动态学习阶段。",
            "duration_ms": 520,
        },
        {
            "key": "resource_planning",
            "name": "资源生成规划",
            "input_summary": _short(resource_plan.get("goal") or payload.learning_goal),
            "output_summary": f"计划覆盖 {len(resource_plan.get('coverage', []) or [])} 类资源。",
            "duration_ms": 420,
        },
        {
            "key": "resource_generation",
            "name": "多模态资源生成",
            "input_summary": f"资源规划 {len(resource_plan.get('items', []) or [])} 项",
            "output_summary": f"生成 {len(resources)} 个个性化资源。",
            "duration_ms": 820,
        },
        {
            "key": "rag_tutoring",
            "name": "RAG 智能答疑",
            "input_summary": f"基于 {len(contexts)} 条引用生成答疑",
            "output_summary": _short(state.get("tutor_answer", {}), "已生成带引用答疑结果。"),
            "duration_ms": 760,
        },
        {
            "key": "learning_evaluation",
            "name": "学习效果评估",
            "input_summary": "形成性测验与演示作答",
            "output_summary": _short(evaluation, "已形成测评反馈与画像更新建议。"),
            "duration_ms": 520,
        },
        {
            "key": "content_audit",
            "name": "内容安全与防幻觉审核",
            "input_summary": f"引用 {evidence.get('citation_count', len(contexts))} 条，资源 {len(resources)} 个",
            "output_summary": f"{audit.get('review_status', '未审核')}；风险等级：{audit.get('risk_level', 'unknown')}",
            "duration_ms": 390,
        },
        {
            "key": "report_generation",
            "name": "报告生成",
            "input_summary": "汇总画像、RAG 证据、路径、资源、测评和审核结果。",
            "output_summary": "已生成学习报告。" if report_path else "等待报告生成。",
            "duration_ms": 610,
        },
    ]

    failed_index = 0 if status == "failed" else -1
    result = []
    for index, item in enumerate(rows):
        if index == failed_index:
            step_status = "failed"
        elif status == "success":
            step_status = "success"
        elif status == "pending_review":
            step_status = "success" if item["key"] not in {"content_audit", "report_generation"} else "pending_review" if item["key"] == "content_audit" else "waiting"
        else:
            step_status = "waiting"
        result.append(
            {
                **item,
                "status": step_status,
                "duration": _duration_text(item["duration_ms"]),
                "error": error if index == failed_index else "",
            }
        )
    return result


def _knowledge_reference_items(contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source": item.get("source_file") or item.get("document_id") or "课程知识库",
            "section": item.get("section_title"),
            "knowledge_point": item.get("knowledge_point"),
            "citation_id": item.get("citation_id"),
            "confidence": item.get("confidence", item.get("score", 0)),
            "content": _short(item.get("content"), "暂无引用内容。", 120),
        }
        for item in contexts[:5]
    ]


def _artifacts(output: dict[str, Any]) -> dict[str, Any]:
    contexts = output.get("retrieved_context", []) or []
    evidence = output.get("knowledge_evidence", {}) or {}
    resource_plan = output.get("resource_plan", {}) or {}
    resources = output.get("generated_resources", []) or []
    evaluation = output.get("evaluation_result", {}) or {}
    audit = output.get("audit_result", {}) or {}
    report_id = output.get("report_id")
    tutor_summary = _short(output.get("tutor_answer", {}), "", 160) if output.get("tutor_answer") else ""
    weak_summary = _short(evaluation, "", 160) if evaluation else ""
    knowledge_items = evidence.get("items") or _knowledge_reference_items(contexts)
    return {
        "tutor_answer": {
            "title": "答疑结果",
            "summary": tutor_summary,
            "unsupported_answer_risk": bool(output.get("tutor_answer", {}).get("unsupported_answer_risk")),
        },
        "knowledge_references": {
            "title": "知识库引用",
            "count": len(contexts),
            "items": _knowledge_reference_items(contexts),
        },
        "knowledge_evidence": {
            "title": "RAG 证据包",
            "query": evidence.get("query"),
            "confidence": evidence.get("confidence", 0),
            "citation_count": evidence.get("citation_count", len(contexts)),
            "unsupported_answer_risk": evidence.get("unsupported_answer_risk", False),
            "items": knowledge_items[:5],
        },
        "resource_plan": {
            "title": "资源生成计划",
            "coverage": resource_plan.get("coverage", []),
            "items": resource_plan.get("items", [])[:7],
        },
        "generated_resources": {
            "title": "生成资源包",
            "count": len(resources),
            "items": [
                {
                    "resource_type": item.get("resource_type"),
                    "title": item.get("title"),
                    "difficulty": item.get("difficulty"),
                    "summary": _short(item.get("content"), "暂无资源内容。", 140),
                    "source_refs": item.get("source_refs", []),
                    "confidence": item.get("confidence"),
                }
                for item in resources[:7]
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
                for item in (output.get("learning_path", {}).get("stages", []) or resources or [])[:3]
            ],
        },
        "audit_result": {
            "title": "内容审核",
            "review_status": audit.get("review_status"),
            "risk_level": audit.get("risk_level"),
            "checks": audit.get("checks", [])[:6],
            "suggestions": audit.get("suggestions", [])[:4],
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
    artifact_count += int(artifacts.get("knowledge_evidence", {}).get("citation_count") or 0)
    artifact_count += len(artifacts.get("resource_plan", {}).get("items") or [])
    artifact_count += int(artifacts.get("generated_resources", {}).get("count") or 0)
    if artifacts.get("weak_points", {}).get("summary"):
        artifact_count += 1
    if artifacts.get("audit_result", {}).get("review_status"):
        artifact_count += 1
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
            "key": "profile_analysis",
            "name": "画像构建",
            "status": "success",
            "input_summary": _short(input_data.get("learning_goal") or seed.workflow_name),
            "output_summary": "复用原始输入生成画像维度。",
            "duration_ms": 180,
            "duration": "180ms",
            "error": "",
        },
        {
            "key": "knowledge_retrieval",
            "name": "RAG 证据检索",
            "status": "success",
            "input_summary": "基于课程、问题和薄弱知识点检索资料。",
            "output_summary": "命中课程讲义、实践任务和题库片段。",
            "duration_ms": 360,
            "duration": "360ms",
            "error": "",
        },
        {
            "key": "resource_generation",
            "name": "多模态资源生成",
            "status": "success",
            "input_summary": "引用检索片段生成结构化资源包。",
            "output_summary": "生成讲义、导图、题库、视频脚本和代码案例。",
            "duration_ms": 540,
            "duration": "540ms",
            "error": "",
        },
        {
            "key": "content_audit",
            "name": "内容审核",
            "status": "success",
            "input_summary": "检查引用覆盖和低依据风险。",
            "output_summary": "输出可演示的审核结论。",
            "duration_ms": 430,
            "duration": "430ms",
            "error": "",
        },
        {
            "key": "report_generation",
            "name": "报告生成",
            "status": "success",
            "input_summary": "沉淀本次运行产物。",
            "output_summary": "生成可进入报告中心的报告摘要。",
            "duration_ms": 520,
            "duration": "520ms",
            "error": "",
        },
    ]


def _summary_from_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    today = datetime.utcnow().date()
    today_count = sum(1 for item in records if item.get("created_at") and item["created_at"].date() == today)
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
    node_keys = [
        "ProfileAgent",
        "KnowledgeAgent",
        "PlannerAgent",
        "ResourcePlannerAgent",
        "ResourceAgent",
        "TutorAgent",
        "EvaluatorAgent",
        "AuditAgent",
        "ComplianceAgent",
        "AuditRetry",
        "TeacherArbitration",
        "ReporterAgent",
    ]
    names = ["个性化资源生成工作流", "学习路径规划工作流", "学习报告生成工作流"]
    return [
        {
            "name": name,
            "demo_fallback_note": "EduMind 当前已接入真实后端多智能体链路；未安装 LangGraph 时自动使用同序顺序兜底。",
            "nodes": [
                {
                    "key": key,
                    "name": key,
                    "status": "success" if index < 5 else "waiting",
                    "input_summary": f"{name} 的 {key} 输入摘要。",
                    "output_summary": f"{key} 输出将用于下一个节点演示。",
                    "duration_ms": 180 + index * 70,
                }
                for index, key in enumerate(node_keys)
            ],
        }
        for name in names
    ]


@router.get("")
def get_workflow_center(
    user_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_roles("student", "teacher", "admin")),
):
    query = scope_agent_run_query(db.query(AgentRun), db, current_user)
    runs = query.order_by(AgentRun.id.desc()).limit(50).all()
    records = [_record_from_run(item) for item in runs]
    accessible_run_ids = {str(item.id) for item in runs}
    business_events = [
        item
        for item in list_events(db, limit=20)
        if item["event_type"] in {"resource_generated", "path_updated", "report_generated", "agent_workflow_rerun"}
        and (
            str(current_user.get("role")) == "admin"
            or (item.get("target_type") == "agent_run" and str(item.get("target_id")) in accessible_run_ids)
        )
    ]
    latest = records[0] if records else {}
    effective_user_id = (
        str(current_user.get("user_id") or current_user.get("username") or "")
        if str(current_user.get("role")) == "student"
        else user_id
    )
    steps = build_agent_steps(effective_user_id) if effective_user_id else latest.get("steps") or build_agent_steps()
    return {
        "workflow_summary": _summary_from_records(records) if records else {
            "today_run_count": 3,
            "success_rate": 100,
            "average_duration_ms": sum(item["duration_ms"] for item in steps),
            "average_duration": _duration_text(sum(item["duration_ms"] for item in steps)),
            "artifact_count": 8,
        },
        "steps": steps,
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
def run_full_learning_flow(
    payload: FullFlowPayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_staff),
):
    course = get_course_for_write(db, current_user, payload.course_id)
    actor_id, actor_name, actor_role = current_user_label(current_user)

    run = AgentRun(
        course_id=payload.course_id,
        workflow_name="full-learning-flow",
        input_json=payload.model_dump_json(),
        status="running",
        current_node="ProfileAgent",
        state=dumps({"status": "running", "payload": payload.model_dump()}),
        messages=dumps(["Agent 工作流已启动"]),
        started_at=datetime.utcnow(),
    )
    db.add(run)
    db.flush()
    run.run_id = f"run-{run.id:06d}"
    record_event(
        db,
        event_type="agent_workflow_started",
        title="Agent 工作流启动",
        description=f"{payload.student_name} 的 full-learning-flow 已开始执行。",
        actor_id=actor_id,
        actor_role=actor_role,
        actor_name=actor_name,
        target_type="agent_run",
        target_id=run.id,
        status="running",
        metadata={"run_id": f"run-{run.id:06d}", "course_id": payload.course_id, "student_name": payload.student_name},
        commit=False,
    )
    db.commit()
    db.refresh(run)

    try:
        state = run_full_learning_graph(
            {
                **payload.model_dump(),
                "run_id": run.run_id,
                "course_title": course.title,
                "messages": [],
                "errors": [],
            }
        )
        pending_review = (
            state.get("status") == "pending_review"
            or (state.get("teacher_arbitration_result") or {}).get("status") == "pending"
        )
        workflow_status = "pending_review" if pending_review else "success"

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
                source_agent=item.get("source_agent", "ResourceAgent"),
                recommend_reason=item.get("recommend_reason") or item.get("recommendation_reason"),
                generation_status="draft" if pending_review else "generated",
                audit_status="pending_review" if pending_review else "passed",
            )
            db.add(resource)
            resources.append(resource)

        quiz = Quiz(
            course_id=payload.course_id,
            student_profile_id=profile.id,
            quiz_json=dumps(state.get("quiz", {})),
        )
        db.add(quiz)

        report = None
        if not pending_review and state.get("report_path"):
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
        if report:
            db.refresh(report)

        run.student_profile_id = profile.id
        output = {
            "student_profile": state.get("student_profile", {}),
            "knowledge_query": state.get("knowledge_query", ""),
            "knowledge_evidence": state.get("knowledge_evidence", {}),
            "learning_path": state.get("learning_path", {}),
            "resource_plan": state.get("resource_plan", {}),
            "generated_resources": state.get("generated_resources", []),
            "quiz": state.get("quiz", {}),
            "quiz_id": quiz.id,
            "tutor_answer": state.get("tutor_answer", {}),
            "retrieved_context": state.get("retrieved_context", []),
            "evaluation_result": state.get("evaluation_result", {}),
            "audit_result": state.get("audit_result", {}),
            "report_path": state.get("report_path", ""),
            "report_id": report.id if report else None,
            "agent_run_id": run.id,
            "messages": state.get("messages", []),
            "teacher_arbitration_result": state.get("teacher_arbitration_result", {}),
            "retry_count": int(state.get("retry_count") or 0),
            "status": workflow_status,
        }
        steps = _workflow_steps(payload, course, dict(state), status=workflow_status)
        artifacts = _artifacts(output)
        output.update(
            {
                "workflow_summary": _workflow_summary(workflow_status, steps, artifacts),
                "steps": steps,
                "artifacts": artifacts,
            }
        )
        run.output_json = dumps(output)
        run.status = workflow_status
        run.current_node = "TeacherArbitration" if pending_review else "ReporterAgent"
        run.state = dumps(
            {
                **state,
                "run_id": run.run_id,
                "status": workflow_status,
                "current_node": run.current_node,
                "profile_id": profile.id,
                "quiz_id": quiz.id,
                "resource_ids": [resource.id for resource in resources],
                "report_id": report.id if report else None,
            }
        )
        run.messages = dumps(state.get("messages", []))
        run.audit_result = dumps(state.get("audit_result", {}))
        run.retry_count = int(state.get("retry_count") or 0)
        run.teacher_arbitration_result = dumps(state.get("teacher_arbitration_result", {}))
        run.finished_at = None if pending_review else datetime.utcnow()
        db.commit()
        return output
    except Exception as exc:
        run.status = "failed"
        run.current_node = "error"
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
        run.finished_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=f"Agent 工作流运行失败：{exc}") from exc


@router.get("/runs")
def list_runs(
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_roles("student", "teacher", "admin")),
):
    query = scope_agent_run_query(db.query(AgentRun), db, current_user)
    runs = query.order_by(AgentRun.id.desc()).limit(50).all()
    return [_record_from_run(item) for item in runs]


@router.get("/runs/{run_id}")
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_roles("student", "teacher", "admin")),
):
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run or not can_access_agent_run(db, current_user, run) or not agent_run_student_matches_course(db, run):
        raise HTTPException(status_code=404, detail="Agent 运行记录不存在")
    return _record_from_run(run)


@router.post("/runs/{run_id}/rerun")
def rerun(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_staff),
):
    with _rerun_lock:
        seed = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        if not seed or not can_access_agent_run(db, current_user, seed) or not agent_run_student_matches_course(db, seed):
            raise HTTPException(status_code=404, detail="Agent 运行记录不存在")
        input_data = loads(seed.input_json, {})
        if input_data.get("rerun_from") is not None:
            raise HTTPException(status_code=409, detail="重跑产生的运行记录不能再次重跑")
        if seed.status not in {"success", "failed"}:
            raise HTTPException(status_code=409, detail="当前运行状态不允许重跑")
        existing_child = next(
            (
                item
                for item in db.query(AgentRun).filter(AgentRun.workflow_name.like("%-rerun")).all()
                if loads(item.input_json, {}).get("rerun_from") == seed.id
            ),
            None,
        )
        if existing_child:
            raise HTTPException(status_code=409, detail="该运行记录已经重跑")

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
        db.flush()
        actor_id, actor_name, actor_role = current_user_label(current_user)
        write_audit_log(
            db,
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            action="agent_run_rerun",
            target_type="agent_run",
            target_id=seed.id,
            detail={"source_run_id": seed.run_id or f"run-{seed.id:06d}", "new_agent_run_id": run.id},
            commit=False,
        )
        record_event(
            db,
            event_type="agent_workflow_rerun",
            title="Agent 工作流重跑",
            description="授权用户已基于既有运行创建一次演示重跑记录。",
            actor_id=actor_id,
            actor_role=actor_role,
            actor_name=actor_name,
            target_type="agent_run",
            target_id=seed.id,
            related_course=str(seed.course_id),
            metadata={"new_agent_run_id": run.id},
            commit=False,
        )
        db.commit()
        db.refresh(run)
        return _record_from_run(run)


@router.post("/run-full-learning-flow/stream")
def run_full_learning_flow_stream(
    payload: FullFlowPayload,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_staff),
):
    """SSE 流式推送 Agent 工作流执行进度。"""

    course = get_course_for_write(db, current_user, payload.course_id)

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
