from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AgentRun, Course, CourseDocument, LearningReport, SystemLog, TutorQuestionLog
from app.services.json_utils import dumps, loads


router = APIRouter(prefix="/logs", tags=["logs"])


TYPE_TO_CATEGORY = {
    "qa": "qa",
    "document_upload": "knowledge",
    "agent_workflow": "agent",
    "report_generation": "report",
    "error": "error",
    "system": "system",
    "business_event": "event",
}


def _short(value: Any, fallback: str = "暂无内容", limit: int = 160) -> str:
    if value is None:
        return fallback
    text = value if isinstance(value, str) else str(value)
    text = text.strip() or fallback
    return text if len(text) <= limit else f"{text[:limit]}..."


def _course_titles(db: Session) -> dict[int, str]:
    return {item.id: item.title for item in db.query(Course).all()}


def _to_iso(value: datetime) -> str:
    return value.isoformat()


def _base_log(
    *,
    log_id: str,
    created_at: datetime,
    type: str,
    title: str,
    content: str,
    level: str,
    module: str,
    user: str = "demo_teacher",
    related_id: str | int | None = None,
    duration_ms: int = 0,
    status: str = "success",
    error_message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    category = TYPE_TO_CATEGORY.get(type, type)
    return {
        "id": log_id,
        "type": type,
        "category": category,
        "title": title,
        "content": content,
        "summary": _short(content),
        "level": level,
        "module": module,
        "user": user,
        "related_id": related_id,
        "related_type": type,
        "created_at": _to_iso(created_at),
        "time": _to_iso(created_at),
        "duration_ms": duration_ms,
        "status": status,
        "error_message": error_message or "",
        "metadata": metadata or {},
        "action": title,
        "source": module,
        "course_id": metadata.get("course_id") if metadata else None,
        "course_title": metadata.get("course_title", "暂无关联课程") if metadata else "暂无关联课程",
        "suggestion": metadata.get("suggestion", "当前日志用于演示可观测链路，后续可接入真实采集器。") if metadata else "当前日志用于演示可观测链路，后续可接入真实采集器。",
    }


def _fallback_logs() -> list[dict[str, Any]]:
    now = datetime.utcnow()
    return [
        _base_log(
            log_id="demo-fallback-qa",
            created_at=now,
            type="qa",
            title="演示问答日志",
            content="暂无真实问答记录，日志中心使用本地数据保持页面可查看。",
            level="INFO",
            module="TutorChat",
            status="demo",
            metadata={"demo": True, "suggestion": "进入智能答疑页面提交问题后会产生真实问答日志。"},
        ),
        _base_log(
            log_id="demo-fallback-document",
            created_at=now,
            type="document_upload",
            title="演示文档上传日志",
            content="暂无知识库文档记录，建议先运行演示数据脚本或上传课程资料。",
            level="WARNING",
            module="KnowledgeBase",
            status="demo",
            metadata={"demo": True, "suggestion": "上传 PDF、Word、TXT 或 Markdown 后会形成解析日志。"},
        ),
    ]


def _collect_logs(db: Session) -> list[dict[str, Any]]:
    course_titles = _course_titles(db)
    rows: list[dict[str, Any]] = []

    for item in db.query(SystemLog).order_by(SystemLog.created_at.desc()).limit(200).all():
        rows.append(
            _base_log(
                log_id=f"log-{item.id}",
                created_at=item.created_at,
                type=item.type,
                title=item.title,
                content=item.content,
                level=item.level,
                module=item.module,
                user=item.user,
                related_id=item.related_id,
                duration_ms=item.duration_ms,
                status=item.status,
                error_message=item.error_message,
                metadata=loads(item.metadata_json, {}),
            )
        )

    for item in db.query(CourseDocument).order_by(CourseDocument.created_at.desc()).limit(80).all():
        status = item.parse_status or "unknown"
        level = "SUCCESS" if status in {"parsed", "indexed"} else "ERROR" if status == "failed" else "WARNING"
        rows.append(
            _base_log(
                log_id=f"kb-{item.id}",
                created_at=item.created_at,
                type="document_upload",
                title="知识库文档解析",
                content=f"{item.filename} 已进入知识库处理链路，解析状态 {status}，切片数 {item.chunk_count}。",
                level=level,
                module="KnowledgeBase",
                related_id=item.id,
                duration_ms=max(120, int(item.chunk_count or 1) * 38),
                status=status,
                error_message="文档解析失败，请检查格式或内容。" if status == "failed" else "",
                metadata={
                    "course_id": item.course_id,
                    "course_title": course_titles.get(item.course_id, "未知课程"),
                    "file_type": item.file_type,
                    "chunk_count": item.chunk_count,
                },
            )
        )

    for item in db.query(TutorQuestionLog).order_by(TutorQuestionLog.created_at.desc()).limit(100).all():
        contexts = loads(item.contexts_json, [])
        rows.append(
            _base_log(
                log_id=f"qa-{item.id}",
                created_at=item.created_at,
                type="qa",
                title="智能答疑",
                content=item.question,
                level="SUCCESS",
                module="TutorChat",
                related_id=item.id,
                duration_ms=640 + len(contexts) * 80,
                status="answered",
                metadata={
                    "course_id": item.course_id,
                    "course_title": course_titles.get(item.course_id, "未知课程"),
                    "mode": item.mode,
                    "citation_count": len(contexts),
                    "based_on_material": bool(contexts),
                },
            )
        )

    for item in db.query(AgentRun).order_by(AgentRun.created_at.desc()).limit(80).all():
        output = loads(item.output_json, {}) if item.output_json else {}
        input_data = loads(item.input_json, {}) if item.input_json else {}
        summary = output.get("workflow_summary", {})
        status = item.status or "unknown"
        rows.append(
            _base_log(
                log_id=f"agent-{item.id}",
                created_at=item.created_at,
                type="agent_workflow",
                title="Agent 工作流运行",
                content=_short(input_data.get("learning_goal") or item.workflow_name, "Agent 工作流运行记录"),
                level="ERROR" if status == "failed" else "SUCCESS" if status == "success" else "INFO",
                module="AgentWorkflow",
                related_id=item.id,
                duration_ms=int(summary.get("duration_ms") or 0),
                status=status,
                error_message=_short(output.get("error"), "", 200) if status == "failed" else "",
                metadata={
                    "course_id": item.course_id,
                    "course_title": course_titles.get(item.course_id, "未知课程"),
                    "run_id": f"run-{item.id:06d}",
                    "langgraph_run_id": output.get("langgraph_run_id"),
                    "step_count": len(output.get("steps", [])),
                },
            )
        )

    for item in db.query(LearningReport).order_by(LearningReport.created_at.desc()).limit(80).all():
        data = loads(item.report_json, {})
        rows.append(
            _base_log(
                log_id=f"report-{item.id}",
                created_at=item.created_at,
                type="report_generation",
                title="学习报告生成",
                content=item.report_title,
                level="SUCCESS",
                module="ReportCenter",
                related_id=item.id,
                duration_ms=int(data.get("duration_ms") or 1200),
                status="completed" if item.report_path else "recorded",
                metadata={
                    "course_id": item.course_id,
                    "course_title": course_titles.get(item.course_id, "未知课程"),
                    "quality_score": data.get("score") or data.get("quality_score"),
                    "reference_count": len(data.get("references", []) or []),
                },
            )
        )

    if not rows:
        rows.extend(_fallback_logs())
    return rows


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _apply_filters(
    logs: list[dict[str, Any]],
    type: str | None,
    category: str | None,
    level: str | None,
    module: str | None,
    keyword: str | None,
    start_time: str | None,
    end_time: str | None,
) -> list[dict[str, Any]]:
    keyword_text = (keyword or "").strip().lower()
    start_dt = _parse_dt(start_time)
    end_dt = _parse_dt(end_time)

    rows = []
    for item in logs:
        created_at = _parse_dt(str(item["created_at"]))
        haystack = " ".join(
            str(item.get(key, ""))
            for key in ("title", "content", "summary", "module", "course_title", "status", "error_message")
        ).lower()
        if type and type != "all" and item["type"] != type:
            continue
        if category and category != "all" and item["category"] != category:
            continue
        if level and level != "all" and item["level"] != level:
            continue
        if module and module != "all" and item["module"] != module:
            continue
        if keyword_text and keyword_text not in haystack:
            continue
        if start_dt and created_at and created_at < start_dt:
            continue
        if end_dt and created_at and created_at > end_dt:
            continue
        rows.append(item)
    return rows


@router.get("")
def list_logs(
    type: str | None = None,
    category: str | None = None,
    level: str | None = None,
    module: str | None = None,
    keyword: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    order: str = "desc",
    limit: int = 120,
    db: Session = Depends(get_db),
):
    rows = _apply_filters(_collect_logs(db), type, category, level, module, keyword, start_time, end_time)
    reverse = order != "asc"
    rows = sorted(rows, key=lambda item: item["created_at"], reverse=reverse)
    return rows[: min(max(limit, 1), 200)]


@router.get("/summary")
def logs_summary(db: Session = Depends(get_db)):
    rows = _collect_logs(db)
    today = datetime.utcnow().date()
    return {
        "today_log_count": sum(1 for item in rows if _parse_dt(str(item["created_at"])).date() == today),
        "error_log_count": sum(1 for item in rows if item["level"] == "ERROR" or item["type"] == "error"),
        "agent_run_count": sum(1 for item in rows if item["type"] == "agent_workflow"),
        "question_count": sum(1 for item in rows if item["type"] == "qa"),
        "total_count": len(rows),
        "type_counts": {key: sum(1 for item in rows if item["type"] == key) for key in TYPE_TO_CATEGORY},
    }


@router.get("/{log_id}")
def get_log_detail(log_id: str, db: Session = Depends(get_db)):
    for item in _collect_logs(db):
        if item["id"] == log_id:
            return item
    raise HTTPException(status_code=404, detail="日志不存在")


def create_demo_log(
    db: Session,
    *,
    type: str,
    title: str,
    content: str,
    module: str,
    level: str = "INFO",
    status: str = "success",
    related_id: str | int | None = None,
    duration_ms: int = 0,
    error_message: str | None = None,
    metadata: dict[str, Any] | None = None,
    created_at: datetime | None = None,
) -> SystemLog:
    item = SystemLog(
        type=type,
        title=title,
        content=content,
        level=level,
        module=module,
        related_id=str(related_id) if related_id is not None else None,
        duration_ms=duration_ms,
        status=status,
        error_message=error_message,
        metadata_json=dumps({"demo": True, **(metadata or {})}),
        created_at=created_at or datetime.utcnow(),
    )
    db.add(item)
    return item
