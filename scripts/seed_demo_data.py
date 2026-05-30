from __future__ import annotations

import runpy
import sys
from datetime import datetime, timedelta
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
LEGACY_SEED = Path(__file__).with_name("seed-demo-data.py")

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import Base, SessionLocal, engine  # noqa: E402
from app.models import SystemLog  # noqa: E402
from app.services.json_utils import dumps, loads  # noqa: E402


DEMO_SEED = "EduMind competition demo seed v2"


def _created_at(hours: int) -> datetime:
    return datetime.utcnow() - timedelta(hours=hours)


def _ensure_log(db, *, type: str, title: str, content: str, level: str, module: str, status: str, hours: int, duration_ms: int, related_id: str, metadata: dict):
    existing = (
        db.query(SystemLog)
        .filter(SystemLog.type == type, SystemLog.title == title, SystemLog.related_id == related_id)
        .first()
    )
    if existing:
        return False
    db.add(
        SystemLog(
            type=type,
            title=title,
            content=content,
            level=level,
            module=module,
            user="demo_teacher",
            related_id=related_id,
            duration_ms=duration_ms,
            status=status,
            error_message=metadata.get("error_message"),
            metadata_json=dumps({"demo_seed": DEMO_SEED, **metadata}),
            created_at=_created_at(hours),
        )
    )
    return True


def seed_log_management_data() -> dict[str, int]:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    created = 0
    try:
        rows = [
            {
                "type": "qa",
                "title": "智能答疑引用生成",
                "content": "学生围绕 Python 文件读取提问，系统检索课程资料后生成带引用的引导式回答。",
                "level": "SUCCESS",
                "module": "TutorChat",
                "status": "answered",
                "hours": 1,
                "duration_ms": 780,
                "related_id": "demo-qa-001",
                "metadata": {"citation_count": 3, "based_on_material": True},
            },
            {
                "type": "document_upload",
                "title": "课程资料解析入库",
                "content": "Python 函数与模块讲义完成解析，生成知识切片并进入 lightweight RAG fallback。",
                "level": "SUCCESS",
                "module": "KnowledgeBase",
                "status": "indexed",
                "hours": 3,
                "duration_ms": 1450,
                "related_id": "demo-doc-001",
                "metadata": {"chunk_count": 18, "file_type": "pdf"},
            },
            {
                "type": "agent_workflow",
                "title": "Agent 学习闭环运行",
                "content": "classify、retrieve、generate、analyze、report 节点完成一次模拟运行。",
                "level": "SUCCESS",
                "module": "AgentWorkflow",
                "status": "success",
                "hours": 5,
                "duration_ms": 2030,
                "related_id": "demo-agent-001",
                "metadata": {"run_id": "demo-run-001", "langgraph_run_id": None, "node_count": 5},
            },
            {
                "type": "report_generation",
                "title": "学习报告生成完成",
                "content": "报告中心根据学生画像、测评结果、问答引用和 Agent 产物生成阶段学习报告。",
                "level": "SUCCESS",
                "module": "ReportCenter",
                "status": "completed",
                "hours": 8,
                "duration_ms": 1240,
                "related_id": "demo-report-001",
                "metadata": {"quality_score": 86.5, "reference_count": 4},
            },
            {
                "type": "error",
                "title": "知识库命中不足告警",
                "content": "RAG 检索返回片段不足，系统降级使用 demo/fallback 提示并建议补充课程资料。",
                "level": "ERROR",
                "module": "KnowledgeBase",
                "status": "fallback",
                "hours": 10,
                "duration_ms": 320,
                "related_id": "demo-error-001",
                "metadata": {"error_message": "retrieval hit count below threshold", "suggestion": "补充课程资料或降低 TopK 阈值。"},
            },
        ]
        for row in rows:
            created += 1 if _ensure_log(db, **row) else 0
        db.commit()
        return {"created": created, "reused": len(rows) - created}
    finally:
        db.close()


def main() -> None:
    if LEGACY_SEED.exists():
        print("Running existing EduMind business demo seed...")
        runpy.run_path(str(LEGACY_SEED), run_name="__main__")
    stats = seed_log_management_data()
    print("\nLogManagement demo data ready:")
    print(f"- system_logs: created {stats['created']}, reused {stats['reused']}")
    print("- storage: SQLite fallback under backend/storage/eduagent.sqlite3")


if __name__ == "__main__":
    main()
