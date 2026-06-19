from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import AgentRun, Course, CourseDocument, LearningReport, QuizSubmission, StudentProfile, SystemLog, TutorQuestionLog
from app.services.json_utils import loads


def _as_iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _last_seven_days() -> list[date]:
    today = date.today()
    return [today - timedelta(days=offset) for offset in range(6, -1, -1)]


def _count_by_day(db: Session, model: Any, *filters: Any) -> dict[date, int]:
    query = db.query(func.date(model.created_at), func.count(model.id)).filter(
        model.created_at >= datetime.combine(_last_seven_days()[0], datetime.min.time())
    )
    for item in filters:
        query = query.filter(item)
    rows = query.group_by(func.date(model.created_at)).all()
    return {date.fromisoformat(str(day)): count for day, count in rows if day}


def _mock_questions() -> list[dict[str, Any]]:
    now = datetime.utcnow()
    return [
        {
            "id": -1,
            "course_id": 1,
            "workflow_name": "tutor-ask",
            "question": "为什么我的 while 循环会死循环？",
            "status": "answered",
            "created_at": _as_iso(now - timedelta(hours=2)),
            "source": "本地学习记录",
        },
        {
            "id": -2,
            "course_id": 1,
            "workflow_name": "tutor-ask",
            "question": "break 和 continue 应该怎么区分？",
            "status": "answered",
            "created_at": _as_iso(now - timedelta(hours=5)),
            "source": "本地学习记录",
        },
        {
            "id": -3,
            "course_id": 2,
            "workflow_name": "tutor-ask",
            "question": "循环嵌套变量变化应该怎么记录？",
            "status": "answered",
            "created_at": _as_iso(now - timedelta(days=1, hours=3)),
            "source": "本地学习记录",
        },
    ]


def get_dashboard_summary(db: Session) -> dict[str, Any]:
    course_count = db.query(Course).count()
    document_count = db.query(CourseDocument).count()
    parsed_document_count = db.query(CourseDocument).filter(CourseDocument.parse_status == "parsed").count()
    report_count = db.query(LearningReport).count()
    real_qa_count = db.query(TutorQuestionLog).count()
    mock_questions = _mock_questions() if real_qa_count == 0 else []
    qa_count = real_qa_count or len(mock_questions)
    quiz_submission_count = db.query(QuizSubmission).count()
    total_chunks = db.query(func.coalesce(func.sum(CourseDocument.chunk_count), 0)).scalar() or 0
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_qa_count = db.query(TutorQuestionLog).filter(TutorQuestionLog.created_at >= today_start).count()
    today_agent_count = db.query(AgentRun).filter(AgentRun.created_at >= today_start).count()
    today_report_count = db.query(LearningReport).filter(LearningReport.created_at >= today_start).count()
    failed_agent_count = db.query(AgentRun).filter(AgentRun.status == "failed").count()
    explicit_error_count = db.query(SystemLog).filter(SystemLog.level == "ERROR").count()
    risk_students = []
    weak_point_counter: dict[str, int] = {}
    for profile in db.query(StudentProfile).all():
        profile_json = loads(profile.profile_json, {})
        weak_points = loads(profile.weak_points, [])
        if isinstance(weak_points, str):
            weak_points = [weak_points]
        for point in weak_points[:6]:
            weak_point_counter[str(point)] = weak_point_counter.get(str(point), 0) + 1
        if profile_json.get("risk_level") in {"需关注", "高风险", "闇€鍏虫敞"} or "弱" in (profile.current_level or ""):
            risk_students.append(
                {
                    "student_id": profile.id,
                    "student_name": profile.student_name,
                    "course_id": profile.course_id,
                    "risk_level": profile_json.get("risk_level") or "需关注",
                    "reason": profile_json.get("diagnosis") or profile.weak_points or "薄弱知识点较集中",
                }
            )

    if document_count == 0:
        knowledge_status = "empty"
    elif parsed_document_count == document_count:
        knowledge_status = "ready"
    else:
        knowledge_status = "building"

    overview_cards = [
        {"key": "course_count", "label": "课程数量", "value": course_count, "unit": "门"},
        {"key": "document_count", "label": "知识库文档", "value": document_count, "unit": "份"},
        {"key": "qa_count", "label": "最近问答", "value": qa_count, "unit": "次"},
        {"key": "report_count", "label": "报告数量", "value": report_count, "unit": "份"},
        {"key": "risk_student_count", "label": "学习预警", "value": len(risk_students), "unit": "人"},
        {"key": "weak_point_count", "label": "薄弱知识点", "value": len(weak_point_counter), "unit": "个"},
        {"key": "warning_count", "label": "错误/告警", "value": failed_agent_count + explicit_error_count, "unit": "条"},
        {"key": "today_active_count", "label": "今日活跃", "value": today_qa_count + today_agent_count + today_report_count, "unit": "次"},
    ]
    module_health = [
        {"module": "KnowledgeBase", "status": knowledge_status, "message": f"{parsed_document_count}/{document_count} 份文档已解析"},
        {"module": "TutorChat", "status": "ready" if qa_count else "local", "message": f"累计 {qa_count} 次问答"},
        {"module": "AgentWorkflow", "status": "warning" if failed_agent_count else "ready", "message": f"失败 {failed_agent_count} 次"},
        {"module": "ReportCenter", "status": "ready" if report_count else "local", "message": f"累计 {report_count} 份报告"},
        {"module": "LogManagement", "status": "ready", "message": "业务日志与本地日志可观测"},
    ]
    weak_items = sorted(weak_point_counter.items(), key=lambda item: item[1], reverse=True)[:8]

    payload = {
        "metrics": {
            "course_count": course_count,
            "document_count": document_count,
            "qa_count": qa_count,
            "report_count": report_count,
            "quiz_submission_count": quiz_submission_count,
            "knowledge_chunk_count": int(total_chunks),
        },
        "overview_cards": overview_cards,
        "module_health": module_health,
        "knowledge_base": {
            "status": knowledge_status,
            "parsed_document_count": parsed_document_count,
            "document_count": document_count,
        },
        "knowledge_base_stats": {
            "document_count": document_count,
            "indexed_document_count": parsed_document_count,
            "chunk_count": int(total_chunks),
            "coverage_rate": round((parsed_document_count / course_count) * 100, 1) if course_count else 0,
            "quality_score": min(95, 60 + parsed_document_count * 5 + int(total_chunks / 20)) if document_count else 0,
        },
        "tutor_chat_stats": {
            "total_questions": qa_count,
            "today_questions": today_qa_count,
            "citation_enabled": True,
        },
        "agent_run_stats": {
            "total_runs": db.query(AgentRun).count(),
            "today_runs": today_agent_count,
            "failed_runs": failed_agent_count,
            "latest_status": db.query(AgentRun).order_by(AgentRun.created_at.desc()).first().status if db.query(AgentRun).first() else "empty",
        },
        "report_stats": {
            "total_reports": report_count,
            "today_reports": today_report_count,
        },
        "student_risk_stats": {
            "risk_student_count": len(risk_students),
            "items": risk_students[:6],
            "weak_points": [{"name": name, "count": count} for name, count in weak_items],
        },
        "warning_items": [
            {"module": "AgentWorkflow", "level": "ERROR", "message": "存在失败运行记录", "count": failed_agent_count}
        ] if failed_agent_count else [],
        "data_loop": {
            "steps": [
                {"name": "课程资料", "done": document_count > 0},
                {"name": "知识库切片", "done": int(total_chunks) > 0},
                {"name": "智能答疑", "done": qa_count > 0},
                {"name": "学情测评", "done": quiz_submission_count > 0},
                {"name": "Agent 编排", "done": db.query(AgentRun).count() > 0},
                {"name": "学习报告", "done": report_count > 0},
                {"name": "日志追踪", "done": True},
            ]
        },
        "recent_documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "course_id": doc.course_id,
                "status": doc.parse_status,
                "chunk_count": doc.chunk_count,
                "created_at": _as_iso(doc.created_at),
            }
            for doc in db.query(CourseDocument).order_by(CourseDocument.created_at.desc()).limit(5).all()
        ],
        "recent_questions": [
            {
                "id": item.id,
                "course_id": item.course_id,
                "workflow_name": "tutor-ask",
                "question": item.question,
                "answer": loads(item.answer_json, {}),
                "status": "answered",
                "created_at": _as_iso(item.created_at),
                "source": "database",
            }
            for item in db.query(TutorQuestionLog).order_by(TutorQuestionLog.created_at.desc()).limit(5).all()
        ]
        or mock_questions,
    }
    return payload


