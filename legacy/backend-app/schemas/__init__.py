from app.schemas.agent import LessonGenerateRequest, LessonGenerateResponse
from app.schemas.avatar import (
    AIGenerateRequest,
    AvatarChatRequest,
    QuizGenerateRequest,
    QuizItem,
)
from app.schemas.common import ApiResponse
from app.schemas.config import ChatHistoryOut, ConfigCreate, ConfigOut, ConfigUpdate
from app.schemas.projects import (
    AttachmentOut,
    GeneratedContentEntry,
    GeneratedContentOut,
    ProjectCreate,
    ProjectDetail,
    ProjectOut,
    ProjectUpdate,
    ResponseModel,
    StagedAttachmentOut,
)

__all__ = [
    "ApiResponse",
    "LessonGenerateRequest",
    "LessonGenerateResponse",
    "AvatarChatRequest",
    "AIGenerateRequest",
    "QuizItem",
    "QuizGenerateRequest",
    "ConfigCreate",
    "ConfigUpdate",
    "ConfigOut",
    "ChatHistoryOut",
    "ResponseModel",
    "AttachmentOut",
    "StagedAttachmentOut",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectOut",
    "ProjectDetail",
    "GeneratedContentEntry",
    "GeneratedContentOut",
]
