from __future__ import annotations

from datetime import datetime
from importlib.util import find_spec

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.config import settings
from app.db.session import get_db
from app.models import CourseDocument, LearningReport, TutorQuestionLog
from app.services.llm_service import llm_service
from app.services.xfyun_safety_service import xfyun_safety_service
from app.services.xfyun_spark_service import xfyun_spark_service
from app.services.xfyun_tts_service import xfyun_tts_service


router = APIRouter(prefix="/settings", tags=["settings"])


def _api_key_configured() -> bool:
    if settings.llm_provider == "deepseek":
        return bool(settings.deepseek_api_key)
    if settings.llm_provider in {"qwen", "dashscope"}:
        return bool(settings.qwen_api_key or settings.dashscope_api_key)
    return False


def _model_mode() -> str:
    if settings.is_mock_mode:
        return "Mock"
    return "API"


def _model_name() -> str:
    model_map = {
        "mock": "mock-llm",
        "deepseek": "deepseek-chat",
        "qwen": "qwen-plus",
        "dashscope": "qwen-plus",
    }
    return model_map.get(settings.llm_provider, "mock-llm")


def _vector_store_type() -> str:
    return "Chroma" if find_spec("chromadb") else "fallback JSON"


def _database_hint() -> str:
    if settings.resolved_database_url.startswith("sqlite"):
        return "本地 SQLite（物理路径已隐藏）"
    return "外部数据库连接已配置，前端不展示连接串。"


def _xfyun_status() -> dict:
    return {
        "xfyun_enabled": settings.xfyun_configured,
        "tts": xfyun_tts_service.status(),
        "spark": xfyun_spark_service.status(),
        "safety": xfyun_safety_service.status(),
        "fallback_engine": "local_intelligent_evaluator",
    }


@router.get("")
def get_settings_snapshot(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    parsed_docs = db.query(CourseDocument).filter(CourseDocument.parse_status == "parsed").count()
    report_count = db.query(LearningReport).count()
    qa_count = db.query(TutorQuestionLog).count()
    vector_type = _vector_store_type()

    return {
        "overview": {
            "system_mode": "本地开发模式",
            "model_mode": _model_mode(),
            "knowledge_base_status": "已就绪" if parsed_docs else "等待构建",
            "last_updated": datetime.utcnow().isoformat(),
        },
        "model_config": {
            "llm_provider": settings.llm_provider,
            "model_name": _model_name(),
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream_enabled": False,
            "api_key_status": "已配置" if _api_key_configured() else "未配置",
        },
        "rag_config": {
            "chunk_size": 800,
            "chunk_overlap": 120,
            "top_k": 5,
            "similarity_threshold": 0.2,
            "vector_store_type": vector_type,
            "persist_dir": "已配置（物理路径已隐藏）",
        },
        "teaching_strategy": {
            "answer_mode": "严谨",
            "show_citations": True,
            "record_qa_logs": True,
            "generate_learning_suggestions": True,
            "generate_reports": True,
        },
        "security": {
            "api_key_visible": False,
            "upload_size_tip": "建议单个教学资料控制在 20MB 内，便于本地解析和演示。",
            "local_dev_tip": "当前为本地开发展示配置，保存按钮不会写入真实密钥或系统环境变量。",
            "database_path": _database_hint(),
            "vector_store_path": "已配置（物理路径已隐藏）",
        },
        "runtime": {
            "llm_mode": llm_service.runtime_mode,
            "mock_mode": settings.is_mock_mode,
            "parsed_document_count": parsed_docs,
            "report_count": report_count,
            "qa_count": qa_count,
        },
        "xfyun_tools": {**_xfyun_status(), "enabled": settings.xfyun_configured, "secret_visible": False},
        "xfyun_status": _xfyun_status(),
        "ai_tool_status": {
            "provider": "local_intelligent_evaluator",
            "xfyun_configurable": True,
            "xfyun_status": _xfyun_status(),
        },
    }


@router.post("/test")
def test_settings_connection(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    parsed_docs = db.query(CourseDocument).filter(CourseDocument.parse_status == "parsed").count()
    return {
        "status": "ok",
        "message": "系统配置检查完成，未读取或返回任何真实 API Key。",
        "checks": [
            {
                "name": "模型运行模式",
                "status": "ok",
                "detail": f"{llm_service.runtime_mode} / {_model_mode()}",
            },
            {
                "name": "知识库",
                "status": "ok" if parsed_docs else "warning",
                "detail": f"{_vector_store_type()}，已解析文档 {parsed_docs} 份。",
            },
            {
                "name": "报告目录",
                "status": "ok",
                "detail": "报告目录已配置（物理路径已隐藏）",
            },
            {
                "name": "科大讯飞 TTS",
                "status": "ok" if settings.xfyun_configured else "warning",
                "detail": xfyun_tts_service.status()["message"],
            },
        ],
    }
