from __future__ import annotations

import json
import secrets
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

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


class StatusPayload(BaseModel):
    status: str


class RolePayload(BaseModel):
    role: str


class PermissionPayload(BaseModel):
    permissions: list[str]


def _load() -> dict[str, Any]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"users": DEFAULT_USERS, "roles": DEFAULT_ROLES}


def _save(data: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@router.get("/users")
def list_users():
    data = _load()
    users = data["users"]
    return {
        "users": users,
        "summary": {
            "total": len(users),
            "enabled": sum(1 for item in users if item["status"] == "启用"),
            "students": sum(1 for item in users if item["role"] == "学生"),
            "teachers": sum(1 for item in users if item["role"] == "教师"),
            "assistants": sum(1 for item in users if item["role"] == "助教"),
            "admins": sum(1 for item in users if item["role"] == "管理员"),
        },
    }


@router.patch("/users/{user_id}/status")
def update_status(user_id: int, payload: StatusPayload):
    data = _load()
    for user in data["users"]:
        if user["id"] == user_id:
            user["status"] = payload.status
            _save(data)
            return user
    return {"id": user_id, "status": payload.status}


@router.patch("/users/{user_id}/role")
def update_role(user_id: int, payload: RolePayload):
    data = _load()
    for user in data["users"]:
        if user["id"] == user_id:
            user["role"] = payload.role
            _save(data)
            return user
    return {"id": user_id, "role": payload.role}


@router.post("/users/{user_id}/reset-password")
def reset_password(user_id: int):
    password = f"EM-{secrets.token_hex(3).upper()}"
    return {"user_id": user_id, "temporary_password": password, "message": "已生成一次性临时密码，请通过线下安全渠道发送给用户。"}


@router.get("/roles")
def list_roles():
    return _load()["roles"]


@router.patch("/roles/{role}/permissions")
def update_role_permissions(role: str, payload: PermissionPayload):
    data = _load()
    data["roles"][role] = payload.permissions
    _save(data)
    return {"role": role, "permissions": payload.permissions}
