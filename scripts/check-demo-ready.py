from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    AgentRun,
    AuditLog,
    Course,
    CourseDocument,
    GeneratedResource,
    LearningPath,
    LearningReport,
    Quiz,
    QuizSubmission,
    StudentProfile,
    SystemLog,
    TutorQuestionLog,
)


CORE_STUDENTS = ["李明", "张三", "李四", "王五"]
CORE_TEACHERS = ["王老师", "陈老师", "张老师"]
CORE_COURSES = ["Python 程序设计", "Python 爬虫基础与实践", "人工智能导论", "数据结构与算法", "Web 开发技术"]
CORE_CLASSES = ["计科大三 1 班", "计科大三 2 班"]
COURSE_KB_FILE = ROOT_DIR / "docs" / "course_kb" / "python_programming.json"

FRONTEND_ROUTES = [
    "/",
    "/login",
    "/student",
    "/student/courses",
    "/student/learning-path",
    "/student/assistant",
    "/student/knowledge",
    "/student/exams",
    "/student/reports",
    "/teacher",
    "/courses",
    "/profiles",
    "/learning-path",
    "/teacher-analysis",
    "/reports",
    "/dashboard",
    "/admin/users",
    "/admin/courses",
    "/admin/reports",
    "/admin/knowledge",
    "/resource-generation",
    "/agent-workflow",
    "/logs",
    "/settings",
    "/demo-status",
]


@dataclass
class CheckResult:
    status: str
    name: str
    current: str
    expected: str
    suggestion: str
    category: str = "data"


def _count_check(name: str, current: int, expected: int, suggestion: str, category: str = "data") -> CheckResult:
    return CheckResult(
        "PASS" if current >= expected else "FAIL",
        name,
        str(current),
        str(expected),
        "满足演示要求" if current >= expected else suggestion,
        category,
    )


def _value_check(name: str, ok: bool, current: str, expected: str, suggestion: str, category: str = "data") -> CheckResult:
    return CheckResult("PASS" if ok else "FAIL", name, current, expected, "满足演示要求" if ok else suggestion, category)


def _exists_check(name: str, path: Path, fail_if_missing: bool, suggestion: str, category: str = "file") -> CheckResult:
    if path.exists():
        return CheckResult("PASS", name, "exists", "exists", "文件或目录已存在", category)
    return CheckResult("FAIL" if fail_if_missing else "WARN", name, "missing", "exists", suggestion, category)


def _source_check(name: str, relative_path: str, patterns: list[str], suggestion: str, category: str = "source") -> CheckResult:
    path = ROOT_DIR / relative_path
    if not path.exists():
        return CheckResult("FAIL", name, "missing", "exists", suggestion, category)
    content = path.read_text(encoding="utf-8", errors="replace")
    missing = [pattern for pattern in patterns if pattern not in content]
    return CheckResult(
        "PASS" if not missing else "FAIL",
        name,
        "ok" if not missing else "missing: " + ",".join(missing[:4]),
        "all patterns present",
        "满足演示要求" if not missing else suggestion,
        category,
    )


def _http_check(name: str, url: str, expected_status: int = 200) -> CheckResult:
    try:
        request = Request(url, headers={"User-Agent": "EduMind-demo-ready-check/1.0"})
        with urlopen(request, timeout=8) as response:
            status = int(response.status)
        return CheckResult(
            "PASS" if status == expected_status else "FAIL",
            name,
            str(status),
            str(expected_status),
            "HTTP 访问正常" if status == expected_status else f"请检查服务和路由：{url}",
            "http",
        )
    except HTTPError as exc:
        return CheckResult("FAIL", name, str(exc.code), str(expected_status), f"HTTP 状态异常：{url}", "http")
    except (URLError, TimeoutError) as exc:
        return CheckResult("FAIL", name, "unavailable", str(expected_status), f"服务不可用或超时：{url}；{exc}", "http")
    except Exception as exc:  # noqa: BLE001
        return CheckResult("FAIL", name, "error", str(expected_status), f"检查异常：{exc}", "http")


