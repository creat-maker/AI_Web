from __future__ import annotations

from datetime import datetime
from typing import Any

from app.services import demo_profile_chain


DEMO_STUDENTS: list[dict[str, Any]] = [
    {
        "user_id": "demo-basic",
        "aliases": ["demo-student-liming", "demo-student-zhangsan", "student-li-ming", "basic", "李明"],
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
    },
    {
        "user_id": "demo-advanced",
        "aliases": ["advanced", "陈浩"],
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
        "aliases": ["exam", "王悦"],
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


def normalize_profile_schema(profile: dict[str, Any] | None = None, user_id: str | int | None = None) -> dict[str, Any]:
    return demo_profile_chain.normalize_profile_schema(profile, user_id)


def demo_profile_to_api(student: dict[str, Any]) -> dict[str, Any]:
    return demo_profile_chain.demo_profile_to_api(student)


def get_demo_profiles(user_id: str | int | None = None) -> list[dict[str, Any]]:
    return demo_profile_chain.get_demo_profiles(user_id)


def build_learning_tasks(
    user_id: str | int | None = None,
    profile_type: str | None = None,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return demo_profile_chain.build_learning_tasks(user_id=user_id, profile_type=profile_type, profile=profile)


def build_resource_pack(payload: dict[str, Any]) -> dict[str, Any]:
    return demo_profile_chain.build_resource_pack(payload)


def build_agent_steps(user_id: str | int | None = None) -> list[dict[str, Any]]:
    student = get_demo_student(user_id)
    weak_points = "、".join(student["weak_points"][:3])
    names = [
        ("profile_agent", "画像构建 Agent", "自然语言对话、学习历史、测验结果", f"识别{student['student_name']}的画像：{student['profile_type']}，薄弱点：{weak_points}", "规则抽取器、画像模板"),
        ("knowledge_agent", "知识检索 Agent", f"课程={student['course_name']}，章节=循环结构", "召回 while 循环、循环嵌套、break / continue 证据", "轻量 RAG、课程知识库"),
        ("path_agent", "学习路径规划 Agent", "画像 + 薄弱知识点 + 引用证据", "生成 5 阶段专项补弱路径", "路径规划规则"),
        ("resource_plan_agent", "资源生成规划 Agent", "学习目标、资源偏好、知识点", "规划 9 类资源包", "资源模板库"),
        ("resource_agent", "多类型资源生成 Agent", "资源规划和引用依据", "生成讲义、导图、练习、HTML 动画、视频脚本、TTS、MP4、代码案例和项目任务", "资源模板与课程知识库"),
        ("rag_agent", "RAG 答疑 Agent", "问题：为什么 while 循环会死循环", "返回带引用、置信度和下一步路径的答疑", "轻量检索、答疑卡片"),
        ("evaluation_agent", "学习效果评估 Agent", "测验结果、错题知识点、资源使用", "形成 Python 循环结构形成性评价", "评价量表"),
        ("audit_agent", "内容安全与防幻觉审核 Agent", "资源包、AI 回答、引用依据", "输出通过/需修改/人工复核/风险拦截", "审核规则"),
        ("report_agent", "报告生成 Agent", "画像、路径、资源、测评、审核结果", "生成学生报告和教师干预建议", "报告模板"),
    ]
    return [
        {
            "key": key,
            "name": name,
            "input_summary": input_summary,
            "tool_summary": tool,
            "output_summary": output_summary,
            "evidence": "Python 程序设计课程知识库 / 循环结构章节",
            "duration_ms": 180 + index * 70,
            "duration": f"{180 + index * 70}ms",
            "status": "success",
        }
        for index, (key, name, input_summary, output_summary, tool) in enumerate(names)
    ]


def build_teacher_analysis() -> dict[str, Any]:
    weak_counter: dict[str, int] = {}
    for student in DEMO_STUDENTS:
        for point in student["weak_points"]:
            weak_counter[point] = weak_counter.get(point, 0) + 1
    weak_ranking = [
        {"name": name, "value": 30 + count * 18, "student_count": count}
        for name, count in sorted(weak_counter.items(), key=lambda item: item[1], reverse=True)
    ][:6]
    return {
        "class_profile_distribution": [
            {"name": item["profile_type"], "value": 1, "student_name": item["student_name"]}
            for item in DEMO_STUDENTS
        ],
        "weak_point_ranking": weak_ranking,
        "warning_students": [
            {
                "user_id": item["user_id"],
                "student_name": item["student_name"],
                "profile_type": item["profile_type"],
                "risk_level": item["risk_level"],
                "weak_points": item["weak_points"][:3],
                "suggestion": item["recommended_strategy"],
            }
            for item in DEMO_STUDENTS
            if item["risk_level"] != "学习状态：稳定"
        ],
        "resource_usage": [
            {
                "student_name": item["student_name"],
                "profile_type": item["profile_type"],
                "usage_rate": item["resource_usage"],
                "recommended_count": 9,
                "completed_count": max(1, round(item["resource_usage"] / 20)),
            }
            for item in DEMO_STUDENTS
        ],
    }


def build_content_review_items() -> dict[str, Any]:
    now = datetime.utcnow().isoformat(timespec="seconds")
    return {
        "items": [
            {
                "id": "cr-demo-001",
                "title": "Python 循环结构个性化补弱资源包",
                "resource_type": "AI 个性化资源包",
                "source": "多类型资源生成 Agent -> 内容安全与防幻觉审核 Agent",
                "risk_tags": ["事实准确性", "知识点匹配度", "难度匹配度", "引用依据完整性", "敏感违规内容", "建议人工复核"],
                "status": "已通过",
                "review_opinion": "引用依据为 Python 程序设计课程知识库 / 循环结构章节，可发布给李明。",
                "student_name": "李明",
                "profile_type": "基础薄弱 + 代码实操偏好型",
                "createdAt": now,
                "audit_flow": ["生成", "审核", "绑定知识点", "入库", "推荐给学生", "使用反馈"],
            },
            {
                "id": "cr-demo-002",
                "title": "while 死循环 AI 学伴回答",
                "resource_type": "AI 学伴回答",
                "source": "RAG 答疑 Agent -> 内容安全与防幻觉审核 Agent",
                "risk_tags": ["引用依据完整性", "低依据风险"],
                "status": "待审核",
                "review_opinion": "需教师确认示例代码与课堂讲解口径一致。",
                "student_name": "李明",
                "profile_type": "基础薄弱 + 代码实操偏好型",
                "createdAt": now,
                "audit_flow": ["生成", "审核", "教师复核", "发布"],
            },
        ],
        "policy": "所有 AI 回答或资源生成内容都显示引用依据：Python 程序设计课程知识库 / 循环结构章节。",
    }
