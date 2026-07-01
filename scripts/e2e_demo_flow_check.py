from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REQUIRED_EVENT_TYPES = [
    "profile_generated",
    "resource_generated",
    "resource_added_to_path",
    "path_updated",
    "teacher_intervention_created",
    "task_assigned",
    "quiz_completed",
    "question_answered",
    "admin_review_completed",
]


@dataclass
class StepResult:
    name: str
    endpoint: str
    method: str = "GET"
    success: bool = False
    status_code: int | None = None
    key_fields: dict[str, Any] = field(default_factory=dict)
    event_written: str = "not_applicable"
    failure_reason: str = ""


class DemoFlowChecker:
    def __init__(self, base_url: str, timeout: int = 12) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.steps: list[StepResult] = []

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, Any]:
        data = None
        headers = {"Accept": "application/json", "User-Agent": "EduMind-e2e-demo-flow-check/1.0"}
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)
        with urlopen(request, timeout=self.timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            return int(response.status), json.loads(text) if text else None

    def safe_request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int | None, Any, str]:
        try:
            status, body = self.request(method, path, payload)
            return status, body, ""
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            return exc.code, None, detail or str(exc)
        except URLError as exc:
            return None, None, f"request failed: {exc.reason}"
        except TimeoutError:
            return None, None, "request timed out"
        except Exception as exc:  # noqa: BLE001
            return None, None, f"unexpected error: {exc}"

    def add_step(self, **kwargs: Any) -> None:
        self.steps.append(StepResult(**kwargs))

    def get_events(self) -> list[dict[str, Any]]:
        status, body, _ = self.safe_request("GET", "/api/v1/events?limit=200")
        if status and status < 400 and isinstance(body, list):
            return body
        return []

    def event_exists(self, event_type: str, target_id: Any | None = None) -> bool:
        for item in self.get_events():
            if item.get("event_type") != event_type:
                continue
            if target_id is None or str(item.get("target_id")) == str(target_id):
                return True
        return False

    def first_course(self) -> dict[str, Any] | None:
        status, body, reason = self.safe_request("GET", "/api/v1/courses")
        if status and status < 400 and isinstance(body, list) and body:
            return body[0]
        self.add_step(
            name="准备课程数据",
            endpoint="/api/v1/courses",
            method="GET",
            success=False,
            status_code=status,
            failure_reason=reason or "课程列表为空，请先运行 python scripts/seed_demo_data.py。",
        )
        return None

    @staticmethod
    def pick_profile_dialog_run(body: Any) -> dict[str, Any]:
        if not isinstance(body, dict):
            raise ValueError("response is not a JSON object")
        required = ["studentName", "courseName", "summary", "dimensions", "weakKnowledgePoints", "recommendedStrategy", "mode"]
        missing = [key for key in required if key not in body]
        if missing:
            raise ValueError(f"missing fields: {', '.join(missing)}")
        if not isinstance(body.get("dimensions"), list) or not body["dimensions"]:
            raise ValueError("dimensions must be a non-empty list")
        if not isinstance(body.get("weakKnowledgePoints"), list):
            raise ValueError("weakKnowledgePoints must be a list")
        return {
            "studentName": body.get("studentName"),
            "dimension_count": len(body.get("dimensions", [])),
            "weak_point_count": len(body.get("weakKnowledgePoints", [])),
            "mode": body.get("mode"),
        }

    @staticmethod
    def pick_resource_pack(body: Any) -> dict[str, Any]:
        if not isinstance(body, dict):
            raise ValueError("response is not a JSON object")
        required = ["packageTitle", "courseName", "weakPoints", "resourceCount", "resources", "mode"]
        missing = [key for key in required if key not in body]
        if missing:
            raise ValueError(f"missing fields: {', '.join(missing)}")
        resources = body.get("resources")
        if not isinstance(resources, list) or len(resources) < 5:
            raise ValueError("resources must contain at least 5 items")
        return {
            "packageTitle": body.get("packageTitle"),
            "resource_count": len(resources),
            "mode": body.get("mode"),
        }

    @staticmethod
    def pick_rag_answer(body: Any) -> dict[str, Any]:
        if not isinstance(body, dict):
            raise ValueError("response is not a JSON object")
        required = ["answer", "citations", "matchedChunks", "confidence", "recommendedExercises", "relatedKnowledgePoints"]
        missing = [key for key in required if key not in body]
        if missing:
            raise ValueError(f"missing fields: {', '.join(missing)}")
        if not body.get("answer"):
            raise ValueError("answer is empty")
        if not isinstance(body.get("citations"), list):
            raise ValueError("citations must be a list")
        return {
            "citation_count": len(body.get("citations", [])),
            "matched_chunk_count": len(body.get("matchedChunks", [])),
            "confidence": body.get("confidence"),
            "retrieval_mode": body.get("retrievalMode"),
        }

    @staticmethod
    def pick_content_review(body: Any) -> dict[str, Any]:
        if not isinstance(body, dict):
            raise ValueError("response is not a JSON object")
        required = ["riskLevel", "confidence", "citationCoverage", "reviewStatus", "suggestions"]
        missing = [key for key in required if key not in body]
        if missing:
            raise ValueError(f"missing fields: {', '.join(missing)}")
        return {
            "review_status": body.get("reviewStatus"),
            "risk_level": body.get("riskLevel"),
            "confidence": body.get("confidence"),
            "citation_coverage": body.get("citationCoverage"),
        }

    @staticmethod
    def pick_demo_status(body: Any) -> dict[str, Any]:
        if not isinstance(body, dict):
            raise ValueError("response is not a JSON object")
        required = ["status", "message", "capability_checklist", "readiness_checks"]
        missing = [key for key in required if key not in body]
        if missing:
            raise ValueError(f"missing fields: {', '.join(missing)}")
        return {
            "status": body.get("status"),
            "capability_count": len(body.get("capability_checklist", [])),
            "readiness_count": len(body.get("readiness_checks", [])),
        }

    def run_step(self, name: str, method: str, endpoint: str, payload: dict[str, Any] | None, expected_event: str | None, key_picker) -> Any:
        status, body, reason = self.safe_request(method, endpoint, payload)
        success = bool(status and status < 400)
        key_fields: dict[str, Any] = {}
        target_id = None
        if success:
            try:
                key_fields = key_picker(body) if key_picker else {}
                target_id = key_fields.get("target_id")
            except Exception as exc:  # noqa: BLE001
                success = False
                reason = f"关键字段解析失败：{exc}"
        event_written = "not_applicable"
        if expected_event:
            event_written = "yes" if self.event_exists(expected_event, target_id) or self.event_exists(expected_event) else "no"
            success = success and event_written == "yes"
            if event_written == "no" and not reason:
                reason = f"未查询到事件 {expected_event}"
        self.add_step(
            name=name,
            endpoint=endpoint,
            method=method,
            success=success,
            status_code=status,
            key_fields=key_fields,
            event_written=event_written,
            failure_reason=reason,
        )
        return body if success else None

    def run(self) -> None:
        course = self.first_course()
        course_id = course.get("id") if course else None
        stamp = datetime.now().strftime("%m%d%H%M%S")

        profile = self.run_step(
            "A. 画像生成",
            "POST",
            "/api/v1/profiles/generate",
            {
                "course_id": course_id,
                "student_name": "张三",
                "current_level": "基础薄弱",
                "learning_goal": "完成 Python 爬虫基础与实践学习闭环演示",
                "weak_points": ["HTTP 请求", "引用来源", "学习路径规划"],
                "learning_preference": "案例驱动",
            },
            "profile_generated",
            lambda body: {"profile_id": body.get("id"), "student_name": body.get("student_name"), "target_id": body.get("id")},
        )
        profile_id = profile.get("id") if isinstance(profile, dict) else None
        student_name = profile.get("student_name") if isinstance(profile, dict) else "张三"

        package = self.run_step(
            "B. 个性化资源包生成",
            "POST",
            "/api/v1/events/resource-package",
            {"course_id": course_id, "student_profile_id": profile_id, "actor_role": "student", "actor_name": student_name},
            "resource_generated",
            lambda body: {"package_id": body.get("package_id"), "resource_count": len(body.get("resources", [])), "target_id": body.get("package_id")},
        )
        package_id = package.get("package_id") if isinstance(package, dict) else "pkg-demo-missing"

        self.run_step(
            "C. 资源包加入学习路径",
            "POST",
            "/api/v1/events/add-resource-to-path",
            {"course_id": course_id, "student_profile_id": profile_id, "package_id": package_id, "actor_role": "student", "actor_name": student_name},
            "resource_added_to_path",
            lambda body: {"path_id": body.get("path_id"), "package_id": package_id, "target_id": body.get("path_id")},
        )

        self.run_step(
            "D. 教师布置补强任务",
            "POST",
            "/api/v1/events/assign-task",
            {"course_id": course_id, "student_profile_id": profile_id, "weak_point": "HTTP 请求", "task_type": "完成分层练习", "actor_role": "teacher", "actor_name": "王老师"},
            "task_assigned",
            lambda body: {"task_id": body.get("task", {}).get("task_id"), "target_id": body.get("task", {}).get("task_id")},
        )

        self.run_step(
            "E. demo 测验完成",
            "POST",
            "/api/v1/events/demo-quiz",
            {"course_id": course_id, "student_profile_id": profile_id, "actor_role": "student", "actor_name": student_name},
            "quiz_completed",
            lambda body: {"submission_id": body.get("id"), "score": body.get("quiz_result", {}).get("score"), "target_id": body.get("id")},
        )

        self.run_step(
            "F. 智能答疑",
            "POST",
            "/api/v1/tutor/ask",
            {"course_id": course_id, "question": "如何判断一次回答是否有可靠引用来源？", "top_k": 3, "heuristic_mode": True, "no_direct_answer": False, "hint_level": "medium"},
            "question_answered",
            lambda body: {"citation_count": len(body.get("citation_sources", [])), "confidence": body.get("confidence")},
        )

        self.run_step(
            "G. 管理员报告审核",
            "POST",
            "/api/v1/events/admin-review",
            {
                "event_type": "admin_review_completed",
                "title": "端到端验收报告审核通过",
                "description": "管理员完成一次 demo/fallback 报告审核。",
                "actor_role": "admin",
                "actor_name": "管理员",
                "target_type": "learning_report",
                "target_id": f"e2e-report-{stamp}",
                "metadata": {"demo": True},
            },
            "admin_review_completed",
            lambda body: {"event_id": body.get("event_id")},
        )

        self.run_step("H. 查询业务事件", "GET", "/api/v1/events?limit=200", None, None, lambda body: {"event_count": len(body or [])})
        self.run_step("I. 查询治理审计日志", "GET", "/api/v1/audit-logs", None, None, lambda body: {"log_count": len(body or [])})
        self.run_step("J. 查询 Agent 工作流", "GET", "/api/v1/agent-workflow", None, None, lambda body: {"template_count": len(body.get("workflow_templates", [])), "event_run_count": len(body.get("business_event_records", []))})
        self.run_step("K. 查询学习路径", "GET", "/api/v1/learning-paths", None, None, lambda body: {"path_count": len(body or []), "package_id_checked": package_id})

        self.run_step(
            "L. profile-dialog/run compatibility API",
            "POST",
            "/api/v1/profile-dialog/run",
            {
                "studentId": "demo-student-zhangsan",
                "studentName": "张三",
                "courseId": "demo-course-python",
                "courseName": "Python 程序设计",
                "answer": "Python 文件处理和递归边界比较薄弱，喜欢代码案例和分步练习。",
            },
            None,
            self.pick_profile_dialog_run,
        )
        self.run_step(
            "M. resources/generate-pack API",
            "POST",
            "/api/v1/resources/generate-pack",
            {
                "studentId": "demo-student-zhangsan",
                "courseId": "demo-course-python",
                "courseName": "Python 程序设计",
                "weakPoints": ["Python 文件处理", "递归边界", "代码调试"],
            },
            None,
            self.pick_resource_pack,
        )
        self.run_step(
            "N. rag/ask API",
            "POST",
            "/api/v1/rag/ask",
            {
                "question": "递归题应该怎么分析？",
                "courseId": "python-programming",
                "studentId": "demo-student-zhangsan",
            },
            None,
            self.pick_rag_answer,
        )
        self.run_step(
            "O. content-review/check API",
            "POST",
            "/api/v1/content-review/check",
            {
                "courseId": "python-programming",
                "content": "递归函数需要递归出口，并通过更小规模的问题逐步逼近结果。",
                "citations": [
                    {
                        "sourceFile": "python_ch02_functions.md",
                        "chapter": "函数与模块化",
                        "section": "递归基础",
                        "snippet": "递归函数必须包含递归出口。",
                    }
                ],
            },
            None,
            self.pick_content_review,
        )
        self.run_step("P. demo-status API", "GET", "/api/v1/demo-status", None, None, self.pick_demo_status)

    def event_summary(self) -> dict[str, bool]:
        existing = {item.get("event_type") for item in self.get_events()}
        return {event_type: event_type in existing for event_type in REQUIRED_EVENT_TYPES}

    def write_report(self, output: Path) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        passed = sum(1 for item in self.steps if item.success)
        total = len(self.steps)
        event_summary = self.event_summary()
        lines = [
            "# EduMind 比赛演示端到端验收报告",
            "",
            f"- 验收时间：{datetime.now().isoformat(timespec='seconds')}",
            f"- 后端地址：{self.base_url}",
            f"- 总体通过率：{passed}/{total} ({round(passed / total * 100) if total else 0}%)",
            "",
            "## 步骤结果",
            "",
            "| 步骤 | 接口 | 结果 | HTTP | 关键字段 | 事件写入 | 失败原因 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for item in self.steps:
            key_fields = json.dumps(item.key_fields, ensure_ascii=False)
            lines.append(
                f"| {item.name} | `{item.method} {item.endpoint}` | {'PASS' if item.success else 'FAIL'} | "
                f"{item.status_code or '-'} | `{key_fields}` | {item.event_written} | {item.failure_reason or '-'} |"
            )
        lines.extend(["", "## 关键 event_type 检查", ""])
        for event_type, ok in event_summary.items():
            lines.append(f"- {'PASS' if ok else 'FAIL'} `{event_type}`")
        lines.extend(
            [
                "",
                "## 能力边界说明",
                "",
                "- 业务事件写入 system_logs 表，用于 EduMind 三端演示闭环。",
                "- 资源包、学习路径、测验、问答和报告记录会沉淀到后端数据表。",
                "- 当前真实登录鉴权、真实 LangGraph、真实 RAGFlow/Dify/FastGPT 为后续扩展项。",
                "",
                "## 推荐演示路线",
                "",
                "```text",
                "学生端：/student -> /student/courses -> /student/learning-path -> /student/assistant -> /student/exams -> /student/reports",
                "教师端：/teacher -> /courses -> /profiles -> /learning-path -> /teacher-analysis -> /reports",
                "管理员端：/dashboard -> /admin/users -> /admin/courses -> /resource-generation -> /agent-workflow -> /logs -> /settings",
                "```",
                "",
            ]
        )
        output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run EduMind end-to-end demo flow checks and write a Markdown report.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Backend base URL.")
    parser.add_argument("--output", default="reports/demo_flow_check.md", help="Markdown report output path.")
    parser.add_argument("--timeout", type=int, default=12, help="HTTP timeout seconds.")
    args = parser.parse_args()

    checker = DemoFlowChecker(args.base_url, args.timeout)
    checker.run()
    output = Path(args.output)
    checker.write_report(output)
    passed = sum(1 for item in checker.steps if item.success)
    total = len(checker.steps)
    print(f"EduMind e2e demo flow check: {passed}/{total} passed")
    print(f"Report: {output.resolve()}")
    return 0 if passed == total and all(checker.event_summary().values()) else 1


if __name__ == "__main__":
    sys.exit(main())
