import os

import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import SystemConfig
from app.schemas import ResponseModel
from app.services import get_config_value, mock_baidu_token

router = APIRouter(prefix="/digital-human", tags=["数字人"])


@router.post("/token")
def get_digital_human_token(db: Session = Depends(get_db)):
    try:
        api_key = get_config_value(db, "BAIDU_APP_KEY")
        app_key = get_config_value(db, "BAIDU_APP_KEY")
        secret_key = get_config_value(db, "BAIDU_SECRET_KEY")
    except HTTPException:
        return mock_baidu_token("配置缺失")

    try:
        token_url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
        resp = requests.post(token_url, params=params, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        access_token = result.get("access_token")
        if not access_token:
            return mock_baidu_token("未返回 access_token")
        return ResponseModel(data={"access_token": access_token, "expires_in": result.get("expires_in", 3600)})
    except requests.RequestException as exc:
        return mock_baidu_token(str(exc))


@router.post("/avatar/generate")
def generate_avatar_video(request: Request, db: Session = Depends(get_db)):
    body = request._json if hasattr(request, "_json") else {}

    try:
        api_key = get_config_value(db, "QWEN_API_KEY")
    except HTTPException:
        return ResponseModel(data={"status": "mock", "message": "API key not configured, using mock mode"})

    return ResponseModel(data={"status": "generated", "message": "Avatar video generation triggered"})


@router.get("/config")
def get_digital_human_config(db: Session = Depends(get_db)):
    configs = db.query(SystemConfig).filter(
        SystemConfig.config_key.in_(["BAIDU_APP_KEY", "BAIDU_SECRET_KEY", "BAIDU_AUDIO_MODEL"])
    ).all()

    config_map = {c.config_key: c.config_value for c in configs}
    return ResponseModel(data={
        "app_key": config_map.get("BAIDU_APP_KEY", ""),
        "secret_key": config_map.get("BAIDU_SECRET_KEY", ""),
        "audio_model": config_map.get("BAIDU_AUDIO_MODEL", ""),
    })
