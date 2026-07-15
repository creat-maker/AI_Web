from __future__ import annotations

from app.core.config import settings
from app.services.xfyun_tts_service import NOT_CONFIGURED_MESSAGE


class XfyunSafetyService:
    provider = "xfyun_safety"

    def is_configured(self) -> bool:
        return settings.xfyun_configured and bool(settings.xfyun_safety_url)

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
            "endpoint": settings.xfyun_safety_url,
            "message": "内容安全扩展服务已具备配置条件，可接入科大讯飞审核能力。",
        }

    def check(self, content: str) -> dict:
        if not self.is_configured():
            return {
                "status": "not_configured",
                "provider": self.provider,
                "message": NOT_CONFIGURED_MESSAGE,
            }
        return {
            "status": "ready",
            "provider": self.provider,
            "endpoint": settings.xfyun_safety_url,
            "message": "当前环境已配置讯飞参数，生产环境可在此处接入真实内容安全审核请求。",
            "checked_length": len(content or ""),
        }


xfyun_safety_service = XfyunSafetyService()
