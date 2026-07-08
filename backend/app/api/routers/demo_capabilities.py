from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AgentRun, AuditLog, Course, Quiz, StudentProfile
from app.services.governance_service import apply_teacher_arbitration_decision
from app.services.json_utils import dumps, loads
from app.services.quiz_service import create_quiz, submit_quiz


router = APIRouter(tags=["demo-capabilities"])


class QuizSubmitPayload(BaseModel):
    quiz_id: int | None = None
    student_profile_id: int = 1
    course_id: int | None = None
    answers: dict[str, Any] = {}


class ArbitrationDecisionPayload(BaseModel):
    decision: str
    comment: str | None = None
    revised_content: str | None = None
    teacher_comment: str | None = None
    suggested_action: str | None = None


def _agent_run_to_dict(item: AgentRun) -> dict[str, Any]:
    output = loads(item.output_json, {}) if item.output_json else {}
    return {
        "id": item.id,
        "run_id": item.run_id or f"run-{item.id:06d}",
        "student_id": item.student_profile_id,
        "course_id": item.course_id,
        "topic": loads(item.input_json, {}).get("learning_goal") or loads(item.input_json, {}).get("topic") or item.workflow_name,
        "current_node": item.current_node or output.get("current_node") or ("ReporterAgent" if item.status == "success" else "运行中"),
        "status": item.status,
        "messages": loads(item.messages, output.get("messages", [])),
        "state": loads(item.state, output),
        "audit_result": loads(item.audit_result, output.get("audit_result", {})),
        "retry_count": item.retry_count or int(output.get("retry_count") or 0),
        "teacher_arbitration_result": loads(item.teacher_arbitration_result, output.get("teacher_arbitration_result", {})),
        "started_at": item.started_at or item.created_at,
        "finished_at": item.finished_at,
        "steps": output.get("steps", []),
        "artifacts": output.get("artifacts", {}),
    }


@router.post("/quiz/submit")
def submit_quiz_compat(payload: QuizSubmitPayload, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.id == payload.student_profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="学生画像不存在")
    quiz = db.query(Quiz).filter(Quiz.id == payload.quiz_id).first() if payload.quiz_id else None
    if not quiz:
        course_id = payload.course_id or profile.course_id
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        quiz = create_quiz(db, course, profile)
    submission = submit_quiz(db, quiz, profile, payload.answers)
    feedback = loads(submission.feedback_json, {})
    return {
        "id": submission.id,
        "quiz_id": quiz.id,
        "student_profile_id": profile.id,
        "score": submission.score,
        "feedback": feedback,
        "error_analysis": feedback.get("mistake_analysis") or feedback.get("error_analysis") or "已完成错因分析。",
        "weak_points": feedback.get("detected_new_weak_points") or feedback.get("weak_points") or [],
        "dkvmn": feedback.get("dkvmn", {}),
        "profile_updated": bool(feedback.get("dkvmn")),
        "path_adjustment": feedback.get("path_adjustment", {}),
        "teacher_arbitration_required": bool((feedback.get("path_adjustment") or {}).get("teacher_arbitration_required")),
    }


@router.get("/agent-runs")
def list_agent_runs(db: Session = Depends(get_db)):
    rows = db.query(AgentRun).order_by(AgentRun.id.desc()).limit(80).all()
    if not rows:
        return [
            {
                "run_id": "fallback-run-001",
                "student_id": 1,
                "course_id": 1,
                "topic": "Python 循环结构",
                "current_node": "TeacherArbitration",
                "status": "pending_review",
                "messages": ["本地 fallback：暂无真实 AgentRun，展示治理链路结构。"],
                "audit_result": {"risk_level": "medium", "review_status": "needs_review"},
                "retry_count": 1,
                "teacher_arbitration_result": {"status": "pending"},
                "started_at": datetime.utcnow().isoformat(),
                "finished_at": None,
            }
        ]
    return [_agent_run_to_dict(item) for item in rows]


@router.get("/agent-runs/{run_id}")
def get_agent_run(run_id: str, db: Session = Depends(get_db)):
    item = None
    if run_id.isdigit():
        item = db.query(AgentRun).filter(AgentRun.id == int(run_id)).first()
    if not item:
        item = db.query(AgentRun).filter(AgentRun.run_id == run_id).first()
    if not item and run_id.startswith("run-"):
        try:
            item = db.query(AgentRun).filter(AgentRun.id == int(run_id.split("-")[-1])).first()
        except ValueError:
            item = None
    if not item:
        raise HTTPException(status_code=404, detail="Agent 运行记录不存在")
    return _agent_run_to_dict(item)


@router.get("/audit-logs")
def list_audit_logs(db: Session = Depends(get_db)):
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    if not rows:
        return [
            {
                "id": "fallback-audit-001",
                "action": "content_rule_check",
                "target_type": "rag_answer",
                "status": "needs_review",
                "retry_count": 1,
                "risk_level": "medium",
                "arbitration_status": "pending",
                "rule_engine_result": {"dimensions": ["事实准确性", "课程对齐度", "超纲风险", "隐私风险", "不当内容", "幻觉风险", "学段适配"]},
                "xfyun_result": {"status": "not_configured", "message": "讯飞安全 API 未配置，使用本地规则 fallback。"},
                "created_at": datetime.utcnow().isoformat(),
            }
        ]
    return [
        {
            "id": item.id,
            "actor_id": item.actor_id,
            "actor_name": item.actor_name,
            "actor_role": item.actor_role,
            "action": item.action,
            "target_type": item.target_type,
            "target_id": item.target_id,
            "status": item.status,
            "detail": item.detail,
            "retry_count": item.retry_count,
            "xfyun_result": loads(item.xfyun_result, {}),
            "rule_engine_result": loads(item.rule_engine_result, {}),
            "risk_level": item.risk_level or "low",
            "arbitration_status": item.arbitration_status or "none",
            "created_at": item.created_at,
        }
        for item in rows
    ]


