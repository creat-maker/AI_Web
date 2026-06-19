from __future__ import annotations

from fastapi import Request

from app.services.demo_profile_chain import normalize_user_id


def get_demo_user_id(request: Request, user_id: str | None = None) -> str:
    header_user_id = request.headers.get("X-Demo-User-Id")
    return normalize_user_id(user_id or header_user_id or "demo-basic")
