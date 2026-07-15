from __future__ import annotations

import re
from typing import Any


def mask_student_no(value: str | int | None) -> str:
    text = "" if value is None else str(value)
    if len(text) <= 6:
        return text[:1] + "*" * max(len(text) - 1, 0)
    return f"{text[:4]}****{text[-2:]}"


def mask_phone(value: str | None) -> str:
    text = value or ""
    return re.sub(r"(\d{3})\d{4}(\d{4})", r"\1****\2", text)


def mask_email(value: str | None) -> str:
    text = value or ""
    if "@" not in text:
        return text
    name, domain = text.split("@", 1)
    if len(name) <= 2:
        return f"{name[:1]}***@{domain}"
    return f"{name[:1]}***{name[-1:]}@{domain}"


def mask_name(value: str | None) -> str:
    text = value or ""
    if not text:
        return ""
    return f"{text[:1]}*"


def mask_score(value: Any) -> str:
    if value is None or value == "":
        return ""
    return "已记录，按角色授权查看"


def summarize_text(value: Any, limit: int = 120) -> str:
    text = "" if value is None else str(value)
    text = re.sub(r"\s+", " ", text).strip()
    text = mask_phone(mask_email(text))
    text = re.sub(r"\b(20\d{8,12})\b", lambda m: mask_student_no(m.group(1)), text)
    return text if len(text) <= limit else f"{text[:limit]}..."


def redact_payload(value: Any, limit: int = 240) -> str:
    if isinstance(value, dict):
        safe = []
        for key, item in value.items():
            lowered = str(key).lower()
            if any(token in lowered for token in ("phone", "mobile", "email", "student_no", "score", "dialog", "report")):
                safe.append(f"{key}=已脱敏")
            elif any(token in str(key) for token in ("姓名", "电话", "邮箱", "成绩", "对话", "报告")):
                safe.append(f"{key}=已脱敏")
            else:
                safe.append(f"{key}={summarize_text(item, 40)}")
        return summarize_text("；".join(safe), limit)
    return summarize_text(value, limit)
