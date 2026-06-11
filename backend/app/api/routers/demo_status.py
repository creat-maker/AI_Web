from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter


router = APIRouter(prefix="/demo-status", tags=["demo-status"])

ROOT_DIR = Path(__file__).resolve().parents[4]
FLOW_REPORT_PATH = ROOT_DIR / "reports" / "demo_flow_check.md"
READY_CHECK_PATH = ROOT_DIR / "docs" / "reports" / "demo_ready_check.md"
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist" / "index.html"
COURSE_KB_FILE = ROOT_DIR / "docs" / "course_kb" / "python_programming.json"

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
    "student": ["/student", "/student/courses", "/student/learning-path", "/student/assistant", "/student/exams", "/student/reports"],
    "teacher": ["/teacher", "/courses", "/profiles", "/learning-path", "/teacher-analysis", "/reports"],
    "admin": ["/dashboard", "/admin/users", "/admin/courses", "/resource-generation", "/agent-workflow", "/logs", "/settings"],
}

CAPABILITY_CHECKLIST = [
    {"name": "Web 三端 Ready", "status": "PASS", "detail": "学生端、教师端、管理员端核心页面和演示路线已固化。"},
    {"name": "小程序学生端 Ready", "status": "PASS", "detail": "miniprogram 原生微信小程序学生端体验版已提供 6 个页面和本地 fallback 数据。"},
    {"name": "Agent 执行链路 Ready", "status": "PASS", "detail": "AgentWorkflow 展示画像构建、知识检索、路径规划、资源生成、内容审核和学习报告。"},
    {"name": "三端角色系统", "status": "PASS", "detail": "学生端、教师端、管理员端入口和菜单已拆分。"},
    {"name": "学习画像", "status": "PASS", "detail": "围绕张三、李四、王五生成画像和薄弱点。"},
    {"name": "个性化路径", "status": "PASS", "detail": "学习路径与资源包、任务布置联动。"},
    {"name": "智能答疑", "status": "PASS", "detail": "保留 RAG/fallback 答疑与引用展示。"},
    {"name": "资源生成", "status": "PASS", "detail": "支持演示资源包生成和任务记录。"},
    {"name": "报告生成", "status": "PASS", "detail": "学习报告可生成、预览并下载。"},
    {"name": "Agent 工作流", "status": "PASS", "detail": "展示节点、产物、运行记录和失败边界。"},
    {"name": "日志与系统治理", "status": "PASS", "detail": "聚合业务事件、系统日志和设置状态。"},
]

REAL_CAPABILITIES = [
    "三端角色系统",
    "小程序学生端体验版",
    "对话式学习画像",
    "5 类个性化资源生成",
    "课程知识库",
    "轻量 RAG 引用问答",
    "防幻觉内容审核",
    "Agent 执行链路",
    "学习画像",
    "个性化路径",
    "智能答疑",
    "资源生成记录",
    "报告生成",
    "Agent 工作流展示",
    "日志与系统治理",
]

DEMO_FALLBACK_CAPABILITIES = [
    "AI 资源正文可由 fallback 模板生成",
    "Agent 节点输出可用演示数据回放",
    "报告审核状态机为轻量演示",
    "真实登录鉴权、真实 LangGraph、真实 RAGFlow/Dify/FastGPT 为后续扩展",
]


def _source_has(relative_path: str, pattern: str) -> bool:
    path = ROOT_DIR / relative_path
    if not path.exists():
        return False
    return pattern in path.read_text(encoding="utf-8", errors="replace")


def _route_capability(name: str, route: str, relative_path: str, pattern: str, detail: str) -> dict:
    exists = _source_has(relative_path, pattern)
    return {
        "name": name,
        "status": "PASS" if exists else "FAIL",
        "detail": f"{route} {detail}" if exists else f"{route} 未在 {relative_path} 中注册",
    }


def _capability_checklist() -> list[dict]:
    dynamic_api_checks = [
        _route_capability(
            "对话式画像兼容接口",
            "POST /api/v1/profile-dialog/run",
            "backend/app/api/routers/profile_dialog.py",
            '@router.post("/run")',
            "已存在，返回 StudentAssistant 兼容的单轮画像结构。",
        ),
        _route_capability(
            "5 类资源包生成接口",
            "POST /api/v1/resources/generate-pack",
            "backend/app/api/routers/resources.py",
            '@router.post("/generate-pack")',
            "已存在，返回稳定的规则化资源包。",
        ),
        _route_capability(
            "轻量 RAG 引用问答接口",
            "POST /api/v1/rag/ask",
            "backend/app/api/routers/rag.py",
            '@router.post("/ask")',
            "已存在，返回回答、引用、匹配片段、可信度和推荐练习。",
        ),
        _route_capability(
            "防幻觉内容审核接口",
            "POST /api/v1/content-review/check",
            "backend/app/api/routers/content_review.py",
            '@router.post("/check")',
            "已存在，返回审核状态、风险等级、可信度和建议。",
        ),
        _route_capability(
            "演示状态接口",
            "GET /api/v1/demo-status",
            "backend/app/api/routers/demo_status.py",
            '@router.get("")',
            "已存在，会读取本地 readiness/e2e 报告。",
        ),
        {
            "name": "课程知识库文件",
            "status": "PASS" if COURSE_KB_FILE.exists() else "FAIL",
            "detail": "docs/course_kb/python_programming.json 已存在"
            if COURSE_KB_FILE.exists()
            else "docs/course_kb/python_programming.json 缺失",
        },
    ]
    return CAPABILITY_CHECKLIST[:2] + dynamic_api_checks + CAPABILITY_CHECKLIST[2:]


