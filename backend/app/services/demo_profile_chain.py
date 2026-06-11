from __future__ import annotations

from datetime import datetime
from typing import Any


DEMO_STUDENTS: list[dict[str, Any]] = [
    {
        "user_id": "demo-basic",
        "aliases": ["demo-student-zhangsan", "basic", "基础薄弱型", "张三"],
        "student_name": "张三",
        "profile_type": "基础薄弱型",
        "major": "物联网工程技术",
        "course_id": 1,
        "course_name": "Python 程序设计",
        "current_level": "基础薄弱",
        "knowledge_level": "基础薄弱",
        "learning_goal": "补齐 Python 和数据库基础",
        "weak_points": ["Python 函数", "SQL 查询", "接口基础"],
        "learning_style": "步骤化讲解、图解、基础例题",
        "learning_preference": "步骤化讲解、图解、基础例题",
        "mistake_pattern": "概念混淆、代码调试能力弱",
        "available_time": "每天 1 小时",
        "resource_preference": "基础讲义、知识点卡片、基础题",
        "risk_level": "高",
        "score": 58,
        "progress": 36,
        "resource_usage": 48,
        "recommended_strategy": "先用图解和知识点卡片补概念，再用基础题巩固 Python 函数、SQL 查询和接口基础。",
    },
    {
        "user_id": "demo-advanced",
        "aliases": ["advanced", "进阶提升型", "李四"],
        "student_name": "李四",
        "profile_type": "进阶提升型",
        "major": "计算机/人工智能相关方向",
        "course_id": 1,
        "course_name": "软件杯项目开发",
        "current_level": "基础较好",
        "knowledge_level": "基础较好",
        "learning_goal": "完成软件杯项目开发",
        "weak_points": ["RAG", "后端工程化", "系统部署"],
        "learning_style": "案例驱动、项目实战",
        "learning_preference": "案例驱动、项目实战",
        "mistake_pattern": "工程整合不熟、部署经验不足",
        "available_time": "每天 2 小时",
        "resource_preference": "项目案例、接口文档、实战任务",
        "risk_level": "中",
        "score": 84,
        "progress": 72,
        "resource_usage": 78,
        "recommended_strategy": "以项目案例和接口文档为主线，把 RAG、后端工程化和部署串成可交付任务。",
    },
    {
        "user_id": "demo-exam",
        "aliases": ["exam", "考试冲刺型", "王五"],
        "student_name": "王五",
        "profile_type": "考试冲刺型",
        "major": "电子信息/计算机方向",
        "course_id": 1,
        "course_name": "课程考核复习",
        "current_level": "中等但不稳定",
        "knowledge_level": "中等但不稳定",
        "learning_goal": "课程考核和期末冲刺",
        "weak_points": ["高频考点", "错题", "概念辨析"],
        "learning_style": "考点总结、题目训练",
        "learning_preference": "考点总结、题目训练",
        "mistake_pattern": "概念混淆、审题不稳",
        "available_time": "每天 45 分钟",
        "resource_preference": "模拟题、错题集、复习清单",
        "risk_level": "中",
        "score": 72,
        "progress": 61,
        "resource_usage": 66,
        "recommended_strategy": "按高频考点建立复习清单，用模拟题和错题训练稳定概念辨析与审题过程。",
    },
]


def normalize_user_id(user_id: str | int | None = None) -> str:
    value = str(user_id or "demo-basic").strip()
    for student in DEMO_STUDENTS:
        if value == student["user_id"] or value in student.get("aliases", []):
            return student["user_id"]
    return "demo-basic"


def get_demo_student(user_id: str | int | None = None) -> dict[str, Any]:
    normalized = normalize_user_id(user_id)
    return next(item for item in DEMO_STUDENTS if item["user_id"] == normalized)


