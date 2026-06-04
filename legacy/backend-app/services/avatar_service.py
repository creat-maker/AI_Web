import logging
import os
from typing import Optional

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import SystemConfig
from app.schemas import ResponseModel

logger = logging.getLogger("avatar")

BAIDU_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
QWEN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
ALLOW_MOCK_BAIDU_TOKEN = os.getenv("PACER_ALLOW_MOCK_BAIDU_TOKEN", "true").lower() != "false"


def get_config_value(db: Session, key: str) -> str:
    config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    if not config or not config.config_value:
        raise HTTPException(status_code=500, detail=f"系统配置缺失: {key}，请先在 /api/config 中配置")
    return config.config_value


def call_qwen(api_key: str, messages: list, temperature: float = 0.7, response_format: Optional[dict] = None) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": "qwen-turbo", "messages": messages, "temperature": temperature}
    if response_format:
        payload["response_format"] = response_format

    resp = requests.post(QWEN_API_URL, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"千问接口异常: HTTP {resp.status_code} - {resp.text}")

    result = resp.json()
    choices = result.get("choices")
    if not choices:
        raise HTTPException(status_code=502, detail=f"千问返回数据异常: {result}")

    return choices[0]["message"]["content"]


def mock_baidu_token(reason: str) -> ResponseModel:
    logger.warning("百度数字人 Token 鉴权失败，回退到本地 mock token: %s", reason)
    return ResponseModel(data={
        "access_token": "mock-local-baidu-token",
        "expires_in": 86400,
        "mock": True,
    })