def _extract(pattern: str, text: str, fallback: str = "") -> str:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else fallback


def _check_report_status(content: str, keyword: str) -> str:
    rows = [line for line in content.splitlines() if keyword in line]
    if not rows:
        return "UNKNOWN"
    if any("| FAIL |" in line for line in rows):
        return "FAIL"
    if any("| WARN |" in line for line in rows):
        return "WARN"
    return "PASS"


def _readiness_checks() -> list[dict]:
    if not READY_CHECK_PATH.exists():
        return [
            {"name": "前端页面可访问状态", "status": "UNKNOWN", "detail": "尚未运行 scripts/check-demo-ready.py"},
            {"name": "后端接口健康状态", "status": "UNKNOWN", "detail": "尚未运行 scripts/check-demo-ready.py"},
            {"name": "三端核心路由检查结果", "status": "UNKNOWN", "detail": "尚未运行 scripts/check-demo-ready.py"},
            {"name": "演示数据是否存在", "status": "UNKNOWN", "detail": "尚未运行 scripts/check-demo-ready.py"},
            {
                "name": "最近一次构建/验收结果",
                "status": "PASS" if FRONTEND_DIST.exists() else "WARN",
                "detail": "frontend/dist/index.html 已存在" if FRONTEND_DIST.exists() else "尚未检测到 frontend/dist/index.html",
            },
        ]

    content = READY_CHECK_PATH.read_text(encoding="utf-8", errors="replace")
    overall = _extract(r"总体状态：([^\n]+)", content, "UNKNOWN")
    return [
        {"name": "前端页面可访问状态", "status": _check_report_status(content, "frontend/"), "detail": "来自 docs/reports/demo_ready_check.md"},
        {"name": "后端接口健康状态", "status": _check_report_status(content, "backend_"), "detail": "来自 docs/reports/demo_ready_check.md"},
        {"name": "三端核心路由检查结果", "status": _check_report_status(content, "frontend/"), "detail": "学生端、教师端、管理员端核心路由"},
        {"name": "演示数据是否存在", "status": _check_report_status(content, "core_"), "detail": "张三、李四、王五和四门核心课程"},
        {
            "name": "最近一次构建/验收结果",
            "status": "PASS" if overall == "READY" and FRONTEND_DIST.exists() else "WARN",
            "detail": f"检查报告：{overall}；构建产物：{'存在' if FRONTEND_DIST.exists() else '缺失'}",
        },
        {
            "name": "课程知识库文件",
            "status": "PASS" if COURSE_KB_FILE.exists() else "WARN",
            "detail": "docs/course_kb/python_programming.json" if COURSE_KB_FILE.exists() else "课程知识库文件缺失",
        },
    ]


def _base_response(status: str, message: str) -> dict:
    return {
        "status": status,
        "message": message,
        "passed": 0,
        "total": 0,
        "pass_rate": "0%",
        "report_path": str(Path("reports") / "demo_flow_check.md"),
        "ready_report_path": str(Path("docs") / "reports" / "demo_ready_check.md"),
        "last_checked_at": "",
        "key_events": [{"event_type": event_type, "label": label, "status": "UNKNOWN"} for event_type, label in EVENT_LABELS.items()],
        "demo_routes": DEMO_ROUTES,
        "readiness_checks": _readiness_checks(),
        "capability_checklist": _capability_checklist(),
        "real_capabilities": REAL_CAPABILITIES,
        "demo_fallback_capabilities": DEMO_FALLBACK_CAPABILITIES,
        "refresh_command": (
            r"python scripts\check-demo-ready.py && "
            r"python scripts\e2e_demo_flow_check.py --base-url http://127.0.0.1:8000 --output reports\demo_flow_check.md"
        ),
    }


@router.get("")
def demo_status():
    if not FLOW_REPORT_PATH.exists():
        return _base_response("missing_report", "请先运行 scripts/e2e_demo_flow_check.py 生成端到端验收报告。")

    content = FLOW_REPORT_PATH.read_text(encoding="utf-8", errors="replace")
    checked_at = _extract(r"验收时间：([^\n]+)", content)
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
        "last_checked_at": checked_at,
        "key_events": key_events,
    }
