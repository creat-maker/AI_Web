from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

JWT_SECRET = settings.jwt_secret
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 86400

DEMO_USERS: dict[str, dict[str, str]] = {
    "student": {"password": "123456", "role": "student", "name": "李明", "id": "student_001", "student_id": "1"},
    "teacher": {"password": "123456", "role": "teacher", "name": "王老师", "id": "teacher_001"},
    "admin": {"password": "123456", "role": "admin", "name": "管理员", "id": "admin_001"},
    "demo_student": {"password": "123456", "role": "student", "name": "李明", "id": "student_001", "student_id": "1"},
    "demo_teacher": {"password": "123456", "role": "teacher", "name": "王老师", "id": "teacher_001"},
    "demo_admin": {"password": "123456", "role": "admin", "name": "管理员", "id": "admin_001"},
}

ROLE_REDIRECTS = {
    "student": "/student",
    "teacher": "/teacher",
    "admin": "/dashboard",
}


class LoginPayload(BaseModel):
    username: str
    password: str


def _b64url_encode(data: bytes) -> str:
    import base64

    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    import base64

    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


def _sign_jwt(payload: dict[str, Any]) -> str:
    header = json.dumps({"alg": JWT_ALGORITHM, "typ": "JWT"}, separators=(",", ":"))
    payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    header_b64 = _b64url_encode(header.encode("utf-8"))
    payload_b64 = _b64url_encode(payload_json.encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(JWT_SECRET.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


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
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


async def get_current_user(request: Request) -> dict[str, Any]:
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        payload = verify_jwt(auth[7:])
        if payload:
            return payload
    return {"role": "guest", "name": "访客", "username": "anonymous"}


@router.post("/login")
def login(payload: LoginPayload):
    username = payload.username.strip()
    user = DEMO_USERS.get(username)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    now = int(time.time())
    role = user["role"]
    token_payload = {
        "username": username,
        "role": role,
        "name": user["name"],
        "display_name": user["name"],
        "user_id": user["id"],
        "student_id": user.get("student_id"),
        "iat": now,
        "exp": now + JWT_EXPIRE_SECONDS,
    }
    token = _sign_jwt(token_payload)
    response_user = {
        "id": user["id"],
        "username": username,
        "display_name": user["name"],
        "name": user["name"],
        "role": role,
    }
    if user.get("student_id"):
        response_user["student_id"] = user["student_id"]

    return {
        "access_token": token,
        "token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRE_SECONDS,
        "user": response_user,
        "role": role,
        "name": user["name"],
        "display_name": user["name"],
        "redirect": ROLE_REDIRECTS[role],
    }


@router.get("/me")
def me(current_user: dict[str, Any] = Depends(get_current_user)):
    return current_user


@router.get("/demo-accounts")
def demo_accounts():
    return [
        {"username": key, "role": value["role"], "name": value["name"], "password": value["password"]}
        for key, value in DEMO_USERS.items()
    ]
