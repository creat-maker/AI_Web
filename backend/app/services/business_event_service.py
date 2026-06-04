from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models import SystemLog
from app.services.json_utils import dumps, loads


EVENT_LOG_TYPE = "business_event"


def record_event(
    db: Session,
    *,
    event_type: str,
    title: str,
    description: str,
    actor_role: str = "demo",
    actor_name: str = "EduMind demo user",
    target_type: str = "system",
    target_id: str | int | None = None,
    related_student: str | None = None,
    related_course: str | None = None,
    status: str = "success",
    metadata: dict[str, Any] | None = None,
    commit: bool = True,
) -> SystemLog:
    payload = {
        "event_type": event_type,
        "actor_role": actor_role,
        "actor_name": actor_name,
        "target_type": target_type,
        "target_id": target_id,
        "related_student": related_student or "",
        "related_course": related_course or "",
        "status": status,
        "metadata": metadata or {},
        "demo_fallback_note": "业务事件写入 system_logs，用于 EduMind 三端演示闭环，不代表真实权限审计系统。",
    }
    item = SystemLog(
        type=EVENT_LOG_TYPE,
        title=title,
        content=description,
        level="INFO" if status in {"success", "completed", "demo"} else "WARNING",
        module="BusinessEvent",
        user=actor_name,
        related_id=str(target_id or ""),
        duration_ms=int((metadata or {}).get("duration_ms") or 0),
        status=status,
        metadata_json=dumps(payload),
    )
    db.add(item)
    if commit:
        db.commit()
        db.refresh(item)
    return item


def event_to_dict(item: SystemLog) -> dict[str, Any]:
    data = loads(item.metadata_json, {})
    metadata = data.get("metadata", {}) if isinstance(data, dict) else {}
    return {
        "id": item.id,
        "event_type": data.get("event_type") or item.type,
        "title": item.title,
        "description": item.content,
        "actor_role": data.get("actor_role", "demo"),
        "actor_name": data.get("actor_name") or item.user,
        "target_type": data.get("target_type", item.module),
        "target_id": data.get("target_id") or item.related_id,
        "related_student": data.get("related_student", ""),
        "related_course": data.get("related_course", metadata.get("course_title", "")),
        "status": data.get("status") or item.status,
        "created_at": item.created_at,
        "metadata": metadata,
        "demo_fallback_note": data.get("demo_fallback_note", "业务事件来自 EduMind demo/fallback 事件服务。"),
    }


def list_events(
    db: Session,
    *,
    event_type: str | None = None,
    actor_role: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    query = db.query(SystemLog).filter(SystemLog.type == EVENT_LOG_TYPE)
    rows = query.order_by(SystemLog.created_at.desc()).limit(max(1, min(limit, 200))).all()
    events = [event_to_dict(item) for item in rows]
    if event_type:
        events = [item for item in events if item["event_type"] == event_type]
    if actor_role:
        events = [item for item in events if item["actor_role"] == actor_role]
    return events
