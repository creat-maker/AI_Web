from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

JWT_SECRET = settings.jwt_secret
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 86400  # 24 hours

DEMO_USERS = {
    "demo_student": {"password": "123456", "role": "student", "name": "张三"},
    "demo_teacher": {"password": "123456", "role": "teacher", "name": "王老师"},
    "demo_admin": {"password": "123456", "role": "admin", "name": "管理员"},
}


class LoginPayload(BaseModel):
    username: str
    password: str


def _sign_jwt(payload: dict[str, Any]) -> str:
    header = json.dumps({"alg": JWT_ALGORITHM, "typ": "JWT"}, separators=(",", ":"))
    payload_json = json.dumps(payload, separators=(",", ":"))
    header_b64 = _b64url_encode(header.encode("utf-8"))
    payload_b64 = _b64url_encode(payload_json.encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(JWT_SECRET.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def _b64url_encode(data: bytes) -> str:
    import base64

    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    import base64

    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


def verify_jwt(token: str) -> dict[str, Any] | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
        actual_sig = _b64url_decode(signature_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload_json = _b64url_decode(payload_b64).decode("utf-8")
        payload = json.loads(payload_json)
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


async def get_current_user(request: Request) -> dict[str, Any]:
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        payload = verify_jwt(token)
        if payload:
            return payload
    # Demo mode: allow without token
    return {"role": "guest", "name": "访客", "username": "anonymous"}


@router.post("/login")
def login(payload: LoginPayload):
    user = DEMO_USERS.get(payload.username)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    now = int(time.time())
    token_payload = {
        "username": payload.username,
        "role": user["role"],
        "name": user["name"],
        "iat": now,
        "exp": now + JWT_EXPIRE_SECONDS,
    }
    token = _sign_jwt(token_payload)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRE_SECONDS,
        "role": user["role"],
        "name": user["name"],
    }


@router.get("/me")
def me(current_user: dict[str, Any] = Depends(get_current_user)):
    return current_user


@router.get("/demo-accounts")
def demo_accounts():
    return [
        {"username": k, "role": v["role"], "name": v["name"], "password": v["password"]}
        for k, v in DEMO_USERS.items()
    ]
