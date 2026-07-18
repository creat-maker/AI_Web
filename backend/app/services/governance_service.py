from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models import (
    AITaskRun,
    AgentRun,
    AuditLog,
    ContentVersion,
    GeneratedResource,
    LearningReport,
    Quiz,
    ReviewItem,
)
from app.services.json_utils import dumps, loads
from app.services.privacy_service import mask_name, redact_payload, summarize_text

TASK_STATUSES = {
    "draft",
    "generating",
    "pending_review",
    "approved",
    "rejected",
    "published",
    "failed",
    "archived",
}

DEFAULT_ITEM_KEY = {
    "learning_path": "student-li-ming-python-loop",
    "resource_pack": "student-li-ming-python-loop",
    "learning_report": "student-li-ming-python-loop",
}


def current_user_label(user: dict[str, Any] | None) -> tuple[str, str, str]:
    user = user or {}
    return (
        str(user.get("user_id") or user.get("username") or "anonymous"),
        str(user.get("name") or user.get("display_name") or "访客"),
        str(user.get("role") or "guest"),
    )


def write_audit_log(
    db: Session,
    *,
    actor_id: str | None = None,
    actor_name: str | None = None,
    actor_role: str = "guest",
    action: str,
    target_type: str,
    target_id: str | int | None = None,
    status: str = "success",
    detail: Any = "",
    ip_address: str | None = None,
    commit: bool = True,
) -> AuditLog:
    row = AuditLog(
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        status=status,
        detail=redact_payload(detail),
        ip_address=ip_address,
    )
    db.add(row)
    if commit:
        db.commit()
        db.refresh(row)
    return row


def create_ai_task(
    db: Session,
    *,
    task_type: str,
    title: str,
    actor_id: str | None,
    actor_role: str,
    input_summary: Any,
    output_summary: Any = "",
    status: str = "pending_review",
    confidence: float = 0.88,
    error_message: str | None = None,
    trace: dict[str, Any] | None = None,
    commit: bool = True,
) -> AITaskRun:
    row = AITaskRun(
        task_type=task_type,
        title=title,
        actor_id=actor_id,
        actor_role=actor_role,
        input_summary=redact_payload(input_summary),
        output_summary=summarize_text(output_summary, 220),
        status=status if status in TASK_STATUSES else "draft",
        confidence=confidence,
        error_message=summarize_text(error_message, 220) if error_message else None,
        trace_json=dumps(trace or {}),
    )
    db.add(row)
    if commit:
        db.commit()
        db.refresh(row)
    return row


def create_review_item(
    db: Session,
    *,
    item_type: str,
    item_title: str,
    source_task_id: int | None,
    content: dict[str, Any],
    status: str = "pending_review",
    commit: bool = True,
) -> ReviewItem:
    row = ReviewItem(
        item_type=item_type,
        item_title=item_title,
        source_task_id=source_task_id,
        content_json=dumps(content),
        status=status,
    )
    db.add(row)
    if commit:
        db.commit()
        db.refresh(row)
    return row


def create_content_version(
    db: Session,
    *,
    item_type: str,
    item_key: str,
    content: dict[str, Any],
    status: str,
    is_active: bool,
    source_task_id: int | None = None,
    commit: bool = True,
) -> ContentVersion:
    latest = (
        db.query(ContentVersion)
        .filter(ContentVersion.item_type == item_type, ContentVersion.item_key == item_key)
        .order_by(ContentVersion.version_no.desc())
        .first()
    )
    if is_active:
        (
            db.query(ContentVersion)
            .filter(ContentVersion.item_type == item_type, ContentVersion.item_key == item_key)
            .update({ContentVersion.is_active: False})
        )
    row = ContentVersion(
        item_type=item_type,
        item_key=item_key,
        version_no=(latest.version_no + 1) if latest else 1,
        content_json=dumps(content),
        status=status,
        is_active=is_active,
        source_task_id=source_task_id,
    )
    db.add(row)
    if commit:
        db.commit()
        db.refresh(row)
    return row


