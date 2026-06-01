from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import agent_workflow, courses, dashboard, demo_status, events, knowledge_base, learning_paths, logs, profiles, quizzes, reports, resources, system_settings, tutor
from app.core.config import settings
from app.db.session import Base, engine
from app.models import *  # noqa: F401,F403
from app.services.llm_service import llm_service


Base.metadata.create_all(bind=engine)

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
app.include_router(profiles.router, prefix=API_PREFIX)
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
app.include_router(dashboard.router, prefix="/api")


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
