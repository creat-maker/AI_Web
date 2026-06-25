from __future__ import annotations

from app.core.config import settings
from app.services.xfyun_tts_service import NOT_CONFIGURED_MESSAGE


class XfyunSparkService:
    provider = "xfyun_spark"

    def is_configured(self) -> bool:
        return settings.xfyun_configured and bool(settings.xfyun_spark_url)

    def status(self) -> dict:
        if not self.is_configured():
            return {
                "enabled": False,
                "status": "not_configured",
                "provider": self.provider,
                "message": NOT_CONFIGURED_MESSAGE,
            }
        return {
            "enabled": True,
            "status": "configured",
            "provider": self.provider,
            "message": "星火大模型接入参数已配置，可作为可插拔 AI 服务用于画像、规划和内容生成。",
        }


xfyun_spark_service = XfyunSparkService()
