from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import AgentRun, Course, CourseDocument, LearningReport, QuizSubmission, TutorQuestionLog
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
            "question": "Python 爬虫请求失败时应该先检查什么？",
            "status": "answered",
            "created_at": _as_iso(now - timedelta(hours=2)),
            "source": "mock",
        },
        {
            "id": -2,
            "course_id": 1,
            "workflow_name": "tutor-ask",
            "question": "如何理解 requests 和 BeautifulSoup 的分工？",
            "status": "answered",
            "created_at": _as_iso(now - timedelta(hours=5)),
            "source": "mock",
        },
        {
            "id": -3,
            "course_id": 2,
            "workflow_name": "tutor-ask",
            "question": "知识库引用来源为空时该如何排查？",
            "status": "answered",
            "created_at": _as_iso(now - timedelta(days=1, hours=3)),
            "source": "mock",
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

    if document_count == 0:
        knowledge_status = "empty"
    elif parsed_document_count == document_count:
        knowledge_status = "ready"
    else:
        knowledge_status = "building"

    return {
        "metrics": {
            "course_count": course_count,
            "document_count": document_count,
            "qa_count": qa_count,
            "report_count": report_count,
            "quiz_submission_count": quiz_submission_count,
            "knowledge_chunk_count": int(total_chunks),
        },
        "knowledge_base": {
            "status": knowledge_status,
            "parsed_document_count": parsed_document_count,
            "document_count": document_count,
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

    return {
        "trend": trend,
        "recent_activity": recent_activity[:8],
    }