def ensure_governance_seed(db: Session) -> None:
    if db.query(AITaskRun).count() > 0 and db.query(ContentVersion).count() > 0:
        return

    path_content = {
        "title": "Python 循环结构专项学习路径",
        "student": mask_name("李明"),
        "course": "Python 程序设计",
        "topic": "循环结构",
        "status_text": "已发布",
        "risk_notice": "中风险画像，已采用分层练习与变量变化表。",
        "items": [
            "while 循环条件更新专项练习",
            "循环嵌套变量变化表",
            "break / continue 输出判断题",
        ],
    }
    create_content_version(
        db,
        item_type="learning_path",
        item_key=DEFAULT_ITEM_KEY["learning_path"],
        content=path_content,
        status="published",
        is_active=True,
        commit=False,
    )

    resource_task = create_ai_task(
        db,
        task_type="resource_pack",
        title="Python 循环结构个性化补弱资源包",
        actor_id="system_demo_seed",
        actor_role="system",
        input_summary="课程=Python 程序设计；主题=循环结构；学生画像=基础薄弱 + 代码实操偏好型",
        output_summary="生成讲义、练习、动画、代码案例和项目任务，等待教师复核。",
        status="pending_review",
        confidence=0.86,
        trace={"steps": ["profile_summary", "knowledge_retrieval", "resource_generation", "risk_review"]},
        commit=False,
    )
    db.flush()
    create_review_item(
        db,
        item_type="resource_pack",
        item_title=resource_task.title,
        source_task_id=resource_task.id,
        content={
            "item_key": DEFAULT_ITEM_KEY["resource_pack"],
            "course": "Python 程序设计",
            "student": mask_name("李明"),
            "confidence": 0.86,
            "risk_tip": "引用完整，建议教师复核示例代码输出。",
            "generation_basis": ["循环结构章节", "while 循环错题", "代码实操偏好"],
            "resources": ["while 循环讲义", "循环嵌套练习", "break / continue 代码案例"],
        },
        commit=False,
    )

    failed_task = create_ai_task(
        db,
        task_type="learning_report",
        title="循环结构形成性评价报告重新生成",
        actor_id="system_demo_seed",
        actor_role="system",
        input_summary="学生报告摘要、最近测验结果、答疑摘要",
        output_summary="未覆盖上一版报告。",
        status="failed",
        confidence=0.0,
        error_message="课程知识库引用片段不足，已保留上一版已发布报告。",
        trace={"rollback": "active_version_kept", "active_item_key": DEFAULT_ITEM_KEY["learning_report"]},
        commit=False,
    )
    db.flush()
    create_content_version(
        db,
        item_type="learning_report",
        item_key=DEFAULT_ITEM_KEY["learning_report"],
        content={
            "title": "Python 循环结构形成性评价报告",
            "student": mask_name("李明"),
            "summary": "while 循环条件更新仍需巩固，当前继续使用上一版已发布报告。",
            "weak_points": ["while 循环条件更新", "循环嵌套变量变化", "break / continue 区分"],
            "rollback_notice": "生成失败，可重试，当前仍使用上一版内容。",
        },
        status="published",
        is_active=True,
        source_task_id=failed_task.id,
        commit=False,
    )
    write_audit_log(
        db,
        actor_id="system",
        actor_name="系统治理",
        actor_role="admin",
        action="task_failed_rollback",
        target_type="learning_report",
        target_id=failed_task.id,
        status="failed",
        detail=failed_task.error_message,
        commit=False,
    )
    write_audit_log(
        db,
        actor_id="system_demo_seed",
        actor_name="演示数据初始化",
        actor_role="system",
        action="resource_pack_submitted",
        target_type="review_item",
        target_id=resource_task.id,
        status="success",
        detail="资源包已生成并进入教师复核。",
        commit=False,
    )
    db.commit()


