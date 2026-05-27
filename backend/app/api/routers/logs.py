from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AgentRun, Course, CourseDocument, LearningReport, TutorQuestionLog
from app.services.json_utils import loads


router = APIRouter(prefix="/logs", tags=["logs"])


def _short(value: Any, fallback: str = "暂无内容", limit: int = 120) -> str:
    if value is None:
        return fallback
    text = value if isinstance(value, str) else str(value)
    text = text.strip() or fallback
    return text if len(text) <= limit else f"{text[:limit]}..."


def _course_titles(db: Session) -> dict[int, str]:
    return {item.id: item.title for item in db.query(Course).all()}


def _base_log(
    *,
    log_id: str,
    created_at: datetime,
    level: str,
    category: str,
    module: str,
    action: str,
    summary: str,
    status: str,
    source: str,
    suggestion: str,
    course_id: int | None = None,
    course_title: str | None = None,
    related_id: int | None = None,
    related_type: str | None = None,
    error_message: str | None = None,
) -> dict[str, Any]:
    return {
        "id": log_id,
        "time": created_at,
        "level": level,
        "category": category,
        "module": module,
        "action": action,
        "summary": summary,
        "status": status,
        "source": source,
        "course_id": course_id,
        "course_title": course_title or "暂无关联课程",
        "related_id": related_id,
        "related_type": related_type,
        "error_message": error_message or "",
        "suggestion": suggestion,
    }


def _system_logs() -> list[dict[str, Any]]:
    now = datetime.utcnow()
    return [
        _base_log(
            log_id="system-runtime",
            created_at=now,
            level="INFO",
            category="system",
            module="Dashboard",
            action="读取运行状态",
            summary="系统运行状态已就绪，Dashboard 可聚合课程、知识库和报告数据。",
            status="正常",
            source="后端运行时检查",
            suggestion="如 Dashboard 数据为空，优先创建课程并上传课程资料。",
        ),
        _base_log(
            log_id="settings-safety",
            created_at=now,
            level="SUCCESS",
            category="system",
            module="Settings",
            action="配置脱敏展示",
            summary="系统设置页仅展示模型和知识库配置状态，不返回真实密钥。",
            status="已脱敏",
            source="系统设置兼容日志",
            suggestion="保持 .env 本地保存，不要提交真实 API Key。",
        ),
    ]


def _fallback_logs() -> list[dict[str, Any]]:
    now = datetime.utcnow()
    return [
        _base_log(
            log_id="fallback-qa",
            created_at=now,
            level="INFO",
            category="qa",
            module="TutorChat",
            action="问答",
            summary="暂无真实问答记录，当前展示兼容示例日志。",
            status="演示",
            source="日志中心 fallback",
            suggestion="进入智能答疑页面提交问题后，将自动展示真实问答日志。",
            related_type="qa",
        ),
        _base_log(
            log_id="fallback-kb",
            created_at=now,
            level="WARNING",
            category="knowledge",
            module="KnowledgeBase",
            action="上传",
            summary="暂无知识库文档记录，请上传课程资料以构建真实知识库日志。",
            status="待补充",
            source="日志中心 fallback",
            suggestion="进入知识库页面上传 PDF、Word、PPT、TXT 或 Markdown 资料。",
            related_type="document",
        ),
        _base_log(
            log_id="fallback-agent",
            created_at=now,
            level="INFO",
            category="agent",
            module="AgentWorkflow",
            action="运行工作流",
            summary="暂无 Agent 运行记录，当前展示工作流兼容日志。",
            status="待运行",
            source="日志中心 fallback",
            suggestion="进入 Agent 工作流页面运行一次完整学习流。",
            related_type="agent_run",
        ),
        _base_log(
            log_id="fallback-report",
            created_at=now,
            level="INFO",
            category="report",
            module="ReportCenter",
            action="生成报告",
            summary="暂无报告生成记录，运行学习流或报告生成后将展示真实日志。",
            status="待生成",
            source="日志中心 fallback",
            suggestion="先创建学生画像和学习路径，再生成学习报告。",
            related_type="report",
        ),
    ]


