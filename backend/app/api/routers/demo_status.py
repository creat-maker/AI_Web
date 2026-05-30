from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter


router = APIRouter(prefix="/demo-status", tags=["demo-status"])

REPORT_PATH = Path(__file__).resolve().parents[4] / "reports" / "demo_flow_check.md"

EVENT_LABELS = {
    "profile_generated": "画像生成",
    "resource_generated": "资源包生成",
    "resource_added_to_path": "资源加入路径",
    "path_updated": "学习路径更新",
    "teacher_intervention_created": "教师干预",
    "task_assigned": "任务布置",
    "quiz_completed": "测验完成",
    "question_answered": "智能答疑",
    "admin_review_completed": "管理员审核",
}

DEMO_ROUTES = {
    "student": ["学习总览", "对话建画像", "个性化资源生成", "学习路径", "智能答疑", "测验成绩", "学习报告"],
    "teacher": ["班级概览", "学生画像分析", "布置补强任务", "测验评价", "报告中心"],
    "admin": ["平台总览", "Agent 工作流", "资源生成中心", "报告审核", "日志管理"],
}

REAL_CAPABILITIES = ["三端角色切换", "业务事件写入", "资源包记录", "学习路径联动", "TutorChat 问答保存", "日志查询"]
DEMO_FALLBACK_CAPABILITIES = ["资源内容生成", "Agent 节点输出", "报告审核状态机", "真实 LangGraph", "真实 RAGFlow", "真实权限鉴权"]


def _base_response(status: str, message: str) -> dict:
    return {
        "status": status,
        "message": message,
        "passed": 0,
        "total": 0,
        "pass_rate": "0%",
        "report_path": str(Path("reports") / "demo_flow_check.md"),
        "last_checked_at": "",
        "key_events": [
            {"event_type": event_type, "label": label, "status": "UNKNOWN"}
            for event_type, label in EVENT_LABELS.items()
        ],
        "demo_routes": DEMO_ROUTES,
        "real_capabilities": REAL_CAPABILITIES,
        "demo_fallback_capabilities": DEMO_FALLBACK_CAPABILITIES,
        "refresh_command": r"python scripts\e2e_demo_flow_check.py --base-url http://127.0.0.1:8000 --output reports\demo_flow_check.md",
    }


def _extract(pattern: str, text: str, fallback: str = "") -> str:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else fallback


@router.get("")
def demo_status():
    if not REPORT_PATH.exists():
        return _base_response("missing_report", "请先运行 scripts/e2e_demo_flow_check.py 生成验收报告。")

    content = REPORT_PATH.read_text(encoding="utf-8", errors="replace")
    checked_at = _extract(r"验收时间：([^\n]+)", content)
    passed_text = _extract(r"总体通过率：(\d+)/(\d+)", content)
    total_match = re.search(r"总体通过率：(\d+)/(\d+)\s+\(([^)]+)\)", content)
    passed = int(total_match.group(1)) if total_match else 0
    total = int(total_match.group(2)) if total_match else 0
    pass_rate = total_match.group(3) if total_match else "0%"
    key_events = []
    for event_type, label in EVENT_LABELS.items():
        status = "PASS" if re.search(rf"-\s+PASS\s+`{re.escape(event_type)}`", content) else "FAIL"
        key_events.append({"event_type": event_type, "label": label, "status": status})
    is_ready = total > 0 and passed == total and all(item["status"] == "PASS" for item in key_events)
    return {
        **_base_response("ready" if is_ready else "warning", "验收报告已读取。" if is_ready else "验收报告存在，但存在未通过项。"),
        "passed": passed,
        "total": total,
        "pass_rate": pass_rate,
        "report_path": str(Path("reports") / "demo_flow_check.md"),
        "last_checked_at": checked_at,
        "key_events": key_events,
        "raw_summary": passed_text,
    }
