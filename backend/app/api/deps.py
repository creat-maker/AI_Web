from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.routers.auth import get_current_user
from app.db.session import get_db
from app.services.demo_profile_chain import normalize_user_id
from app.services.governance_service import current_user_label, write_audit_log


def get_demo_user_id(request: Request, user_id: str | None = None) -> str:
    header_user_id = request.headers.get("X-Demo-User-Id")
    return normalize_user_id(user_id or header_user_id or "demo-basic")


def require_roles(*roles: str) -> Callable[..., dict[str, Any]]:
    allowed = set(roles)

    async def dependency(
        request: Request,
        db: Session = Depends(get_db),
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        role = str(current_user.get("role") or "guest")
        if role in allowed:
            return current_user
        actor_id, actor_name, actor_role = current_user_label(current_user)
        write_audit_log(
            db,
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            action="permission_denied",
            target_type="api",
            target_id=request.url.path,
            status="denied",
            detail=f"需要角色：{', '.join(sorted(allowed))}；当前角色：{role}",
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=403, detail="当前角色无权访问该资源")

    return dependency
