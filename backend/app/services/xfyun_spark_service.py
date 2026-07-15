from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import datetime, timezone
from email.utils import format_datetime
from urllib.parse import urlencode, urlparse

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
            "endpoint": settings.xfyun_spark_url,
            "message": "星火大模型接入参数已配置，可作为可插拔 AI 服务用于画像、规划和内容生成。",
        }

    def build_signed_url(self, url: str | None = None) -> str:
        target = url or settings.xfyun_spark_url
        parsed = urlparse(target)
        host = parsed.netloc
        path = parsed.path or "/v3.5/chat"
        date = format_datetime(datetime.now(timezone.utc), usegmt=True)
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        digest = hmac.new(
            (settings.xfyun_api_secret or "").encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature = base64.b64encode(digest).decode("utf-8")
        authorization_origin = (
            f'api_key="{settings.xfyun_api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")
        query = urlencode({"authorization": authorization, "date": date, "host": host})
        return f"{parsed.scheme}://{host}{path}?{query}"


xfyun_spark_service = XfyunSparkService()