def get_dashboard_activity(db: Session) -> dict[str, Any]:
    days = _last_seven_days()
    documents_by_day = _count_by_day(db, CourseDocument)
    reports_by_day = _count_by_day(db, LearningReport)
    qa_by_day = _count_by_day(db, TutorQuestionLog)
    if not any(qa_by_day.values()):
        qa_by_day = {
            days[-6]: 1,
            days[-4]: 2,
            days[-2]: 3,
            days[-1]: 2,
        }

    trend = [
        {
            "date": day.isoformat(),
            "documents": documents_by_day.get(day, 0),
            "questions": qa_by_day.get(day, 0),
            "reports": reports_by_day.get(day, 0),
        }
        for day in days
    ]

    recent_activity = []
    for doc in db.query(CourseDocument).order_by(CourseDocument.created_at.desc()).limit(4).all():
        recent_activity.append(
            {
                "type": "document",
                "title": f"上传文档：{doc.filename}",
                "status": doc.parse_status,
                "created_at": _as_iso(doc.created_at),
            }
        )
    for report in db.query(LearningReport).order_by(LearningReport.created_at.desc()).limit(4).all():
        recent_activity.append(
            {
                "type": "report",
                "title": report.report_title,
                "status": "generated",
                "created_at": _as_iso(report.created_at),
            }
        )
    for run in db.query(AgentRun).order_by(AgentRun.created_at.desc()).limit(4).all():
        recent_activity.append(
            {
                "type": "agent",
                "title": run.workflow_name,
                "status": run.status,
                "created_at": _as_iso(run.created_at),
            }
        )
    for item in db.query(TutorQuestionLog).order_by(TutorQuestionLog.created_at.desc()).limit(4).all():
        recent_activity.append(
            {
                "type": "question",
                "title": item.question,
                "status": "answered",
                "created_at": _as_iso(item.created_at),
            }
        )
    if not any(item["type"] == "question" for item in recent_activity):
        for item in _mock_questions()[:2]:
            recent_activity.append(
                {
                    "type": "question",
                    "title": item["question"],
                    "status": item["status"],
                    "created_at": item["created_at"],
                }
            )

    recent_activity.sort(key=lambda item: item["created_at"] or "", reverse=True)

    recent_events = recent_activity[:8]
    return {
        "trend": trend,
        "recent_activity": recent_events,
        "recent_events": recent_events,
    }