def _fallback_arbitration_tasks() -> list[dict[str, Any]]:
    return [
        {
            "id": "demo-arb-low",
            "student_name": "李明",
            "course": "Python 程序设计",
            "topic": "while 循环条件更新",
            "risk_level": "low",
            "trigger_reason": "引用证据充分，但建议教师确认示例输出。",
            "original_content": "while 循环补弱讲义与变量更新练习。",
            "suggested_content": "发布到学生端，并保留引用来源。",
            "review_result": "pending",
            "retry_count": 0,
            "rag_citations": ["python_programming.json-001"],
            "profile_risk_evidence": ["while_loop 掌握度 0.48"],
            "recommended_action": "approve",
            "status": "pending",
        },
        {
            "id": "demo-arb-medium",
            "student_name": "李明",
            "course": "Python 程序设计",
            "topic": "break / continue 对比",
            "risk_level": "medium",
            "trigger_reason": "审核发现示例解释略少，需要教师补充说明。",
            "original_content": "break 和 continue 的输出判断题。",
            "suggested_content": "补充 continue 跳过本轮但不跳出循环的解释。",
            "review_result": "needs_review",
            "retry_count": 1,
            "rag_citations": ["python_programming.json-002", "python_programming.json-003"],
            "profile_risk_evidence": ["break_continue 错误 streak=2"],
            "recommended_action": "revise",
            "status": "pending",
        },
        {
            "id": "demo-arb-high",
            "student_name": "李明",
            "course": "Python 程序设计",
            "topic": "循环结构扩展资源",
            "risk_level": "high",
            "trigger_reason": "内容出现课程范围外示例，需拦截或重写。",
            "original_content": "将循环结构扩展到股票预测与机器学习训练。",
            "suggested_content": "拒绝该版本，重新回到 Python 循环基础。",
            "review_result": "blocked",
            "retry_count": 3,
            "rag_citations": [],
            "profile_risk_evidence": ["课程对齐度低", "超纲风险高"],
            "recommended_action": "reject",
            "status": "pending",
        },
    ]


@router.get("/teacher-arbitrations")
def list_teacher_arbitrations(db: Session = Depends(get_db)):
    rows = db.query(AgentRun).order_by(AgentRun.id.desc()).limit(30).all()
    tasks: list[dict[str, Any]] = []
    for item in rows:
        arbitration = loads(item.teacher_arbitration_result, {})
        if not arbitration:
            continue
        output = loads(item.output_json, {})
        audit = loads(item.audit_result, output.get("audit_result", {}))
        input_data = loads(item.input_json, {})
        tasks.append(
            {
                "id": item.run_id or str(item.id),
                "agent_run_id": item.id,
                "student_name": input_data.get("student_name", "李明"),
                "course": input_data.get("course_title", "Python 程序设计"),
                "topic": input_data.get("learning_goal", "循环结构补弱"),
                "risk_level": audit.get("risk_level", "medium"),
                "trigger_reason": arbitration.get("reason", "高风险或多次审核未通过，等待教师仲裁。"),
                "original_content": str(output.get("generated_resources", [])[:1] or "暂无资源摘要"),
                "suggested_content": "教师可通过、修改或拒绝后写回治理日志。",
                "review_result": audit.get("review_status", "needs_review"),
                "retry_count": item.retry_count or int(output.get("retry_count") or 0),
                "rag_citations": [ref.get("citation_id") for ref in output.get("knowledge_evidence", {}).get("items", []) if isinstance(ref, dict)],
                "profile_risk_evidence": [check.get("dimension") for check in audit.get("checks", []) if check.get("status") != "pass"],
                "recommended_action": "reject" if audit.get("risk_level") == "high" else "revise" if audit.get("risk_level") == "medium" else "approve",
                "teacher_comment": arbitration.get("teacher_comment", ""),
                "status": arbitration.get("status", "pending"),
            }
        )
    return tasks or _fallback_arbitration_tasks()


@router.post("/teacher-arbitration/{item_id}/decision")
def teacher_arbitration_decision(item_id: str, payload: ArbitrationDecisionPayload, db: Session = Depends(get_db)):
    if payload.decision not in {"approve", "revise", "reject"}:
        raise HTTPException(status_code=400, detail="decision 必须是 approve / revise / reject")
    item = None
    if item_id.isdigit():
        item = db.query(AgentRun).filter(AgentRun.id == int(item_id)).first()
    if not item:
        item = db.query(AgentRun).filter(AgentRun.run_id == item_id).first()
    if not item and item_id.startswith("run-"):
        try:
            item = db.query(AgentRun).filter(AgentRun.id == int(item_id.split("-")[-1])).first()
        except ValueError:
            item = None
    teacher_comment = payload.teacher_comment or payload.comment or "教师完成仲裁决策。"
    applied = apply_teacher_arbitration_decision(
        db,
        item=item,
        item_id=item_id,
        decision=payload.decision,
        teacher_comment=teacher_comment,
        revised_content=payload.revised_content,
        suggested_action=payload.suggested_action,
    )
    log = applied["audit_log"]
    result = applied["state"]["teacher_arbitration_result"]
    return {
        "id": log.id,
        "item_id": item_id,
        "decision": payload.decision,
        "comment": teacher_comment,
        "revised_content": payload.revised_content,
        "suggested_action": payload.suggested_action,
        "status": result["status"],
        "teacher_arbitration_result": result,
        "next_node": applied["next_node"],
        "message": "教师仲裁结果已写入治理日志。",
    }
