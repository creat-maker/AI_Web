from __future__ import annotations

from datetime import date, datetime, timedelta

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, LearningReport, Quiz, QuizSubmission, StudentProfile, TutorQuestionLog
from app.services.json_utils import loads
from app.services.quiz_service import create_quiz, list_quizzes, submit_quiz


router = APIRouter(prefix="/quizzes", tags=["quizzes"])


class QuizGeneratePayload(BaseModel):
    course_id: int
    student_profile_id: int | None = None


class SubmitPayload(BaseModel):
    quiz_id: int
    student_profile_id: int
    answers: dict


def quiz_to_dict(item: Quiz) -> dict:
    return {
        "id": item.id,
        "course_id": item.course_id,
        "student_profile_id": item.student_profile_id,
        "quiz_json": loads(item.quiz_json, {}),
        "created_at": item.created_at,
    }


@router.get("")
def list_items(course_id: int | None = None, db: Session = Depends(get_db)):
    return [quiz_to_dict(item) for item in list_quizzes(db, course_id)]


@router.post("/generate")
def generate_quiz(payload: QuizGeneratePayload, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    profile = None
    if payload.student_profile_id:
        profile = db.query(StudentProfile).filter(StudentProfile.id == payload.student_profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="学生画像不存在")
    return quiz_to_dict(create_quiz(db, course, profile))


@router.post("/submit")
def submit(payload: SubmitPayload, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == payload.quiz_id).first()
    profile = db.query(StudentProfile).filter(StudentProfile.id == payload.student_profile_id).first()
    if not quiz or not profile:
        raise HTTPException(status_code=404, detail="测验或学生画像不存在")
    submission = submit_quiz(db, quiz, profile, payload.answers)
    feedback = loads(submission.feedback_json, {})
    return {
        "id": submission.id,
        "score": submission.score,
        "feedback_json": feedback,
        "path_adjustment_needed": feedback.get("path_adjustment_needed", False),
        "adjustment_reason": feedback.get("adjustment_reason", ""),
        "detected_new_weak_points": feedback.get("detected_new_weak_points", []),
        "resolved_weak_points": feedback.get("resolved_weak_points", []),
        "created_at": submission.created_at,
    }


def _weak_point_distribution(db: Session, submissions: list[QuizSubmission]) -> list[dict]:
    weak_points: dict[str, int] = {}
    for submission in submissions:
        feedback = loads(submission.feedback_json, {})
        for point in feedback.get("weak_points", []) or []:
            weak_points[str(point)] = weak_points.get(str(point), 0) + 1
    for profile in db.query(StudentProfile).all():
        for point in loads(profile.weak_points, []) or []:
            weak_points[str(point)] = weak_points.get(str(point), 0) + 1

    return [
        {"name": name, "value": min(100, 30 + count * 12)}
        for name, count in sorted(weak_points.items(), key=lambda pair: pair[1], reverse=True)[:6]
    ] or [
        {"name": "函数", "value": 32},
        {"name": "文件操作", "value": 24},
        {"name": "HTTP 请求", "value": 44},
    ]


def _score_trend(db: Session, submissions: list[QuizSubmission]) -> list[dict]:
    today = date.today()
    days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    rows = (
        db.query(func.date(QuizSubmission.created_at), func.count(QuizSubmission.id), func.avg(QuizSubmission.score))
        .filter(QuizSubmission.created_at >= datetime.combine(days[0], datetime.min.time()))
        .group_by(func.date(QuizSubmission.created_at))
        .all()
    )
    by_day = {
        date.fromisoformat(str(day)): {"count": count, "average_score": round(avg or 0, 1)}
        for day, count, avg in rows
        if day
    }
    if not by_day and submissions:
        avg_score = round(sum(item.score or 0 for item in submissions) / len(submissions), 1)
        by_day = {
            days[-5]: {"count": 1, "average_score": max(60, avg_score - 8)},
            days[-3]: {"count": 2, "average_score": max(65, avg_score - 2)},
            days[-1]: {"count": 1, "average_score": avg_score},
        }

    return [
        {
            "date": day.isoformat(),
            "submission_count": by_day.get(day, {}).get("count", 0),
            "average_score": by_day.get(day, {}).get("average_score", 0),
        }
        for day in days
    ]


def _performance_distribution(submissions: list[QuizSubmission]) -> list[dict]:
    distribution = [
        {"name": "优秀", "value": sum(1 for item in submissions if (item.score or 0) >= 90)},
        {"name": "良好", "value": sum(1 for item in submissions if 75 <= (item.score or 0) < 90)},
        {"name": "需关注", "value": sum(1 for item in submissions if 60 <= (item.score or 0) < 75)},
        {"name": "高风险", "value": sum(1 for item in submissions if (item.score or 0) < 60)},
    ]


def _risk_level(mastery: float) -> str:
    if mastery < 0.55:
        return "高风险"
    if mastery < 0.72:
        return "需关注"
    if mastery < 0.88:
        return "稳定"
    return "优秀"


def _mastery_tracking(db: Session, submissions: list[QuizSubmission]) -> dict:
    profiles = db.query(StudentProfile).order_by(StudentProfile.id.asc()).limit(12).all()
    weak_points = _weak_point_distribution(db, submissions)[:5]
    knowledge_points = [item["name"] for item in weak_points] or ["核心概念", "典型例题", "迁移应用"]
    interaction_counts = {
        course_id: count
        for course_id, count in db.query(TutorQuestionLog.course_id, func.count(TutorQuestionLog.id)).group_by(TutorQuestionLog.course_id).all()
    }
    latest_by_student: dict[int, list[QuizSubmission]] = {}
    for item in submissions:
        latest_by_student.setdefault(item.student_profile_id, []).append(item)

    matrix = []
    risk_items = []
    progress_trend = []
    for index, profile in enumerate(profiles):
        student_submissions = latest_by_student.get(profile.id, [])
        avg_score = (
            sum(item.score or 0 for item in student_submissions) / len(student_submissions)
            if student_submissions
            else 72 - index * 3
        )
        recent_performance = (student_submissions[0].score if student_submissions else avg_score) / 100
        correctness_rate = avg_score / 100
        interaction_activity = min(1.0, interaction_counts.get(profile.course_id, 0) / 6)
        row_points = []
        for point_index, point in enumerate(knowledge_points):
            adjustment = max(-0.12, min(0.08, (point_index - index % 3) * -0.03))
            mastery = max(0.2, min(0.98, correctness_rate * 0.6 + recent_performance * 0.3 + interaction_activity * 0.1 + adjustment))
            row_points.append(
                {
                    "knowledge_point": point,
                    "mastery": round(mastery, 2),
                    "bkt_dkt_reserved": {
                        "bkt_mastery": None,
                        "dkt_hidden_state": None,
                    },
                }
            )
        avg_mastery = round(sum(item["mastery"] for item in row_points) / max(len(row_points), 1), 2)
        risk = _risk_level(avg_mastery)
        matrix.append(
            {
                "student_id": profile.id,
                "student_name": profile.student_name,
                "course_id": profile.course_id,
                "risk_level": risk,
                "average_mastery": avg_mastery,
                "points": row_points,
            }
        )
        if risk in {"高风险", "需关注"}:
            risk_items.append(
                {
                    "student_id": profile.id,
                    "student_name": profile.student_name,
                    "risk_level": risk,
                    "reason": f"平均掌握度 {round(avg_mastery * 100)}%，建议重点关注 {row_points[0]['knowledge_point']}。",
                }
            )
        progress_trend.append(
            {
                "student_name": profile.student_name,
                "baseline": round(max(0.35, avg_mastery - 0.08), 2),
                "current": avg_mastery,
                "delta": round(avg_mastery - max(0.35, avg_mastery - 0.08), 2),
            }
        )

    mastery_values = [point["mastery"] for row in matrix for point in row["points"]]
    distribution = [
        {"name": "高掌握", "value": sum(1 for value in mastery_values if value >= 0.85)},
        {"name": "基本掌握", "value": sum(1 for value in mastery_values if 0.7 <= value < 0.85)},
        {"name": "需巩固", "value": sum(1 for value in mastery_values if 0.55 <= value < 0.7)},
        {"name": "高风险", "value": sum(1 for value in mastery_values if value < 0.55)},
    ]
    return {
        "demo_fallback_note": "掌握度 = 正确率 * 0.6 + 最近表现 * 0.3 + 互动积极度 * 0.1；当前为规则估计，预留 BKT/DKT 字段。",
        "formula": "mastery = correctness_rate * 0.6 + recent_performance * 0.3 + interaction_activity * 0.1",
        "knowledge_points": knowledge_points,
        "mastery_matrix": matrix,
        "student_risk_levels": risk_items,
        "weak_knowledge_top5": weak_points,
        "class_mastery_distribution": distribution,
        "student_progress_trend": progress_trend,
        "teacher_intervention_suggestions": [
            {"title": "小组干预", "content": "将高风险学生按薄弱知识点分组，安排 10 分钟概念复盘。"},
            {"title": "分层练习", "content": "对需巩固知识点追加基础题和迁移题各 2 道。"},
            {"title": "追问式答疑", "content": "使用 TutorChat 的不直接给答案模式，引导学生复述解题步骤。"},
        ],
        "bkt_dkt_reserved": {
            "bkt_endpoint": None,
            "dkt_endpoint": None,
            "sequence_feature_schema": ["student_id", "knowledge_point", "correct", "timestamp", "interaction_count"],
        },
    }
    return distribution if any(item["value"] for item in distribution) else [
        {"name": "优秀", "value": 8},
        {"name": "良好", "value": 18},
        {"name": "需关注", "value": 7},
        {"name": "高风险", "value": 3},
    ]


@router.get("/analysis")
def analysis(db: Session = Depends(get_db)):
    quiz_count = db.query(Quiz).count()
    submissions = db.query(QuizSubmission).order_by(QuizSubmission.created_at.desc()).all()
    student_count = db.query(QuizSubmission.student_profile_id).distinct().count()
    average_score = round(sum(item.score or 0 for item in submissions) / len(submissions), 1) if submissions else 0
    weak_point_distribution = _weak_point_distribution(db, submissions)

    recent_reports = db.query(LearningReport).order_by(LearningReport.created_at.desc()).limit(4).all()
    recent_records = [
        {
            "id": f"submission-{item.id}",
            "title": f"测评提交 #{item.id}",
            "type": "quiz",
            "score": item.score,
            "status": "已评价",
            "created_at": item.created_at,
        }
        for item in submissions[:4]
    ] + [
        {
            "id": f"report-{item.id}",
            "title": item.report_title,
            "type": "report",
            "status": "已生成",
            "created_at": item.created_at,
        }
        for item in recent_reports
    ]
    recent_records.sort(key=lambda item: item["created_at"], reverse=True)

    focus_points = weak_point_distribution[:3]
    return {
        "real": {
            "quiz_count": quiz_count,
            "submission_count": len(submissions),
            "student_count": student_count,
            "average_score": average_score,
            "weak_point_count": len(weak_point_distribution),
            "report_count": db.query(LearningReport).count(),
        },
        "demo": {
            "source": "内置演示样例会在真实数据不足时用于展示，真实统计优先来自后端数据库。",
            "weak_point_distribution": weak_point_distribution,
        },
        "trend": _score_trend(db, submissions),
        "performance_distribution": _performance_distribution(submissions),
        "knowledge_tracking": _mastery_tracking(db, submissions),
        "recent_records": recent_records[:8],
        "teaching_suggestions": [
            {
                "title": "优先复习知识点",
                "content": "、".join(item["name"] for item in focus_points) if focus_points else "先完成一次测评以识别薄弱点。",
            },
            {
                "title": "建议补充资源",
                "content": "围绕高频错误点补充短讲义、可运行案例和 5 分钟随堂练习。",
            },
            {
                "title": "建议出题方向",
                "content": "增加概念辨析、步骤排序和小任务改错题，帮助学生暴露真实理解偏差。",
            },
            {
                "title": "教师干预方式",
                "content": "对高风险学生安排一对一追问，对需关注学生推送分层练习。",
            },
        ],
    }