def review_item_to_dict(item: ReviewItem) -> dict[str, Any]:
    content = loads(item.content_json, {})
    return {
        "id": item.id,
        "item_type": item.item_type,
        "item_title": item.item_title,
        "source_task_id": item.source_task_id,
        "content": content,
        "status": item.status,
        "reviewer_id": item.reviewer_id,
        "reviewer_name": item.reviewer_name,
        "review_comment": item.review_comment or "",
        "created_at": item.created_at.isoformat(),
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else "",
        "published_at": item.published_at.isoformat() if item.published_at else "",
        "confidence": content.get("confidence", 0.86),
        "risk_tip": content.get("risk_tip", "低依据风险已进入人工复核。"),
        "generation_basis": content.get("generation_basis", []),
        "actor_name": item.reviewer_name or "",
    }


def task_to_dict(item: AITaskRun) -> dict[str, Any]:
    return {
        "id": item.id,
        "task_type": item.task_type,
        "title": item.title,
        "actor_id": item.actor_id,
        "actor_role": item.actor_role,
        "input_summary": item.input_summary or "",
        "output_summary": item.output_summary or "",
        "status": item.status,
        "confidence": item.confidence,
        "error_message": item.error_message or "",
        "trace": loads(item.trace_json, {}),
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }


def version_to_dict(item: ContentVersion | None) -> dict[str, Any] | None:
    if not item:
        return None
    return {
        "id": item.id,
        "item_type": item.item_type,
        "item_key": item.item_key,
        "version_no": item.version_no,
        "content": loads(item.content_json, {}),
        "status": item.status,
        "is_active": item.is_active,
        "source_task_id": item.source_task_id,
        "created_at": item.created_at.isoformat(),
    }


def approve_review_item(db: Session, item: ReviewItem, user: dict[str, Any], comment: str) -> ReviewItem:
    actor_id, actor_name, actor_role = current_user_label(user)
    content = loads(item.content_json, {})
    item.status = "published"
    item.reviewer_id = actor_id
    item.reviewer_name = actor_name
    item.review_comment = comment or "审核通过，允许发布到学生端。"
    item.reviewed_at = datetime.utcnow()
    item.published_at = datetime.utcnow()
    task = db.query(AITaskRun).filter(AITaskRun.id == item.source_task_id).first() if item.source_task_id else None
    if task:
        task.status = "published"
        task.updated_at = datetime.utcnow()
    create_content_version(
        db,
        item_type=item.item_type,
        item_key=content.get("item_key") or DEFAULT_ITEM_KEY.get(item.item_type, item.item_type),
        content={**content, "review_comment": item.review_comment, "status_text": "已发布"},
        status="published",
        is_active=True,
        source_task_id=item.source_task_id,
        commit=False,
    )
    write_audit_log(
        db,
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action="review_approved",
        target_type=item.item_type,
        target_id=item.id,
        status="success",
        detail=item.review_comment,
        commit=False,
    )
    db.commit()
    db.refresh(item)
    return item


def reject_review_item(db: Session, item: ReviewItem, user: dict[str, Any], comment: str) -> ReviewItem:
    actor_id, actor_name, actor_role = current_user_label(user)
    item.status = "rejected"
    item.reviewer_id = actor_id
    item.reviewer_name = actor_name
    item.review_comment = comment or "已驳回，学生端继续展示上一版已发布内容。"
    item.reviewed_at = datetime.utcnow()
    task = db.query(AITaskRun).filter(AITaskRun.id == item.source_task_id).first() if item.source_task_id else None
    if task:
        task.status = "rejected"
        task.updated_at = datetime.utcnow()
    write_audit_log(
        db,
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action="review_rejected",
        target_type=item.item_type,
        target_id=item.id,
        status="success",
        detail=item.review_comment,
        commit=False,
    )
    db.commit()
    db.refresh(item)
    return item