def normalize_profile_schema(profile: dict[str, Any] | None = None, user_id: str | int | None = None) -> dict[str, Any]:
    base = get_demo_student(user_id or (profile or {}).get("user_id"))
    raw = {**base, **(profile or {})}
    weak_points = raw.get("weak_points") or base["weak_points"]
    if isinstance(weak_points, str):
        weak_points = [item.strip() for item in weak_points.split(",") if item.strip()]
    change_log = raw.get("change_log") or []
    if isinstance(change_log, str):
        change_log = [change_log]
    learning_style = raw.get("learning_style") or raw.get("learning_preference") or base["learning_style"]
    current_level = raw.get("current_level") or raw.get("knowledge_level") or base["current_level"]
    return {
        "user_id": normalize_user_id(raw.get("user_id") or base["user_id"]),
        "student_name": raw.get("student_name") or base["student_name"],
        "profile_type": raw.get("profile_type") or base["profile_type"],
        "major": raw.get("major") or base["major"],
        "course_id": raw.get("course_id") or base["course_id"],
        "course_name": raw.get("course_name") or base["course_name"],
        "learning_goal": raw.get("learning_goal") or base["learning_goal"],
        "knowledge_level": raw.get("knowledge_level") or current_level,
        "current_level": current_level,
        "weak_points": weak_points,
        "learning_style": learning_style,
        "learning_preference": learning_style,
        "mistake_pattern": raw.get("mistake_pattern") or base["mistake_pattern"],
        "available_time": raw.get("available_time") or base["available_time"],
        "resource_preference": raw.get("resource_preference") or base["resource_preference"],
        "risk_level": raw.get("risk_level") or base["risk_level"],
        "recommended_strategy": raw.get("recommended_strategy") or base["recommended_strategy"],
        "updated_at": raw.get("updated_at") or datetime.utcnow().isoformat(),
        "change_log": change_log,
        "score": raw.get("score", base["score"]),
        "progress": raw.get("progress", base["progress"]),
        "resource_usage": raw.get("resource_usage", base["resource_usage"]),
    }


def get_demo_users() -> list[dict[str, Any]]:
    return [
        {
            "user_id": item["user_id"],
            "student_name": item["student_name"],
            "profile_type": item["profile_type"],
            "major": item["major"],
            "current_level": item["current_level"],
            "learning_goal": item["learning_goal"],
            "weak_points": item["weak_points"],
            "risk_level": item["risk_level"],
            "score": item["score"],
        }
        for item in DEMO_STUDENTS
    ]


def demo_profile_to_api(student: dict[str, Any]) -> dict[str, Any]:
    profile_json = normalize_profile_schema(student, student["user_id"])
    return {
        "id": abs(hash(student["user_id"])) % 10000 + 1000,
        **profile_json,
        "profile_json": profile_json,
        "created_at": None,
        "updated_at": profile_json["updated_at"],
    }


def get_demo_profiles(user_id: str | int | None = None) -> list[dict[str, Any]]:
    if user_id:
        return [demo_profile_to_api(get_demo_student(user_id))]
    return [demo_profile_to_api(item) for item in DEMO_STUDENTS]


