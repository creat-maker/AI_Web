from fastapi import APIRouter

from app.api.routers.agent import router as agent_router
from app.api.routers.attachments import router as attachments_router
from app.api.routers.avatar import router as avatar_router
from app.api.routers.config import router as config_router
from app.api.routers.digital_human import router as digital_human_router
from app.api.routers.exam_analysis import router as exam_analysis_router
from app.api.routers.export import router as export_router
from app.api.routers.generator import router as generator_router
from app.api.routers.projects import router as projects_router

__all__ = [
    "agent_router",
    "attachments_router",
    "avatar_router",
    "config_router",
    "digital_human_router",
    "exam_analysis_router",
    "export_router",
    "generator_router",
    "projects_router",
]