def _collect_logs(db: Session) -> list[dict[str, Any]]:
    course_titles = _course_titles(db)
    rows: list[dict[str, Any]] = _system_logs()

    docs = db.query(CourseDocument).order_by(CourseDocument.id.desc()).limit(80).all()
    for item in docs:
        status = item.parse_status or "unknown"
        level = "SUCCESS" if status == "parsed" else "ERROR" if status == "failed" else "WARNING"
        rows.append(
            _base_log(
                log_id=f"kb-{item.id}",
                created_at=item.created_at,
                level=level,
                category="knowledge",
                module="KnowledgeBase",
                action="上传",
                summary=f"{item.filename} 已写入知识库，解析状态：{status}，切片数：{item.chunk_count}。",
                status=status,
                source="知识库上传记录",
                suggestion="解析失败时请检查文件格式、文件内容和后端解析依赖。",
                course_id=item.course_id,
                course_title=course_titles.get(item.course_id),
                related_id=item.id,
                related_type="document",
                error_message="文档解析失败" if status == "failed" else "",
            )
        )

    questions = db.query(TutorQuestionLog).order_by(TutorQuestionLog.id.desc()).limit(100).all()
    for item in questions:
        rows.append(
            _base_log(
                log_id=f"qa-{item.id}",
                created_at=item.created_at,
                level="SUCCESS",
                category="qa",
                module="TutorChat",
                action="问答",
                summary=_short(item.question, "智能答疑记录"),
                status="已回答",
                source=f"智能答疑页面 / {item.mode}",
                suggestion="可结合 retrieved_context 检查回答引用是否覆盖课程关键资料。",
                course_id=item.course_id,
                course_title=course_titles.get(item.course_id),
                related_id=item.id,
                related_type="qa",
            )
        )

    runs = db.query(AgentRun).order_by(AgentRun.id.desc()).limit(80).all()
    for item in runs:
        output = loads(item.output_json, {}) if item.output_json else {}
        input_data = loads(item.input_json, {}) if item.input_json else {}
        status = item.status or "unknown"
        rows.append(
            _base_log(
                log_id=f"agent-{item.id}",
                created_at=item.created_at,
                level="ERROR" if status == "failed" else "SUCCESS" if status == "success" else "INFO",
                category="agent",
                module="AgentWorkflow",
                action="运行工作流",
                summary=_short(input_data.get("learning_goal") or item.workflow_name, "Agent 工作流运行记录"),
                status=status,
                source="AgentWorkflow 页面",
                suggestion="失败时优先检查课程、学生输入、知识库资料和模型运行模式。",
                course_id=item.course_id,
                course_title=course_titles.get(item.course_id),
                related_id=item.id,
                related_type="agent_run",
                error_message=_short(output.get("error"), "", 180) if status == "failed" else "",
            )
        )

    reports = db.query(LearningReport).order_by(LearningReport.id.desc()).limit(80).all()
    for item in reports:
        rows.append(
            _base_log(
                log_id=f"report-{item.id}",
                created_at=item.created_at,
                level="SUCCESS",
                category="report",
                module="ReportCenter",
                action="生成报告",
                summary=_short(item.report_title, "学习报告生成记录"),
                status="已生成" if item.report_path else "已记录",
                source="报告中心",
                suggestion="可在报告中心预览详情并下载 Word 报告。",
                course_id=item.course_id,
                course_title=course_titles.get(item.course_id),
                related_id=item.id,
                related_type="report",
            )
        )

    real_count = len(rows) - len(_system_logs())
    if real_count == 0:
        rows.extend(_fallback_logs())
    return rows


def _apply_filters(
    logs: list[dict[str, Any]],
    category: str | None,
    level: str | None,
    module: str | None,
    keyword: str | None,
) -> list[dict[str, Any]]:
    keyword_text = (keyword or "").strip().lower()
    return [
        item
        for item in logs
        if (not category or category == "all" or item["category"] == category)
        and (not level or level == "all" or item["level"] == level)
        and (not module or module == "all" or item["module"] == module)
        and (
            not keyword_text
            or keyword_text in item["summary"].lower()
            or keyword_text in item["action"].lower()
            or keyword_text in item["module"].lower()
            or keyword_text in item["course_title"].lower()
        )
    ]


@router.get("")
def list_logs(
    category: str | None = None,
    level: str | None = None,
    module: str | None = None,
    keyword: str | None = None,
    order: str = "desc",
    limit: int = 120,
    db: Session = Depends(get_db),
):
    rows = _apply_filters(_collect_logs(db), category, level, module, keyword)
    reverse = order != "asc"
    rows = sorted(rows, key=lambda item: item["time"], reverse=reverse)
    return rows[: min(max(limit, 1), 200)]


@router.get("/summary")
def logs_summary(db: Session = Depends(get_db)):
    rows = _collect_logs(db)
    today = datetime.utcnow().date()
    return {
        "today_log_count": sum(1 for item in rows if item["time"].date() == today),
        "error_log_count": sum(1 for item in rows if item["level"] == "ERROR"),
        "agent_run_count": db.query(AgentRun).count(),
        "question_count": db.query(TutorQuestionLog).count(),
        "total_count": len(rows),
    }
