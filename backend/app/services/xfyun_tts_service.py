from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import quote, urlencode, urlparse

from app.core.config import settings


NOT_CONFIGURED_MESSAGE = "当前未配置科大讯飞密钥，系统使用本地智能评测引擎保持稳定运行"


class XfyunTTSService:
    """科大讯飞 TTS 接入封装，未配置或缺少运行依赖时稳定降级。"""

    provider = "xfyun_tts"

    def is_configured(self) -> bool:
        return settings.xfyun_configured

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
            "message": "科大讯飞 TTS 已配置，可用于生产环境语音合成接入。",
        }

    def build_signed_url(self, url: str | None = None) -> str:
        target = url or settings.xfyun_tts_url
        parsed = urlparse(target)
        host = parsed.netloc
        path = parsed.path or "/v2/tts"
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

    def synthesize(self, text: str, voice_name: str = "xiaoyan") -> dict:
        text = (text or "").strip()
        if not text:
            return {
                "status": "failed",
                "provider": self.provider,
                "message": "待合成文本不能为空。",
            }
        if not self.is_configured():
            return {
                "status": "not_configured",
                "audio_path": None,
                "provider": self.provider,
                "enabled": False,
                "message": NOT_CONFIGURED_MESSAGE,
                "text_resource": text,
            }

        try:
            import websocket  # type: ignore
        except Exception:
            return {
                "status": "failed",
                "audio_path": None,
                "provider": self.provider,
                "message": "当前环境未安装 websocket-client，已保留 TTS 签名接入路径但未发起真实合成。",
                "signed_url_ready": True,
            }

        audio_chunks: list[bytes] = []
        payload = {
            "common": {"app_id": settings.xfyun_app_id},
            "business": {"aue": "lame", "auf": "audio/L16;rate=16000", "vcn": voice_name, "tte": "utf8"},
            "data": {
                "status": 2,
                "text": base64.b64encode(text.encode("utf-8")).decode("utf-8"),
            },
        }

        try:
            ws = websocket.create_connection(self.build_signed_url(), timeout=8)
            ws.send(json.dumps(payload, ensure_ascii=False))
            while True:
                response = json.loads(ws.recv())
                if response.get("code") != 0:
                    ws.close()
                    return {
                        "status": "failed",
                        "audio_path": None,
                        "provider": self.provider,
                        "message": response.get("message") or "科大讯飞 TTS 返回失败。",
                    }
                audio = response.get("data", {}).get("audio")
                if audio:
                    audio_chunks.append(base64.b64decode(audio))
                if response.get("data", {}).get("status") == 2:
                    break
            ws.close()
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "failed",
                "audio_path": None,
                "provider": self.provider,
                "message": f"科大讯飞 TTS 调用失败：{exc}",
            }

        output_dir = settings.path_from_root(settings.upload_dir) / "tts"
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"xfyun_tts_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.mp3"
        output_path = output_dir / quote(filename)
        Path(output_path).write_bytes(b"".join(audio_chunks))
        return {
            "status": "success",
            "audio_path": str(output_path),
            "provider": self.provider,
            "message": "科大讯飞 TTS 合成完成。",
        }


xfyun_tts_service = XfyunTTSService()
