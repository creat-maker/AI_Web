from __future__ import annotations

from datetime import datetime
from typing import Any


DEMO_STUDENTS: list[dict[str, Any]] = [
    {
        "user_id": "demo-basic",
        "aliases": ["demo-student-liming", "demo-student-zhangsan", "basic", "基础薄弱型", "李明"],
        "student_name": "李明",
        "display_name": "李明｜基础薄弱 + 代码实操偏好型",
        "profile_type": "基础薄弱 + 代码实操偏好型",
        "major": "物联网工程技术",
        "course_id": 1,
        "course_name": "Python 程序设计",
        "current_level": "基础薄弱",
        "knowledge_level": "基础薄弱",
        "learning_goal": "补齐 Python 循环结构，完成课程作业和基础代码实操",
        "weak_points": ["while 循环", "循环嵌套", "break / continue"],
        "learning_style": "步骤化讲解、图解、基础例题",
        "learning_preference": "步骤化讲解、图解、基础例题",
        "mistake_pattern": "概念混淆、代码调试能力弱",
        "available_time": "每天 1 小时",
        "resource_preference": "基础讲义、知识点卡片、基础题",
        "risk_level": "高",
        "score": 58,
        "progress": 36,
        "resource_usage": 48,
        "recommended_strategy": "先用图解建立循环执行模型，再通过可运行 while 案例和分层练习巩固。",
        "evidence_items": [
            {
                "source_type": "dialog",
                "description": "对话中提到“函数不会写，参数和返回值经常分不清”，识别为 Python 函数薄弱。",
                "related_field": "weak_points",
                "confidence": 0.92,
            },
            {
                "source_type": "quiz",
                "description": "最近测评 while 死循环题正确率低于 60%，需要补齐循环变量更新和终止条件。",
                "related_field": "weak_points",
                "confidence": 0.88,
            },
            {
                "source_type": "learning",
                "description": "学习记录显示更常打开图解和知识点卡片，步骤化材料完成率更高。",
                "related_field": "learning_style",
                "confidence": 0.84,
            },
        ],
        "dialog_extraction": {
            "mode": "规则抽取",
            "raw_answer": "我正在学 Python 程序设计，循环结构有点弱，尤其是 while 循环和循环嵌套，我更喜欢代码案例和图解。",
            "extracted_fields": {
                "learning_goal": "补齐 Python 循环结构",
                "weak_points": ["while 循环", "循环嵌套", "break / continue"],
                "available_time": "每天 1 小时",
                "learning_style": "步骤化讲解、图解、基础例题",
            },
            "confidence": 0.89,
            "evidence_basis": "命中“while 循环”“循环嵌套”“代码案例”等关键词，并结合测评低分规则。",
        },
    },
    {
        "user_id": "demo-advanced",
        "aliases": ["advanced", "进阶提升型", "陈浩"],
        "student_name": "李同学",
        "display_name": "李同学｜项目提升型",
        "profile_type": "项目提升型",
        "major": "计算机类",
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
        "evidence_items": [
            {
                "source_type": "dialog",
                "description": "对话中明确学习目标是完成软件杯项目开发，适合项目实战路径。",
                "related_field": "learning_goal",
                "confidence": 0.94,
            },
            {
                "source_type": "tutor",
                "description": "问答记录多次出现 RAG、检索增强、接口联调和部署问题。",
                "related_field": "weak_points",
                "confidence": 0.87,
            },
            {
                "source_type": "learning",
                "description": "项目案例和接口文档点击率高，综合任务完成度优于基础讲义。",
                "related_field": "resource_preference",
                "confidence": 0.82,
            },
        ],
        "dialog_extraction": {
            "mode": "规则抽取",
            "raw_answer": "我基础还可以，想把软件杯项目做出来，主要卡在 RAG、后端接口和最后部署。",
            "extracted_fields": {
                "learning_goal": "完成软件杯项目开发",
                "weak_points": ["RAG", "后端工程化", "系统部署"],
                "knowledge_level": "基础较好",
                "learning_style": "案例驱动、项目实战",
            },
            "confidence": 0.91,
            "evidence_basis": "命中“软件杯项目”“RAG”“后端接口”“部署”等项目型关键词。",
        },
    },
    {
        "user_id": "demo-exam",
        "aliases": ["exam", "考试冲刺型", "王悦"],
        "student_name": "王同学",
        "display_name": "王同学｜考试冲刺型",
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
        "evidence_items": [
            {
                "source_type": "dialog",
                "description": "对话中提到期末考核压力大，希望快速复习高频考点。",
                "related_field": "learning_goal",
                "confidence": 0.9,
            },
            {
                "source_type": "quiz",
                "description": "章节测验显示概念辨析题波动较大，错题集中在高频考点。",
                "related_field": "mistake_pattern",
                "confidence": 0.86,
            },
            {
                "source_type": "学习记录",
                "description": "可用时间只有每天 45 分钟，更适合短周期复习清单和模拟题训练。",
                "related_field": "available_time",
                "confidence": 0.83,
            },
        ],
        "dialog_extraction": {
            "mode": "规则抽取",
            "raw_answer": "快期末了，我想冲刺课程考核，概念题经常混，做题时也容易审错题，每天只有 45 分钟。",
            "extracted_fields": {
                "learning_goal": "课程考核和期末冲刺",
                "weak_points": ["高频考点", "错题", "概念辨析"],
                "mistake_pattern": "概念混淆、审题不稳",
                "available_time": "每天 45 分钟",
            },
            "confidence": 0.88,
            "evidence_basis": "命中“期末”“概念题经常混”“审错题”“45 分钟”等考试冲刺关键词。",
        },
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
    evidence_items = raw.get("evidence_items") or base.get("evidence_items", [])
    dialog_extraction = raw.get("dialog_extraction") or base.get("dialog_extraction", {})
    return {
        "user_id": normalize_user_id(raw.get("user_id") or base["user_id"]),
        "student_name": raw.get("student_name") or base["student_name"],
        "display_name": raw.get("display_name") or base.get("display_name") or raw.get("student_name") or base["student_name"],
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
        "evidence_items": evidence_items,
        "dialog_extraction": dialog_extraction,
        "score": raw.get("score", base["score"]),
        "progress": raw.get("progress", base["progress"]),
        "resource_usage": raw.get("resource_usage", base["resource_usage"]),
    }


def get_demo_users() -> list[dict[str, Any]]:
    return [
        {
            "user_id": item["user_id"],
            "student_name": item["student_name"],
            "display_name": item["display_name"],
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
            _task("部署与工程化冲刺", ["后端工程化", "系统部署"], ["部署清单", "FastAPI 接口文档", "项目任务板"], ["整理环境变量", "补齐启动脚本和健康检查"], "2 小时", "本地前后端可启动，关键接口返回 200", "把项目从功能验证推进到可交付状态。", 120, "优先打通可运行链路，再补工程细节。", "推荐"),
        ]
    elif normalized["user_id"] == "demo-exam":
        tasks = [
            _task("高频考点速记", ["高频考点", "概念辨析"], ["高频考点清单", "概念辨析卡"], ["完成 20 分钟考点复盘", "标记 5 个易混概念"], "45 分钟", "考点自测正确率达到 80%", normalized["learning_goal"], 45, normalized["recommended_strategy"], "进行中"),
            _task("错题二刷与模拟题", ["错题", "审题"], ["错题集", "模拟题", "复习清单"], ["重做错题", "完成一组模拟题"], "45 分钟", "写出每道错题的主错因", "稳定期末冲刺得分。", 45, "先审题圈关键词，再选择知识点。", "推荐"),
        ]
    else:
        tasks = [
            _task("Python 函数基础补齐", ["Python 函数", "参数与返回值"], ["基础讲义", "函数知识点卡片"], ["阅读步骤化讲义", "完成 6 道基础函数题"], "1 小时", "能独立解释参数、返回值和调用顺序", normalized["learning_goal"], 60, normalized["recommended_strategy"], "进行中"),
            _task("break / continue 对比", ["break / continue", "while 循环"], ["控制语句对比卡", "输出结果判断题"], ["完成 6 道输出结果判断题", "解释每轮循环变化"], "30 分钟", "能区分跳出循环和跳过本轮循环", "补齐循环控制语句。", 60, "把每轮输出写在表格中。", "推荐"),
        ]
    for task in tasks:
        task["recommendation_reason"] = _recommendation_reason(
            normalized,
            "、".join(task["knowledge_points"][:3]),
            "、".join(task["resources"][:2]),
        )

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


def _recommendation_reason(profile: dict[str, Any], focus: str, resource_hint: str) -> str:
    weak_points = "、".join(str(item) for item in profile["weak_points"][:3])
    return (
        f"由于该学生 knowledge_level 为“{profile['knowledge_level']}”，weak_points 包含“{weak_points}”，"
        f"learning_style 偏好“{profile['learning_style']}”，因此本阶段聚焦“{focus}”，"
        f"优先推荐“{resource_hint}”。"
    )


def build_resource_pack(payload: dict[str, Any]) -> dict[str, Any]:
    profile = normalize_profile_schema(payload.get("profile"), payload.get("studentId") or payload.get("student_id") or payload.get("user_id"))
    weak_points = payload.get("knowledgePoints") or payload.get("knowledge_points") or payload.get("weakPoints") or payload.get("weak_points") or profile["weak_points"]
    if isinstance(weak_points, str):
        weak_points = [weak_points]
    reason = _recommendation_reason(profile, "、".join(str(item) for item in weak_points[:3]), profile["resource_preference"])
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
            ("基础讲义", "Python 循环结构基础讲义", "用步骤化讲解补齐 for 循环、while 循环和 break / continue 概念。", "基础"),
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
        "mode": "profile-aware",
        "profile": profile,
        "auditFlow": ["ResourceAgent 生成", "AuditAgent 初审", "管理员复核", "发布到学生端"],
    }


# Final Python loop learning profile definitions. They intentionally appear last so
# older profile snippets above remain harmless while public function names stay stable.
DEMO_STUDENTS = [
    {
        "user_id": "demo-basic",
        "aliases": ["demo-student-liming", "demo-student-zhangsan", "basic", "基础薄弱型", "李明"],
        "student_name": "李明",
        "display_name": "李明｜基础薄弱 + 代码实操偏好型",
        "profile_type": "基础薄弱 + 代码实操偏好型",
        "major": "计算机类",
        "course_id": 1,
        "course_name": "Python 程序设计",
        "current_level": "基础薄弱",
        "knowledge_level": "基础薄弱",
        "learning_goal": "完成课程作业和基础项目，重点补齐循环结构。",
        "weak_points": ["while 循环", "循环嵌套", "break / continue"],
        "learning_style": "代码案例 + 图解",
        "learning_preference": "代码案例 + 图解",
        "mistake_pattern": "循环条件更新遗漏、嵌套循环变量混用、break / continue 使用场景混淆",
        "available_time": "每天 30 分钟",
        "resource_preference": "代码实操案例、变量变化图解、分层练习题",
        "risk_level": "需巩固",
        "score": 62,
        "progress": 46,
        "resource_usage": 58,
        "recommended_strategy": "先用图解建立循环执行模型，再通过可运行 while 案例和分层练习巩固。",
        "evidence_items": [
            {"source_type": "自然语言对话", "description": "学生明确表示 while 循环和循环嵌套薄弱，偏好代码案例和图解。", "related_field": "weak_points", "confidence": 0.94},
            {"source_type": "测验结果", "description": "最近测验中 while 死循环和循环变量更新题错误率较高。", "related_field": "risk_level", "confidence": 0.88},
            {"source_type": "AI 问答记录", "description": "求助问题集中在循环条件更新、循环嵌套和 break / continue。", "related_field": "mistake_pattern", "confidence": 0.86},
        ],
        "dialog_extraction": {
            "mode": "规则抽取",
            "raw_answer": "我正在学 Python 程序设计，循环结构有点弱，尤其是 while 循环和循环嵌套，我更喜欢代码案例和图解，想尽快完成课程作业。",
            "extracted_fields": {
                "learning_goal": "完成课程作业和基础项目",
                "weak_points": ["while 循环", "循环嵌套", "break / continue"],
                "learning_style": "代码案例 + 图解",
                "risk_level": "需巩固",
            },
            "confidence": 0.9,
            "evidence_basis": "自然语言对话 + 学习历史 + 测验结果 + AI 问答记录",
        },
    },
    {
        "user_id": "demo-advanced",
        "aliases": ["advanced", "进阶提升型", "陈浩"],
        "student_name": "陈浩",
        "display_name": "陈浩｜项目实践提升型",
        "profile_type": "项目实践提升型",
        "major": "计算机类",
        "course_id": 1,
        "course_name": "Python 程序设计",
        "current_level": "中等偏上",
        "knowledge_level": "中等偏上",
        "learning_goal": "用循环、列表和函数完成基础项目拓展。",
        "weak_points": ["循环与列表综合", "函数封装", "代码健壮性"],
        "learning_style": "项目实践 + 代码复盘",
        "learning_preference": "项目案例、代码评审清单、拓展任务",
        "mistake_pattern": "代码拆分不足、边界条件考虑不全",
        "available_time": "每天 45 分钟",
        "resource_preference": "项目任务书、可运行案例、代码检查清单",
        "risk_level": "学习状态：稳定",
        "score": 84,
        "progress": 72,
        "resource_usage": 78,
        "recommended_strategy": "用项目拓展任务串联循环、列表和函数封装。",
    },
    {
        "user_id": "demo-exam",
        "aliases": ["exam", "考试冲刺型", "王悦"],
        "student_name": "王悦",
        "display_name": "王悦｜考试冲刺型",
        "profile_type": "考试冲刺型",
        "major": "计算机类",
        "course_id": 1,
        "course_name": "Python 程序设计",
        "current_level": "中等但不稳定",
        "knowledge_level": "中等但不稳定",
        "learning_goal": "围绕循环结构高频考点进行错题二刷。",
        "weak_points": ["for / while 对比", "break / continue", "循环边界"],
        "learning_style": "错题解析 + 高频考点清单",
        "learning_preference": "模拟题、错题卡、速查表",
        "mistake_pattern": "审题不稳、循环次数估计不准",
        "available_time": "每天 40 分钟",
        "resource_preference": "错题集、考点清单、变量变化表",
        "risk_level": "需关注",
        "score": 74,
        "progress": 61,
        "resource_usage": 66,
        "recommended_strategy": "先做诊断测验定位错因，再按 while 循环和 break / continue 刷题。",
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
    learning_style = raw.get("learning_style") or raw.get("learning_preference") or base["learning_style"]
    current_level = raw.get("current_level") or raw.get("knowledge_level") or base["current_level"]
    return {
        "user_id": normalize_user_id(raw.get("user_id") or base["user_id"]),
        "student_name": raw.get("student_name") or base["student_name"],
        "display_name": raw.get("display_name") or base["display_name"],
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
        "change_log": raw.get("change_log") or [],
        "evidence_items": raw.get("evidence_items") or base.get("evidence_items", []),
        "dialog_extraction": raw.get("dialog_extraction") or base.get("dialog_extraction", {}),
        "score": raw.get("score", base["score"]),
        "progress": raw.get("progress", base["progress"]),
        "resource_usage": raw.get("resource_usage", base["resource_usage"]),
    }


def get_demo_users() -> list[dict[str, Any]]:
    return [
        {
            "user_id": item["user_id"],
            "student_name": item["student_name"],
            "display_name": item["display_name"],
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


def build_learning_tasks(user_id: str | int | None = None, profile_type: str | None = None, profile: dict[str, Any] | None = None) -> dict[str, Any]:
    normalized = normalize_profile_schema(profile, user_id or profile_type)
    tasks = [
        {
            "title": "诊断补弱",
            "stage_name": "诊断补弱",
            "goal": "定位 while 死循环、循环嵌套和 break / continue 的主要错因。",
            "knowledge_points": ["while 循环", "循环嵌套"],
            "prerequisites": ["变量与条件表达式"],
            "mastery": "46%",
            "resources": ["循环结构诊断卷", "变量变化表模板"],
            "practice": "完成 6 道循环边界题。",
            "completion_rule": "正确率达到 80%。",
            "estimated_minutes": 20,
            "ai_suggestion": "先手写前三轮变量变化，再运行代码验证。",
            "recommendation_reason": "最近测验中 while 死循环问题错误率较高。",
            "status": "进行中",
        },
        {
            "title": "核心概念学习",
            "stage_name": "核心概念学习",
            "goal": "理解 for、while、range、break 和 continue 的适用场景。",
            "knowledge_points": ["for 循环", "while 循环", "range 函数", "break / continue"],
            "prerequisites": ["if 条件判断"],
            "mastery": "52%",
            "resources": ["for / while 对比讲义", "break / continue 速查卡"],
            "practice": "改写 3 段循环代码。",
            "completion_rule": "能解释循环次数和退出条件。",
            "estimated_minutes": 25,
            "ai_suggestion": "用流程图区分遍历型循环和条件型循环。",
            "recommendation_reason": "AI 求助集中在循环条件更新和循环嵌套。",
            "status": "推荐",
        },
        {
            "title": "案例实操",
            "stage_name": "案例实操",
            "goal": "完成九九乘法表、猜数字和列表统计三个代码案例。",
            "knowledge_points": ["循环嵌套", "while 循环", "break / continue"],
            "prerequisites": ["核心概念学习"],
            "mastery": "40%",
            "resources": ["Python 代码实操案例包"],
            "practice": "提交 3 个可运行脚本。",
            "completion_rule": "代码通过边界用例。",
            "estimated_minutes": 35,
            "ai_suggestion": "每个案例先写最小可运行版本。",
            "recommendation_reason": "学生偏好代码案例和图解资源。",
            "status": "未开始",
        },
        {
            "title": "练习测评",
            "stage_name": "练习测评",
            "goal": "通过分层练习检查循环结构掌握情况。",
            "knowledge_points": ["for 循环", "while 循环", "循环嵌套"],
            "prerequisites": ["案例实操"],
            "mastery": "待测",
            "resources": ["分层练习题"],
            "practice": "完成基础、变式、综合题各 3 道。",
            "completion_rule": "正确率达到 85%。",
            "estimated_minutes": 30,
            "ai_suggestion": "错题必须标注主错因。",
            "recommendation_reason": "形成性评价需要验证补弱效果。",
            "status": "未开始",
        },
        {
            "title": "项目拓展",
            "stage_name": "项目拓展",
            "goal": "用循环完成课程作业和基础项目。",
            "knowledge_points": ["循环结构综合应用"],
            "prerequisites": ["练习测评"],
            "mastery": "待开始",
            "resources": ["课程作业项目任务书"],
            "practice": "完成一个列表统计小项目。",
            "completion_rule": "提交运行截图和代码说明。",
            "estimated_minutes": 45,
            "ai_suggestion": "把需求拆为输入、循环处理、输出三段。",
            "recommendation_reason": "对齐完成课程作业和基础项目的学习目标。",
            "status": "未开始",
        },
    ]
    return {
        "student_id": normalized["user_id"],
        "student_name": normalized["student_name"],
        "course_name": "Python 程序设计",
        "active_profile_type": normalized["profile_type"],
        "profile": normalized,
        "paths": [
            {
                "profile_type": "李明的 Python 循环结构专项补弱路径",
                "summary": "李明的 Python 循环结构专项补弱路径。",
                "ai_recommendation": normalized["recommended_strategy"],
                "update_reasons": [
                    "最近测验中 while 死循环问题错误率较高",
                    "AI 求助集中在循环条件更新和循环嵌套",
                    "学生偏好代码案例和图解资源",
                ],
                "tasks": tasks,
            }
        ],
    }


def build_resource_pack(payload: dict[str, Any]) -> dict[str, Any]:
    profile = normalize_profile_schema(payload.get("profile"), payload.get("studentId") or payload.get("student_id") or payload.get("user_id"))
    weak_points = payload.get("knowledgePoints") or payload.get("knowledge_points") or payload.get("weakPoints") or payload.get("weak_points") or ["while 循环", "循环嵌套", "break / continue"]
    if isinstance(weak_points, str):
        weak_points = [weak_points]
    reason = "匹配李明基础薄弱、偏好代码案例和图解的画像，并聚焦循环结构薄弱点。"
    specs = [
        ("讲解文档", "循环结构讲解文档", "解释 if 条件、for、while、range、break、continue 和循环嵌套。", "基础"),
        ("思维导图", "for / while 知识点思维导图", "用文字导图呈现遍历型循环、条件型循环和循环控制。", "基础"),
        ("分层练习题", "循环结构分层练习题", "基础题、变式题、综合题，每题带错因标签。", "中等"),
        ("拓展阅读", "循环结构拓展阅读材料", "补充循环不变量、边界条件和调试方法。", "中等"),
        ("代码实操案例", "Python while 循环代码实操案例", "提供猜数字、计数器和输入校验案例。", "基础"),
        ("PPT / 课件大纲", "循环结构课堂讲解课件大纲", "包含导入、概念、案例、练习和总结。", "基础"),
        ("视频 / 动画脚本", "多模态教学视频 / 动画脚本", "以变量变化动画讲解 while 循环终止条件。", "基础"),
    ]
    resources = [
        {
            "resourceType": kind,
            "resource_type": kind,
            "title": title,
            "content": content,
            "sourceAgent": "多类型资源生成 Agent",
            "source_agent": "多类型资源生成 Agent",
            "adaptedProfile": "循环结构需巩固，偏好代码实操",
            "reason": reason,
            "recommendation_reason": reason,
            "recommend_reason": reason,
            "relatedKnowledgePoints": weak_points[:3],
            "difficulty": difficulty,
            "reviewStatus": "通过",
            "displayReviewStatus": "通过",
            "libraryStatus": "待加入",
            "pushStatus": "待推送",
            "suitableLearner": "李明：循环结构需巩固，偏好代码实操",
            "references": ["Python 程序设计课程知识库 / 循环结构章节"],
            "estimatedMinutes": 15 + index * 5,
        }
        for index, (kind, title, content, difficulty) in enumerate(specs)
    ]
    return {
        "studentId": profile["user_id"],
        "studentName": "李明",
        "profileType": "基础薄弱 + 代码实操偏好型",
        "courseId": payload.get("courseId") or payload.get("course_id") or "python-programming",
        "courseName": "Python 程序设计",
        "chapter": "循环结构",
        "studentLevel": "基础薄弱",
        "learningGoal": payload.get("learningGoal") or "完成课程作业和基础项目",
        "weakPoints": weak_points,
        "packageTitle": "Python 循环结构个性化补弱资源包",
        "resources": resources,
        "resourceCount": len(resources),
        "mode": "profile-aware",
        "auditFlow": ["生成", "审核", "入库", "推荐", "学习反馈"],
    }
