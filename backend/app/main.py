from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import agent_workflow, competition, content_review, courses, dashboard, demo_status, events, knowledge_base, learning_paths, logs, profile_dialog, profiles, quizzes, rag, reports, resources, system_settings, tutor, user_profile_ws
from app.core.config import settings
from app.db.session import Base, engine
from app.models import *  # noqa: F401,F403
from app.services.llm_service import llm_service


Base.metadata.create_all(bind=engine)

# 为已存在的表添加新列（SQLite 不支持 ALTER ADD COLUMN 通过 metadata）
with engine.connect() as conn:
    from sqlalchemy import inspect
    insp = inspect(engine)
    if "generated_resources" in insp.get_table_names():
        existing_cols = {col["name"] for col in insp.get_columns("generated_resources")}
        if "recommend_reason" not in existing_cols:
            conn.execute(
                __import__("sqlalchemy").text(
                    "ALTER TABLE generated_resources ADD COLUMN recommend_reason TEXT"
                )
            )
    if "learning_paths" in insp.get_table_names():
        existing_cols = {col["name"] for col in insp.get_columns("learning_paths")}
        if "adjustment_log" not in existing_cols:
            conn.execute(
                __import__("sqlalchemy").text(
                    "ALTER TABLE learning_paths ADD COLUMN adjustment_log TEXT"
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
app.include_router(courses.router, prefix=API_PREFIX)
app.include_router(knowledge_base.router, prefix=API_PREFIX)
app.include_router(rag.router, prefix=API_PREFIX)
app.include_router(content_review.router, prefix=API_PREFIX)
app.include_router(profiles.router, prefix=API_PREFIX)
app.include_router(profile_dialog.router, prefix=API_PREFIX)
app.include_router(learning_paths.router, prefix=API_PREFIX)
app.include_router(resources.router, prefix=API_PREFIX)
app.include_router(tutor.router, prefix=API_PREFIX)
app.include_router(quizzes.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(agent_workflow.router, prefix=API_PREFIX)
app.include_router(system_settings.router, prefix=API_PREFIX)
app.include_router(logs.router, prefix=API_PREFIX)
app.include_router(events.router, prefix=API_PREFIX)
app.include_router(demo_status.router, prefix=API_PREFIX)
app.include_router(competition.router, prefix=API_PREFIX)
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
    return {"status": "ok", "llm_mode": llm_service.runtime_mode}