def _http_post_check(name: str, url: str, payload: dict, expected_status: int = 200) -> CheckResult:
    try:
        request = Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "EduMind-demo-ready-check/1.0",
            },
            method="POST",
        )
        with urlopen(request, timeout=8) as response:
            status = int(response.status)
        return CheckResult(
            "PASS" if status == expected_status else "FAIL",
            name,
            str(status),
            str(expected_status),
            "HTTP 访问正常" if status == expected_status else f"请检查服务和接口：{url}",
            "http",
        )
    except HTTPError as exc:
        return CheckResult("FAIL", name, str(exc.code), str(expected_status), f"HTTP 状态异常：{url}", "http")
    except (URLError, TimeoutError) as exc:
        return CheckResult("FAIL", name, "unavailable", str(expected_status), f"服务不可用或超时：{url}；{exc}", "http")
    except Exception as exc:  # noqa: BLE001
        return CheckResult("FAIL", name, "error", str(expected_status), f"检查异常：{exc}", "http")


def run_checks(backend_url: str, frontend_url: str, include_http: bool) -> tuple[str, list[CheckResult]]:
    results: list[CheckResult] = []
    db = SessionLocal()
    try:
        student_count = db.query(StudentProfile).filter(StudentProfile.student_name.in_(CORE_STUDENTS)).count()
        teacher_count = len({row[0] for row in db.query(Course.teacher_name).filter(Course.teacher_name.in_(CORE_TEACHERS)).all()})
        course_count = db.query(Course).filter(Course.title.in_(CORE_COURSES)).count()
        event_count = db.query(SystemLog).filter(SystemLog.type == "business_event").count()
        results.extend(
            [
                _count_check("courses", db.query(Course).count(), 5, "请运行 python scripts/seed_demo_data.py 初始化核心课程。"),
                _value_check("core_courses", course_count >= 5, str(course_count), "5", "缺少 Python 程序设计等核心课程，请运行 seed-demo-data。"),
                _count_check("student_profiles", db.query(StudentProfile).count(), 4, "请运行 python scripts/seed_demo_data.py 初始化学生画像。"),
                _value_check("core_students", student_count >= 4, str(student_count), "4", "缺少李明、张三、李四、王五画像数据。"),
                _value_check("core_teachers", teacher_count >= 3, str(teacher_count), "3", "缺少王老师、陈老师、张老师课程数据。"),
                _count_check("course_documents", db.query(CourseDocument).count(), 3, "请运行 seed-demo-data 或上传课程资料。"),
                _count_check("tutor_question_logs", db.query(TutorQuestionLog).count(), 5, "请运行 seed-demo-data 或在智能答疑页面提交问题。"),
                _count_check("quizzes", db.query(Quiz).count(), 1, "请生成至少一个测验。"),
                _count_check("quiz_submissions", db.query(QuizSubmission).count(), 1, "请提交至少一次测验。"),
                _count_check("learning_reports", db.query(LearningReport).count(), 3, "请运行 seed-demo-data 或在报告中心生成报告。"),
                _count_check("agent_runs", db.query(AgentRun).count(), 3, "请运行 seed-demo-data 或在 AgentWorkflow 页面运行流程。"),
                _count_check("learning_paths", db.query(LearningPath).count(), 3, "请生成学生学习路径。"),
                _count_check("generated_resources", db.query(GeneratedResource).count(), 3, "请生成学习资源包。"),
                _count_check("audit_logs", db.query(AuditLog).count(), 3, "请运行 seed-demo-data 或触发教师仲裁/审核。"),
                _count_check("business_events", event_count, 9, "请运行 seed-demo-data 或 e2e_demo_flow_check 生成关键业务事件。"),
            ]
        )
    finally:
        db.close()

    for name, path, suggestion in [
        ("backend/storage/uploads", settings.path_from_root(settings.upload_dir), "目录缺失，建议先启动后端或上传课程资料。"),
        ("backend/storage/reports", settings.path_from_root(settings.report_dir), "目录缺失，建议生成报告或运行演示数据脚本。"),
        ("backend/storage/chroma", settings.path_from_root(settings.chroma_persist_dir), "目录缺失，建议先上传文档或构建知识库。"),
        ("frontend/dist/index.html", ROOT_DIR / "frontend" / "dist" / "index.html", "尚未检测到前端构建产物，请运行 npm run build。"),
        ("docs/course_kb/python_programming.json", COURSE_KB_FILE, "课程知识库文件缺失，请补齐 Python 程序设计示例资料集。"),
    ]:
        results.append(_exists_check(name, path, fail_if_missing=False, suggestion=suggestion))

    results.extend(
        [
            _source_check(
                "report_service_methods",
                "backend/app/services/report_service.py",
                ["class ReportService", "generate_student_report", "export_docx", "fallback_reason"],
                "ReportService 缺少报告生成/导出/fallback 方法。",
            ),
            _source_check(
                "profile_service_methods",
                "backend/app/services/profile_service.py",
                ["class ProfileService", "build_profile_visualization", "calculate_risk_level", "merge_profile_evidence"],
                "ProfileService 缺少画像可视化、风险或证据合并方法。",
            ),
            _source_check(
                "quiz_service_methods",
                "backend/app/services/quiz_service.py",
                ["class QuizService", "grade_answers", "wrong_reason_analysis", "dkvmn_updated"],
                "QuizService 缺少评分、错因分析或 DKVMN 更新字段。",
            ),
            _source_check(
                "rag_citations_contract",
                "backend/app/services/lightweight_rag_service.py",
                ["citations", "retrieved_chunks", "parser_warnings", "curriculum_alignment"],
                "RAG 返回结构缺少 citations/retrieved_chunks/parser_warnings/curriculum_alignment。",
            ),
            _source_check(
                "teacher_arbitration_decisions",
                "backend/app/services/governance_service.py",
                ["resume_after_teacher_decision", "approve", "revise", "reject", "teacher_decision_log"],
                "教师仲裁缺少 approve/revise/reject 状态推进逻辑。",
            ),
            _source_check(
                "miniprogram_request_or_fallback",
                "miniprogram/utils/api.js",
                ["requestOrFallback", "fallback", "demoData"],
                "小程序 api.js 缺少 requestOrFallback 或 demoData fallback。",
                "miniprogram",
            ),
        ]
    )

    for relative in [
        "start-dev.bat",
        "stop-dev.bat",
        "seed-demo-data.bat",
        "check-demo-ready.bat",
        "scripts/seed_demo_data.py",
        "scripts/e2e_demo_flow_check.py",
        "scripts/eval_retrieval.py",
        "docker-compose.yml",
        "backend/Dockerfile",
        "frontend/Dockerfile",
        "frontend/nginx.conf",
        ".env.example",
        ".github/workflows/ci.yml",
    ]:
        results.append(_exists_check(relative, ROOT_DIR / relative, fail_if_missing=True, suggestion=f"关键脚本缺失：{relative}", category="script"))

    if include_http:
        backend_url = backend_url.rstrip("/")
        frontend_url = frontend_url.rstrip("/")
        results.extend(
            [
                _http_check("backend_health", f"{backend_url}/health"),
                _http_check("backend_demo_status", f"{backend_url}/api/v1/demo-status"),
                _http_check("backend_courses_api", f"{backend_url}/api/v1/courses"),
                _http_post_check(
                    "backend_rag_ask",
                    f"{backend_url}/api/v1/rag/ask",
                    {
                        "question": "递归题应该怎么分析？",
                        "courseId": "python-programming",
                        "studentId": "demo-student-zhangsan",
                    },
                ),
                _http_post_check(
                    "backend_content_review",
                    f"{backend_url}/api/v1/content-review/check",
                    {
                        "courseId": "python-programming",
                        "content": "递归函数必须包含递归出口，并通过更小规模的问题逐步逼近结果。",
                        "citations": [
                            {
                                "sourceFile": "python_ch02_functions.md",
                                "chapter": "第 2 章 函数与模块化",
                                "section": "递归基础",
                                "snippet": "递归函数必须包含递归出口。",
                            }
                        ],
                    },
                ),
                _http_check("backend_content_review_records", f"{backend_url}/api/v1/content-review/records"),
                _http_check("backend_agent_runs", f"{backend_url}/api/v1/agent-runs"),
                _http_check("backend_audit_logs", f"{backend_url}/api/v1/audit-logs"),
            ]
        )
        for route in FRONTEND_ROUTES:
            results.append(_http_check(f"frontend{route}", f"{frontend_url}{route}"))

    if any(item.status == "FAIL" for item in results):
        overall = "NOT READY"
    elif any(item.status == "WARN" for item in results):
        overall = "WARNING"
    else:
        overall = "READY"
    return overall, results


