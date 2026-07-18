from __future__ import annotations

import json
import shutil
import secrets
from copy import deepcopy
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.config import settings
from app.db.session import get_db
from app.services.governance_service import current_user_label, write_audit_log

router = APIRouter(prefix="/admin", tags=["admin-users"])

STATE_PATH = settings.path_from_root("backend/storage/admin_users_state.json")

DEFAULT_USERS = [
    {"id": 1, "name": "李明", "account": "student", "role": "学生", "org": "计科大三 1 班", "status": "启用", "last_login": "06-24 09:20"},
    {"id": 2, "name": "王老师", "account": "teacher", "role": "教师", "org": "计算机科学与技术学院", "status": "启用", "last_login": "06-24 08:45"},
    {"id": 3, "name": "陈助教", "account": "assistant01", "role": "助教", "org": "Python 课程组", "status": "启用", "last_login": "06-23 18:10"},
    {"id": 4, "name": "管理员", "account": "admin", "role": "管理员", "org": "平台治理中心", "status": "启用", "last_login": "06-23 15:42"},
    {"id": 5, "name": "周同学", "account": "student02", "role": "学生", "org": "计科大三 2 班", "status": "禁用", "last_login": "06-20 10:16"},
]

DEFAULT_ROLES = {
    "学生": ["学习总览", "我的课程", "学习资源", "智能答疑", "学习报告"],
    "教师": ["班级概览", "课程管理", "资源生成", "报告中心", "学生画像"],
    "助教": ["资源审核", "答疑协助", "作业批改", "班级统计"],
    "管理员": ["平台总览", "用户角色", "资源治理", "报告审核", "日志管理", "系统状态"],
}

ROLE_LABELS = {
    "student": "学生",
    "teacher": "教师",
    "assistant": "助教",
    "admin": "管理员",
}
ROLE_ALIASES = {**{key: key for key in ROLE_LABELS}, **{value: key for key, value in ROLE_LABELS.items()}}
VALID_STATUSES = {"启用", "禁用"}
VALID_PERMISSIONS = {permission for permissions in DEFAULT_ROLES.values() for permission in permissions}


class StatusPayload(BaseModel):
    status: str


class RolePayload(BaseModel):
    role: str


class PermissionPayload(BaseModel):
    permissions: list[str]


def _load() -> dict[str, Any]:
    if STATE_PATH.exists():
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if not isinstance(data.get("users"), list) or not isinstance(data.get("roles"), dict):
            raise HTTPException(status_code=500, detail="管理员状态文件结构无效")
        return data
    return {"users": deepcopy(DEFAULT_USERS), "roles": deepcopy(DEFAULT_ROLES)}


def _save(data: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    backup_path = Path(f"{STATE_PATH}.bak")
    temp_path = Path(f"{STATE_PATH}.tmp")
    if STATE_PATH.exists():
        shutil.copy2(STATE_PATH, backup_path)
    try:
        temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(STATE_PATH)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _normalize_role(value: str) -> str | None:
    return ROLE_ALIASES.get(str(value or "").strip())


def _serialize_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": user.get("id"),
        "name": user.get("name"),
        "account": user.get("account"),
        "role": _normalize_role(str(user.get("role") or "")) or "unknown",
        "org": user.get("org"),
        "status": user.get("status"),
        "last_login": user.get("last_login"),
    }


