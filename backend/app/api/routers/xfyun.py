from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter

from app.services.xfyun_safety_service import xfyun_safety_service
from app.services.xfyun_spark_service import xfyun_spark_service
from app.services.xfyun_tts_service import xfyun_tts_service


router = APIRouter(prefix="/xfyun", tags=["xfyun"])


class TTSPayload(BaseModel):
    text: str
    voice_name: str = "xiaoyan"


@router.get("/status")
def status():
    return {
        "tts": xfyun_tts_service.status(),
        "spark": xfyun_spark_service.status(),
        "safety": xfyun_safety_service.status(),
    }


@router.post("/tts")
def synthesize(payload: TTSPayload):
    return xfyun_tts_service.synthesize(payload.text, payload.voice_name)