def write_report(output: Path, overall: str, results: list[CheckResult], backend_url: str, frontend_url: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for item in results if item.status == "PASS")
    warnings = sum(1 for item in results if item.status == "WARN")
    failed = sum(1 for item in results if item.status == "FAIL")
    lines = [
        "# EduMind 演示状态检查报告",
        "",
        f"- 检查时间：{datetime.now().isoformat(timespec='seconds')}",
        f"- 总体状态：{overall}",
        f"- 通过 / 警告 / 失败：{passed} / {warnings} / {failed}",
        f"- 后端地址：{backend_url}",
        f"- 前端地址：{frontend_url}",
        "",
        "## 核心演示对象",
        "",
        f"- 学生：{'、'.join(CORE_STUDENTS)}",
        f"- 教师：{'、'.join(CORE_TEACHERS)}",
        f"- 课程：{'、'.join(CORE_COURSES)}",
        f"- 班级：{'、'.join(CORE_CLASSES)}",
        "",
        "## 检查明细",
        "",
        "| 分类 | 项目 | 状态 | 当前 | 期望 | 建议 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in results:
        lines.append(f"| {item.category} | {item.name} | {item.status} | {item.current} | {item.expected} | {item.suggestion} |")

    lines.extend(
        [
            "",
            "## 三端推荐演示路线",
            "",
            "### 学生端",
            "1. /student 学习总览",
            "2. /student/courses 我的课程",
            "3. /student/learning-path 学习路径",
            "4. /student/assistant 智能答疑",
            "5. /student/exams 测验成绩",
            "6. /student/reports 学习报告",
            "",
            "### 教师端",
            "1. /teacher 班级概览",
            "2. /courses 课程管理",
            "3. /profiles 学生画像",
            "4. /learning-path 学习路径与任务布置",
            "5. /teacher-analysis 测评分析",
            "6. /reports 报告中心",
            "",
            "### 管理员端",
            "1. /dashboard 平台总览",
            "2. /admin/users 用户与角色",
            "3. /admin/courses 课程治理",
            "4. /resource-generation AI 资源生成",
            "5. /agent-workflow Agent 工作流",
            "6. /logs 日志管理",
            "7. /settings 系统设置",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether EduMind is ready for competition demo.")
    parser.add_argument("--backend-url", default="http://127.0.0.1:8000")
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--output", default="docs/reports/demo_ready_check.md")
    parser.add_argument("--skip-http", action="store_true", help="Only check local database/files/scripts.")
    args = parser.parse_args()

    print("EduMind 演示健康检查")
    print(f"项目目录：{ROOT_DIR}")
    print(f"数据库配置：{settings.resolved_database_url}")
    print("说明：本脚本只读取数据库、文件和 HTTP 状态，不删除任何数据。\n")

    try:
        overall, results = run_checks(args.backend_url, args.frontend_url, include_http=not args.skip_http)
    except Exception as exc:
        print("[FAIL] database: 连接失败，请先确认后端依赖和数据库配置。")
        print(f"错误信息：{exc}")
        print("\n总体状态：NOT READY")
        return 1

    for item in results:
        print(f"[{item.status}] {item.name}: {item.current} / {item.expected}，建议：{item.suggestion}")

    output = ROOT_DIR / args.output
    write_report(output, overall, results, args.backend_url, args.frontend_url)
    print(f"\n总体状态：{overall}")
    print(f"验收报告：{output}")
    return 0 if overall in {"READY", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