def build_learning_tasks(
    user_id: str | int | None = None,
    profile_type: str | None = None,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = normalize_profile_schema(profile, user_id or profile_type)
    if normalized["user_id"] == "demo-advanced":
        tasks = [
            _task("RAG 项目链路拆解", ["RAG", "向量检索", "提示词编排"], ["RAG 项目案例", "检索接口文档"], ["复现一个课程资料问答接口", "记录检索、生成、引用三个日志点"], "2 小时", "接口返回引用来源且能回答 3 个项目问题", normalized["learning_goal"], 120, normalized["recommended_strategy"], "进行中"),
            _task("部署与工程化冲刺", ["后端工程化", "系统部署"], ["部署清单", "FastAPI 接口文档", "项目任务板"], ["整理环境变量", "补齐启动脚本和健康检查"], "2 小时", "本地前后端可启动，关键接口返回 200", "把项目从功能演示推进到可交付状态。", 120, "优先打通可运行链路，再补工程细节。", "推荐"),
        ]
    elif normalized["user_id"] == "demo-exam":
        tasks = [
            _task("高频考点速记", ["高频考点", "概念辨析"], ["高频考点清单", "概念辨析卡"], ["完成 20 分钟考点复盘", "标记 5 个易混概念"], "45 分钟", "考点自测正确率达到 80%", normalized["learning_goal"], 45, normalized["recommended_strategy"], "进行中"),
            _task("错题二刷与模拟题", ["错题", "审题"], ["错题集", "模拟题", "复习清单"], ["重做错题", "完成一组模拟题"], "45 分钟", "写出每道错题的主错因", "稳定期末冲刺得分。", 45, "先审题圈关键词，再选择知识点。", "推荐"),
        ]
    else:
        tasks = [
            _task("Python 函数基础补齐", ["Python 函数", "参数与返回值"], ["基础讲义", "函数知识点卡片"], ["阅读步骤化讲义", "完成 6 道基础函数题"], "1 小时", "能独立解释参数、返回值和调用顺序", normalized["learning_goal"], 60, normalized["recommended_strategy"], "进行中"),
            _task("SQL 与接口入门", ["SQL 查询", "接口基础"], ["SQL 知识点卡片", "接口图解"], ["完成 SELECT/WHERE 基础题", "画出一次请求响应流程"], "1 小时", "能写出基础查询并说明接口输入输出", "补齐数据库和接口基础。", 60, "用图解先理解流程，再写最小例题。", "推荐"),
        ]
    return {
        "student_id": normalized["user_id"],
        "student_name": normalized["student_name"],
        "course_name": normalized["course_name"],
        "active_profile_type": normalized["profile_type"],
        "profile": normalized,
        "paths": [
            {
                "profile_type": normalized["profile_type"],
                "summary": f"{normalized['profile_type']}路径：{normalized['recommended_strategy']}",
                "ai_recommendation": normalized["recommended_strategy"],
                "tasks": tasks,
            }
        ],
    }


def _task(
    stage_name: str,
    knowledge_points: list[str],
    resources: list[str],
    tasks: list[str],
    estimated_time: str,
    check_method: str,
    goal: str,
    estimated_minutes: int,
    suggestion: str,
    status: str,
) -> dict[str, Any]:
    return {
        "stage_name": stage_name,
        "knowledge_points": knowledge_points,
        "resources": resources,
        "tasks": tasks,
        "estimated_time": estimated_time,
        "check_method": check_method,
        "title": stage_name,
        "goal": goal,
        "practice": "；".join(tasks),
        "completion_rule": check_method,
        "estimated_minutes": estimated_minutes,
        "ai_suggestion": suggestion,
        "status": status,
    }


def build_resource_pack(payload: dict[str, Any]) -> dict[str, Any]:
    profile = normalize_profile_schema(payload.get("profile"), payload.get("studentId") or payload.get("student_id") or payload.get("user_id"))
    weak_points = payload.get("knowledgePoints") or payload.get("knowledge_points") or payload.get("weakPoints") or payload.get("weak_points") or profile["weak_points"]
    if isinstance(weak_points, str):
        weak_points = [weak_points]
    reason = (
        f"依据画像类型「{profile['profile_type']}」、薄弱点「{'、'.join(weak_points[:3])}」、"
        f"学习风格「{profile['learning_style']}」和资源偏好「{profile['resource_preference']}」推荐。"
    )
    if profile["user_id"] == "demo-advanced":
        specs = [
            ("项目案例", "RAG 课程问答项目案例", "拆解检索、生成、引用和日志记录的完整项目流程。", "进阶"),
            ("接口文档", "后端接口联调文档", "列出画像、路径、资源、问答接口的请求参数和返回字段。", "中等"),
            ("综合任务", "软件杯项目集成任务", "把 RAG、后端工程化和部署检查串成一次可验收任务。", "进阶"),
        ]
    elif profile["user_id"] == "demo-exam":
        specs = [
            ("高频考点", "期末高频考点清单", "按概念辨析、常见题型和易错关键词组织复习。", "基础"),
            ("模拟题", "45 分钟模拟训练", "覆盖高频考点、错题变式和审题陷阱。", "中等"),
            ("错题训练", "错题二刷与原因标签", "要求每题写出主错因和防错规则。", "中等"),
        ]
    else:
        specs = [
            ("基础讲义", "Python 函数与 SQL 查询基础讲义", "用步骤化讲解补齐函数、SQL 和接口基础概念。", "基础"),
            ("知识点卡片", "接口基础图解卡片", "用图解说明请求、响应、参数和返回值。", "基础"),
            ("基础题", "Python/SQL 基础题 10 题", "用低门槛题目检查概念是否真正掌握。", "基础"),
        ]
    resources = [
        {
            "resourceType": kind,
            "resource_type": kind,
            "title": title,
            "content": content,
            "reason": reason,
            "recommendation_reason": reason,
            "recommend_reason": reason,
            "relatedKnowledgePoints": weak_points[:3],
            "difficulty": difficulty,
            "estimatedMinutes": 20 + index * 10,
        }
        for index, (kind, title, content, difficulty) in enumerate(specs)
    ]
    return {
        "studentId": profile["user_id"],
        "studentName": profile["student_name"],
        "profileType": profile["profile_type"],
        "courseId": payload.get("courseId") or payload.get("course_id") or profile["course_id"],
        "courseName": payload.get("courseName") or payload.get("course_name") or profile["course_name"],
        "studentLevel": profile["current_level"],
        "learningGoal": profile["learning_goal"],
        "weakPoints": weak_points,
        "packageTitle": f"{profile['student_name']}的{profile['course_name']}个性化资源包",
        "resources": resources,
        "resourceCount": len(resources),
        "mode": "profile-aware-demo",
        "profile": profile,
        "auditFlow": ["ResourceAgent 生成", "AuditAgent 初审", "管理员复核", "发布到学生端"],
    }