def _find_user(data: dict[str, Any], user_id: int) -> dict[str, Any]:
    user = next((item for item in data["users"] if item.get("id") == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


def _enabled_admin_count(data: dict[str, Any]) -> int:
    return sum(
        1
        for user in data["users"]
        if _normalize_role(str(user.get("role") or "")) == "admin" and user.get("status") == "启用"
    )


def _protect_last_enabled_admin(data: dict[str, Any], user: dict[str, Any], *, status: str | None = None, role: str | None = None) -> None:
    is_enabled_admin = _normalize_role(str(user.get("role") or "")) == "admin" and user.get("status") == "启用"
    removes_admin = status == "禁用" or (role is not None and role != "admin")
    if is_enabled_admin and removes_admin and _enabled_admin_count(data) <= 1:
        raise HTTPException(status_code=409, detail="不能禁用或降级最后一个启用管理员")


def _audit(
    db: Session,
    current_user: dict[str, Any],
    *,
    action: str,
    target_type: str,
    target_id: str | int,
    detail: str,
) -> None:
    actor_id, actor_name, actor_role = current_user_label(current_user)
    write_audit_log(
        db,
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
    )


@router.get("/users")
def list_users(current_user: dict[str, Any] = Depends(require_admin)):
    data = _load()
    return [_serialize_user(user) for user in data["users"]]


@router.patch("/users/{user_id}/status")
def update_status(
    user_id: int,
    payload: StatusPayload,
    current_user: dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="用户状态仅允许启用或禁用")
    data = _load()
    user = _find_user(data, user_id)
    _protect_last_enabled_admin(data, user, status=payload.status)
    previous = user.get("status")
    user["status"] = payload.status
    _save(data)
    _audit(
        db,
        current_user,
        action="admin_user_status_updated",
        target_type="admin_user",
        target_id=user_id,
        detail=f"用户状态由 {previous} 更新为 {payload.status}",
    )
    return _serialize_user(user)


@router.patch("/users/{user_id}/role")
def update_role(
    user_id: int,
    payload: RolePayload,
    current_user: dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db),
):
    role = _normalize_role(payload.role)
    if not role:
        raise HTTPException(status_code=422, detail="用户角色不在允许范围内")
    data = _load()
    user = _find_user(data, user_id)
    _protect_last_enabled_admin(data, user, role=role)
    previous = _normalize_role(str(user.get("role") or "")) or "unknown"
    user["role"] = role
    _save(data)
    _audit(
        db,
        current_user,
        action="admin_user_role_updated",
        target_type="admin_user",
        target_id=user_id,
        detail=f"用户角色由 {previous} 更新为 {role}",
    )
    return _serialize_user(user)


@router.post("/users/{user_id}/reset-password")
def reset_password(
    user_id: int,
    current_user: dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db),
):
    data = _load()
    _find_user(data, user_id)
    password = f"EM-{secrets.token_hex(3).upper()}"
    _audit(
        db,
        current_user,
        action="admin_password_reset",
        target_type="admin_user",
        target_id=user_id,
        detail="已生成一次性临时密码；临时密码值未写入审计日志。",
    )
    return {"user_id": user_id, "temporary_password": password, "message": "已生成一次性临时密码，请通过线下安全渠道发送给用户。"}


@router.get("/roles")
def list_roles(current_user: dict[str, Any] = Depends(require_admin)):
    data = _load()
    counts = {
        role: sum(1 for user in data["users"] if _normalize_role(str(user.get("role") or "")) == role)
        for role in ROLE_LABELS
    }
    rows = []
    for role, label in ROLE_LABELS.items():
        permissions = data["roles"].get(label, data["roles"].get(role, []))
        rows.append({"role": role, "label": label, "count": counts[role], "permissions": permissions})
    return rows


@router.patch("/roles/{role}/permissions")
def update_role_permissions(
    role: str,
    payload: PermissionPayload,
    current_user: dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db),
):
    normalized_role = _normalize_role(role)
    if not normalized_role:
        raise HTTPException(status_code=404, detail="角色不存在")
    invalid = sorted(set(payload.permissions) - VALID_PERMISSIONS)
    if invalid:
        raise HTTPException(status_code=422, detail="权限项不在允许范围内")
    data = _load()
    storage_key = ROLE_LABELS[normalized_role]
    data["roles"][storage_key] = list(dict.fromkeys(payload.permissions))
    _save(data)
    _audit(
        db,
        current_user,
        action="admin_role_permissions_updated",
        target_type="admin_role",
        target_id=normalized_role,
        detail=f"角色权限数量更新为 {len(payload.permissions)}",
    )
    return {"role": normalized_role, "permissions": data["roles"][storage_key]}
