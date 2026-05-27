from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    AgentRun,
    Course,
    CourseDocument,
    GeneratedResource,
    LearningPath,
    LearningReport,
    Quiz,
    QuizSubmission,
    StudentProfile,
    TutorQuestionLog,
)


@dataclass
class CheckResult:
    status: str
    name: str
    current: str
    expected: str
    suggestion: str


def _count_check(name: str, current: int, expected: int, suggestion: str) -> CheckResult:
    return CheckResult(
        status="PASS" if current >= expected else "FAIL",
        name=name,
        current=str(current),
        expected=str(expected),
        suggestion="满足演示要求" if current >= expected else suggestion,
    )


def _exists_check(name: str, path: Path, fail_if_missing: bool, suggestion: str) -> CheckResult:
    exists = path.exists()
    if exists:
        return CheckResult("PASS", name, "exists", "exists", "文件或目录已存在")
    return CheckResult("FAIL" if fail_if_missing else "WARN", name, "missing", "exists", suggestion)


def _print_result(item: CheckResult) -> None:
    print(f"[{item.status}] {item.name}: {item.current} / {item.expected}，建议：{item.suggestion}")


def run_checks() -> tuple[str, list[CheckResult]]:
    results: list[CheckResult] = []

    db = SessionLocal()
    try:
        results.extend(
            [
                _count_check("courses", db.query(Course).count(), 3, "建议运行 python scripts/seed-demo-data.py 初始化演示课程"),
                _count_check(
                    "student_profiles",
                    db.query(StudentProfile).count(),
                    3,
                    "建议运行 python scripts/seed-demo-data.py 初始化学生画像",
                ),
                _count_check(
                    "course_documents",
                    db.query(CourseDocument).count(),
                    3,
                    "建议运行 python scripts/seed-demo-data.py，或在知识库页面上传课程资料",
                ),
                _count_check(
                    "tutor_question_logs",
                    db.query(TutorQuestionLog).count(),
                    8,
                    "建议运行 python scripts/seed-demo-data.py，或在智能答疑页面提交更多问题",
                ),
                _count_check("quizzes", db.query(Quiz).count(), 1, "建议生成至少一个测验"),
                _count_check(
                    "quiz_submissions",
                    db.query(QuizSubmission).count(),
                    1,
                    "建议提交至少一次测验，用于支撑教师分析页面",
                ),
                _count_check(
                    "learning_reports",
                    db.query(LearningReport).count(),
                    3,
                    "建议运行 python scripts/seed-demo-data.py，或在报告中心生成学习报告",
                ),
                _count_check(
                    "agent_runs",
                    db.query(AgentRun).count(),
                    3,
                    "建议运行 python scripts/seed-demo-data.py，或在 AgentWorkflow 页面运行完整学习流",
                ),
                _count_check(
                    "learning_paths",
                    db.query(LearningPath).count(),
                    1,
                    "建议生成至少一条学习路径",
                ),
                _count_check(
                    "generated_resources",
                    db.query(GeneratedResource).count(),
                    1,
                    "建议生成至少一条学习资源",
                ),
            ]
        )
    finally:
        db.close()

    storage_checks = [
        ("backend/storage/uploads", settings.path_from_root(settings.upload_dir), "目录缺失。建议先启动后端或上传课程资料"),
        ("backend/storage/reports", settings.path_from_root(settings.report_dir), "目录缺失。建议生成报告或运行演示数据脚本"),
        (
            "backend/storage/chroma",
            settings.path_from_root(settings.chroma_persist_dir),
            "目录缺失。建议先上传文档或运行知识库构建",
        ),
    ]
    for name, path, suggestion in storage_checks:
        results.append(_exists_check(name, path, fail_if_missing=False, suggestion=suggestion))

    script_checks = [
        "start-dev.bat",
        "stop-dev.bat",
        "seed-demo-data.bat",
        "scripts/seed-demo-data.py",
    ]
    for relative in script_checks:
        results.append(
            _exists_check(
                relative,
                ROOT_DIR / relative,
                fail_if_missing=True,
                suggestion=f"关键脚本缺失，请恢复 {relative}",
            )
        )

    if any(item.status == "FAIL" for item in results):
        overall = "NOT READY"
    elif any(item.status == "WARN" for item in results):
        overall = "WARNING"
    else:
        overall = "READY"
    return overall, results


def main() -> int:
    print("EduMind 演示健康检查")
    print(f"项目目录：{ROOT_DIR}")
    print(f"数据库配置：{settings.resolved_database_url}")
    print("说明：本脚本只读取数据库和文件状态，不修改数据库，不删除任何数据。\n")

    try:
        overall, results = run_checks()
    except Exception as exc:
        print("[FAIL] database: connection failed / available，建议先确认后端依赖和数据库配置")
        print(f"错误信息：{exc}")
        print("\n总体状态：NOT READY")
        return 1

    for item in results:
        _print_result(item)

    print(f"\n总体状态：{overall}")
    if overall == "READY":
        print("建议演示顺序：/dashboard -> /knowledge-base -> /tutor-chat -> /teacher-analysis -> /agent-workflow -> /reports -> /logs -> /settings")
        return 0
    if overall == "WARNING":
        print("存在非阻塞 warning，可继续演示；建议按提示补齐 storage 或知识库运行状态。")
        return 0
    print("演示数据不足，建议先运行：python scripts/seed-demo-data.py")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
