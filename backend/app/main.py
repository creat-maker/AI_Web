from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import agent_workflow, ai_tutor, auth, competition, content_review, courses, dashboard, decision_center, demo_capabilities, demo_status, events, governance, knowledge_base, learning_paths, logs, profile_dialog, profiles, quizzes, rag, reports, resources, student_profile, system_settings, tutor, user_profile_ws, xfyun
from app.api.routers import admin_reports, admin_users, student_courses
from app.core.config import settings
from app.db.session import Base, engine
from app.models import *  # noqa: F401,F403
from app.services.llm_service import llm_service


Base.metadata.create_all(bind=engine)

# 为已存在的表添加新列（SQLite 不支持 ALTER ADD COLUMN 通过 metadata）
with engine.connect() as conn:
    from sqlalchemy import inspect
    insp = inspect(engine)
    table_columns = {
        "student_profiles": {
            "dimension_scores": "TEXT",
            "evidence_items": "TEXT",
            "cognitive_state": "TEXT",
            "profile_history": "TEXT",
            "risk_level": "VARCHAR(50)",
        },
        "learning_paths": {
            "adjustment_log": "TEXT",
            "current_difficulty": "VARCHAR(50)",
            "inserted_tasks": "TEXT",
            "teacher_arbitration_required": "BOOLEAN DEFAULT 0 NOT NULL",
        },
        "generated_resources": {
            "recommend_reason": "TEXT",
            "file_path": "VARCHAR(500)",
            "resource_url": "VARCHAR(500)",
            "preview_type": "VARCHAR(50)",
            "rating": "FLOAT",
            "generation_status": "VARCHAR(50) DEFAULT 'generated' NOT NULL",
            "audit_status": "VARCHAR(50) DEFAULT 'pending_review' NOT NULL",
        },
        "audit_logs": {
            "retry_count": "INTEGER DEFAULT 0 NOT NULL",
            "xfyun_result": "TEXT",
            "rule_engine_result": "TEXT",
            "risk_level": "VARCHAR(50)",
            "arbitration_status": "VARCHAR(50)",
            "decision_request_id": "VARCHAR(128)",
            "arbitration_item_id": "VARCHAR(200)",
        },
        "agent_runs": {
            "run_id": "VARCHAR(100)",
            "current_node": "VARCHAR(100)",
            "state": "TEXT",
            "messages": "TEXT",
            "audit_result": "TEXT",
            "retry_count": "INTEGER DEFAULT 0 NOT NULL",
            "teacher_arbitration_result": "TEXT",
            "started_at": "DATETIME",
            "finished_at": "DATETIME",
        },
    }
    tables = set(insp.get_table_names())
    for table_name, columns in table_columns.items():
        if table_name not in tables:
            continue
        existing_cols = {col["name"] for col in insp.get_columns(table_name)}
        for column_name, column_type in columns.items():
            if column_name not in existing_cols:
                conn.execute(
                    __import__("sqlalchemy").text(
                        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                    )
                )
    conn.commit()

    # Q020: nullable columns preserve historical audit rows; unique indexes make
    # duplicate requests and concurrent decisions for the same arbitration item
    # fail atomically without deleting or rewriting existing evidence.
    if "audit_logs" in tables:
        conn.execute(
            __import__("sqlalchemy").text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_audit_logs_decision_request_id "
                "ON audit_logs (decision_request_id)"
            )
        )
        conn.execute(
            __import__("sqlalchemy").text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_audit_logs_arbitration_item_id "
                "ON audit_logs (arbitration_item_id)"
            )
        )
        conn.commit()

app = FastAPI(
    title="EduMind API",
    description="面向三端教育智能体演示的个性化学习资源生成、学习画像、路径规划、报告生成与平台治理服务。",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(courses.router, prefix=API_PREFIX)
app.include_router(student_courses.router, prefix=API_PREFIX)
app.include_router(knowledge_base.router, prefix=API_PREFIX)
app.include_router(rag.router, prefix=API_PREFIX)
app.include_router(content_review.router, prefix=API_PREFIX)
app.include_router(profiles.router, prefix=API_PREFIX)
app.include_router(profile_dialog.router, prefix=API_PREFIX)
app.include_router(student_profile.router, prefix=API_PREFIX)
app.include_router(learning_paths.router, prefix=API_PREFIX)
app.include_router(resources.router, prefix=API_PREFIX)
app.include_router(tutor.router, prefix=API_PREFIX)
app.include_router(ai_tutor.router, prefix=API_PREFIX)
app.include_router(quizzes.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(admin_reports.router, prefix=API_PREFIX)
app.include_router(admin_users.router, prefix=API_PREFIX)
app.include_router(agent_workflow.router, prefix=API_PREFIX)
app.include_router(system_settings.router, prefix=API_PREFIX)
app.include_router(xfyun.router, prefix=API_PREFIX)
app.include_router(governance.router, prefix=API_PREFIX)
app.include_router(logs.router, prefix=API_PREFIX)
app.include_router(events.router, prefix=API_PREFIX)
app.include_router(demo_status.router, prefix=API_PREFIX)
app.include_router(demo_capabilities.router, prefix=API_PREFIX)
app.include_router(competition.router, prefix=API_PREFIX)
app.include_router(decision_center.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix="/api")
app.include_router(user_profile_ws.router)

@app.get("/api/v1/runtime")
def runtime():
    return {
        "llm_mode": llm_service.runtime_mode,
        "mock_mode": settings.is_mock_mode,
        "chroma_persist_dir": str(settings.path_from_root(settings.chroma_persist_dir)),
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_mode": llm_service.runtime_mode,
        "services": {
            "database": "ok",
            "rag": "ok",
            "dkvmn": "ok",
            "arbitration": "ok",
            "report": "ok",
            "version": app.version,
        },
    }


@app.get("/api/v1/health")
def api_health():
    return health()