def build_retry_context(audit_result: dict[str, Any], teacher_comment: str | None = None) -> dict[str, Any]:
    checks = audit_result.get("checks") or []
    failed_rules = [
        item.get("dimension") or item.get("rule")
        for item in checks
        if isinstance(item, dict) and item.get("status") not in {None, "pass", "PASS"}
    ]
    curriculum = audit_result.get("rule_engine_result", {}).get("curriculum") or audit_result.get("curriculum") or {}
    unsafe_phrases = []
    for item in checks:
        if isinstance(item, dict) and item.get("status") == "error":
            unsafe_phrases.append(item.get("message") or item.get("dimension"))
    return {
        "risk_type": audit_result.get("risk_level") or "medium",
        "failed_rules": [item for item in failed_rules if item],
        "unsafe_phrases": [item for item in unsafe_phrases if item],
        "curriculum_boundary_warning": curriculum.get("boundary_warning") or audit_result.get("boundary_warning") or "",
        "teacher_comment": teacher_comment or "",
    }


def create_teacher_arbitration_state(state: dict[str, Any]) -> dict[str, Any]:
    run_id = str(state.get("run_id") or f"run-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    retry_count = int(state.get("retry_count") or 0)
    audit = state.get("audit_result") or {}
    revision_count = int(state.get("teacher_revision_count") or 0)
    item_id = str(state.get("arbitration_item_id") or f"arb-{run_id}-{retry_count}-{revision_count}")
    review_item = {
        "item_id": item_id,
        "item_type": "resource_pack",
        "status": "pending_review",
        "risk_level": audit.get("risk_level", "medium"),
        "retry_count": retry_count,
        "content_summary": summarize_text(state.get("generated_resources", []), 240),
        "created_at": datetime.utcnow().isoformat(),
    }
    audit_log = {
        "run_id": run_id,
        "item_id": item_id,
        "decision": "pending",
        "teacher_comment": "",
        "previous_status": audit.get("review_status", "needs_review"),
        "next_status": "pending_review",
        "retry_count": retry_count,
        "timestamp": datetime.utcnow().isoformat(),
    }
    ai_task_run = {
        "run_id": run_id,
        "task_type": "teacher_arbitration",
        "status": "pending_review",
        "current_node": "TeacherArbitration",
    }
    return {
        "status": "pending",
        "decision": None,
        "reason": "高风险或多次审核未通过，等待教师 approve / revise / reject。",
        "allowed_actions": ["approve", "revise", "reject"],
        "review_item": review_item,
        "audit_log": audit_log,
        "ai_task_run": ai_task_run,
    }


def resume_after_teacher_decision(
    state: dict[str, Any],
    decision: str,
    teacher_comment: str = "",
    revised_content: str | None = None,
) -> dict[str, Any]:
    if decision not in {"approve", "revise", "reject"}:
        raise ValueError("decision 必须是 approve / revise / reject")
    previous = state.get("current_node") or "TeacherArbitration"
    retry_count = int(state.get("retry_count") or 0)
    result = {
        **(state.get("teacher_arbitration_result") or create_teacher_arbitration_state(state)),
        "status": {"approve": "approved", "revise": "revised", "reject": "rejected"}[decision],
        "decision": decision,
        "teacher_comment": teacher_comment,
        "revised_content": revised_content,
        "decided_at": datetime.utcnow().isoformat(),
    }
    next_node = "ReporterAgent" if decision == "approve" else "ResourceAgent" if decision == "revise" else "END"
    next_status = "success" if decision == "approve" else "generating" if decision == "revise" else "rejected"
    log = {
        "run_id": str(state.get("run_id") or ""),
        "item_id": result.get("review_item", {}).get("item_id") or state.get("arbitration_item_id") or "",
        "decision": decision,
        "teacher_comment": teacher_comment,
        "previous_status": previous,
        "next_status": next_status,
        "retry_count": retry_count,
        "timestamp": datetime.utcnow().isoformat(),
    }
    next_state = {
        **state,
        "teacher_arbitration_result": result,
        "teacher_decision_log": [*state.get("teacher_decision_log", []), log],
        "current_node": next_node,
        "status": next_status,
        "messages": [*state.get("messages", []), f"教师仲裁 {decision}，下一节点：{next_node}"],
    }
    if decision == "revise":
        next_state["teacher_revision_count"] = int(state.get("teacher_revision_count") or 0) + 1
        next_state["retry_context"] = build_retry_context(state.get("audit_result") or {}, teacher_comment)
        next_state["retry_context"]["teacher_revised_content"] = revised_content or ""
        next_state["teacher_revised_content"] = revised_content
    if decision == "approve":
        next_state["audit_result"] = {
            **(state.get("audit_result") or {}),
            "review_status": "teacher_approved",
            "teacher_override": True,
            "teacher_comment": teacher_comment,
        }
    if decision == "reject":
        next_state["audit_result"] = {
            **(state.get("audit_result") or {}),
            "review_status": "rejected",
            "teacher_override": False,
            "teacher_comment": teacher_comment,
        }
        next_state["publication_blocked"] = True
        next_state["rejection_reason"] = teacher_comment or "教师拒绝该版本，终止资源发布。"
    return next_state


def _sync_agent_run_artifacts(db: Session, item: AgentRun, state: dict[str, Any]) -> dict[str, Any]:
    if not item.student_profile_id:
        return {}

    generated = state.get("generated_resources") or []
    existing_resources = (
        db.query(GeneratedResource)
        .filter(GeneratedResource.student_profile_id == item.student_profile_id)
        .order_by(GeneratedResource.id.asc())
        .all()
    )
    decision = (state.get("teacher_arbitration_result") or {}).get("decision")
    if state.get("status") == "success":
        audit_status = "teacher_approved" if decision == "approve" else "passed"
        generation_status = "generated"
    elif state.get("status") == "rejected":
        audit_status = "rejected"
        generation_status = "blocked"
    else:
        audit_status = "pending_review"
        generation_status = "draft"

    resource_ids: list[int] = []
    for index, payload in enumerate(generated):
        row = existing_resources[index] if index < len(existing_resources) else GeneratedResource(
            course_id=item.course_id,
            student_profile_id=item.student_profile_id,
            resource_type=str(payload.get("resource_type") or "resource"),
            title=str(payload.get("title") or "学习资源"),
            content=str(payload.get("content") or ""),
            source_agent=str(payload.get("source_agent") or "ResourceAgent"),
        )
        row.resource_type = str(payload.get("resource_type") or row.resource_type or "resource")
        row.title = str(payload.get("title") or row.title or "学习资源")
        row.content = str(payload.get("content") or "")
        row.difficulty = payload.get("difficulty")
        row.source_agent = str(payload.get("source_agent") or row.source_agent or "ResourceAgent")
        row.recommend_reason = payload.get("recommend_reason") or payload.get("recommendation_reason")
        row.generation_status = generation_status
        row.audit_status = audit_status
        db.add(row)
        db.flush()
        resource_ids.append(row.id)

    quiz_id = None
    quiz_payload = state.get("quiz")
    if quiz_payload:
        quiz = (
            db.query(Quiz)
            .filter(Quiz.student_profile_id == item.student_profile_id, Quiz.course_id == item.course_id)
            .order_by(Quiz.id.desc())
            .first()
        )
        if quiz is None:
            quiz = Quiz(course_id=item.course_id, student_profile_id=item.student_profile_id, quiz_json=dumps(quiz_payload))
            db.add(quiz)
        else:
            quiz.quiz_json = dumps(quiz_payload)
        db.flush()
        quiz_id = quiz.id

    report_id = None
    report_path = str(state.get("report_path") or "")
    if state.get("status") == "success" and report_path:
        report = (
            db.query(LearningReport)
            .filter(
                LearningReport.student_profile_id == item.student_profile_id,
                LearningReport.course_id == item.course_id,
            )
            .order_by(LearningReport.id.desc())
            .first()
        )
        if report is None:
            report = LearningReport(
                student_profile_id=item.student_profile_id,
                course_id=item.course_id,
                report_title=f"Agent 学习报告 - {item.run_id or item.id}",
                report_path=report_path,
                report_json=dumps(state.get("report_summary") or {}),
            )
            db.add(report)
        else:
            report.report_path = report_path
            report.report_json = dumps(state.get("report_summary") or {})
        db.flush()
        report_id = report.id

    return {"resource_ids": resource_ids, "quiz_id": quiz_id, "report_id": report_id}


def _merge_agent_output(item: AgentRun, state: dict[str, Any], artifact_ids: dict[str, Any]) -> dict[str, Any]:
    output = loads(item.output_json, {})
    for key in (
        "student_profile",
        "knowledge_query",
        "knowledge_evidence",
        "learning_path",
        "resource_plan",
        "generated_resources",
        "quiz",
        "tutor_answer",
        "retrieved_context",
        "evaluation_result",
        "audit_result",
        "report_path",
        "report_summary",
        "messages",
        "teacher_arbitration_result",
        "teacher_decision_log",
        "retry_count",
    ):
        if key in state:
            output[key] = state[key]
    output.update({key: value for key, value in artifact_ids.items() if value is not None})
    output["agent_run_id"] = item.id
    output["status"] = state.get("status", item.status)
    summary = output.get("workflow_summary") or {}
    summary.update(
        {
            "status": output["status"],
            "success_rate": 100 if output["status"] == "success" else 0,
        }
    )
    output["workflow_summary"] = summary
    return output


def apply_teacher_arbitration_decision(
    db: Session,
    *,
    item: AgentRun,
    item_id: str,
    current_user: dict[str, Any],
    decision: str,
    teacher_comment: str,
    decision_request_id: str,
    arbitration_item_id: str,
    revised_content: str | None = None,
    suggested_action: str | None = None,
) -> dict[str, Any]:
    arbitration = loads(item.teacher_arbitration_result, {})
    if item.status != "pending_review" or item.current_node != "TeacherArbitration":
        raise ValueError("该任务当前不处于待仲裁状态")
    if arbitration and arbitration.get("status") != "pending":
        raise ValueError("该任务已完成仲裁，不得重复执行")
    state = loads(item.state, {})
    next_state = resume_after_teacher_decision(state, decision, teacher_comment, revised_content)
    can_resume = bool(next_state.get("course_id") and "generated_resources" in next_state)
    if can_resume:
        from app.agents.graph import continue_after_teacher_arbitration

        next_state = continue_after_teacher_arbitration(next_state)
    artifact_ids: dict[str, Any] = {}
    artifact_ids = _sync_agent_run_artifacts(db, item, next_state)
    item.teacher_arbitration_result = dumps(next_state["teacher_arbitration_result"])
    item.state = dumps(next_state)
    item.messages = dumps(next_state.get("messages", []))
    item.current_node = next_state["current_node"]
    item.status = next_state["status"]
    item.output_json = dumps(_merge_agent_output(item, next_state, artifact_ids))
    if next_state["status"] in {"success", "rejected"}:
        item.finished_at = datetime.utcnow()
    else:
        item.finished_at = None
    log_detail = next_state["teacher_decision_log"][-1]
    actor_id, actor_name, actor_role = current_user_label(current_user)
    row = AuditLog(
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action="teacher_arbitration_decision",
        target_type="teacher_arbitration",
        target_id=item_id,
        status=decision,
        detail=redact_payload(teacher_comment),
        retry_count=log_detail["retry_count"],
        rule_engine_result=dumps({**log_detail, "revised_content": revised_content, "suggested_action": suggested_action}),
        xfyun_result=dumps({"status": "not_configured", "message": "使用本地 fallback 记录教师仲裁。"}),
        risk_level=loads(item.audit_result, {}).get("risk_level", "medium"),
        arbitration_status="completed",
        decision_request_id=decision_request_id,
        arbitration_item_id=arbitration_item_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "state": next_state,
        "audit_log": row,
        "next_node": next_state["current_node"],
        "status": next_state["teacher_arbitration_result"]["status"],
        "run_status": next_state["status"],
        "artifacts": artifact_ids,
    }
