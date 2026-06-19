from __future__ import annotations

import compileall
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"


@dataclass
class Summary:
    passed: int = 0
    warned: int = 0
    failed: int = 0

    def add(self, status: str) -> None:
        if status == "PASS":
            self.passed += 1
        elif status == "WARN":
            self.warned += 1
        elif status == "FAIL":
            self.failed += 1


summary = Summary()


def print_result(status: str, name: str, detail: str = "") -> None:
    summary.add(status)
    suffix = f" - {detail}" if detail else ""
    print(f"{status:4} {name}{suffix}")


def check_venv_python() -> None:
    if VENV_PYTHON.exists():
        print_result(
            "WARN",
            "project .venv detected",
            f"建议使用项目虚拟环境执行接口探测：{VENV_PYTHON} scripts/check-a3-program.py",
        )
    else:
        print_result("WARN", "project .venv not found", "未检测到 .venv/Scripts/python.exe")


def check_files(paths: list[str], group: str) -> bool:
    ok = True
    for item in paths:
        path = ROOT / item
        exists = path.exists()
        print_result("PASS" if exists else "FAIL", f"{group}: {item}")
        ok = ok and exists
    return ok


def check_compileall() -> bool:
    backend_app = ROOT / "backend" / "app"
    if not backend_app.exists():
        print_result("FAIL", "python -m compileall backend/app", "backend/app 不存在")
        return False
    ok = compileall.compile_dir(str(backend_app), quiet=1)
    print_result("PASS" if ok else "FAIL", "python -m compileall backend/app")
    return bool(ok)


def endpoint_payload(method: str, path: str) -> dict[str, Any] | None:
    if method == "GET":
        return None
    if path == "/api/v1/rag/ask":
        return {"question": "为什么我的 while 循环会死循环？", "studentId": "student-li-ming"}
    if path == "/api/v1/ai-tutor/ask":
        return {"question": "为什么我的 while 循环会死循环？", "studentId": "student-li-ming", "courseName": "Python 程序设计"}
    if path == "/api/v1/resources/generate-pack":
        return {
            "studentId": "student-li-ming",
            "courseName": "Python 程序设计",
            "knowledgePoints": ["while 循环", "循环嵌套", "break / continue"],
        }
    return {}


def check_fastapi_available() -> bool:
    try:
        import fastapi  # noqa: F401
    except ModuleNotFoundError:
        print_result(
            "WARN",
            "当前环境缺少 fastapi，接口探测跳过",
            f"可使用 {VENV_PYTHON} scripts/check-a3-program.py",
        )
        return False
    return True


def check_endpoints() -> bool:
    if not check_fastapi_available():
        return True

    try:
        sys.path.insert(0, str(ROOT / "backend"))
        from fastapi.testclient import TestClient
        from app.main import app
    except Exception as exc:  # noqa: BLE001
        print_result("WARN", "FastAPI TestClient endpoint probe skipped", str(exc))
        return True

    client = TestClient(app)
    endpoints = [
        ("GET", "/api/v1/student-profile/demo"),
        ("POST", "/api/v1/rag/ask"),
        ("POST", "/api/v1/ai-tutor/ask"),
        ("POST", "/api/v1/resources/generate-pack"),
        ("GET", "/api/v1/decision-center/overview"),
    ]
    ok = True
    for method, path in endpoints:
        try:
            if method == "GET":
                response = client.get(path)
            else:
                response = client.post(path, json=endpoint_payload(method, path))
            healthy = response.status_code < 500
            detail = f"HTTP {response.status_code}"
            try:
                body = response.json()
                if isinstance(body, dict):
                    detail += f", keys={','.join(list(body.keys())[:5])}"
            except json.JSONDecodeError:
                pass
            print_result("PASS" if healthy else "FAIL", f"{method} {path}", detail)
            ok = ok and healthy
        except Exception as exc:  # noqa: BLE001
            print_result("FAIL", f"{method} {path}", str(exc))
            ok = False
    return ok


def print_summary() -> None:
    print("-" * 64)
    print(f"SUMMARY PASS={summary.passed} WARN={summary.warned} FAIL={summary.failed}")


def main() -> int:
    backend_files = [
        "backend/app/api/routers/rag.py",
        "backend/app/api/routers/quizzes.py",
        "backend/app/api/routers/resources.py",
        "backend/app/api/routers/ai_tutor.py",
        "backend/app/api/routers/student_profile.py",
        "backend/app/main.py",
    ]
    frontend_files = [
        "frontend/src/views/StudentAssistant.vue",
        "frontend/src/views/TutorChat.vue",
        "frontend/src/views/StudentExamResult.vue",
        "frontend/src/views/StudentReport.vue",
        "frontend/src/views/StudentLearningPath.vue",
        "frontend/src/views/ResourceGenerate.vue",
        "frontend/src/views/AdminKnowledge.vue",
        "frontend/src/views/AdminContentReview.vue",
    ]
    miniprogram_files = [
        "miniprogram/app.json",
        "miniprogram/pages/home/index.js",
        "miniprogram/pages/path/index.js",
        "miniprogram/pages/resources/index.js",
        "miniprogram/pages/tutor/index.js",
        "miniprogram/pages/quiz/index.js",
        "miniprogram/pages/report/index.js",
    ]
    kb_files = [
        "data/course_knowledge/python_programming/syllabus.md",
        "data/course_knowledge/python_programming/chapter_03_control_flow.md",
        "data/course_knowledge/python_programming/knowledge_graph.json",
        "data/course_knowledge/python_programming/resources.json",
        "data/course_knowledge/python_programming/quizzes.json",
    ]

    check_venv_python()
    results = [
        check_compileall(),
        check_files(backend_files, "backend"),
        check_files(frontend_files, "frontend"),
        check_files(miniprogram_files, "miniprogram"),
        check_files(kb_files, "course-knowledge"),
        check_endpoints(),
    ]
    if all(results):
        print_result("PASS", "EduMind program self-check completed")
        print_summary()
        return 0
    print_result("FAIL", "EduMind program self-check found blocking issues")
    print_summary()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
