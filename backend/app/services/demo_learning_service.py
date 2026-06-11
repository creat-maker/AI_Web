from __future__ import annotations

from typing import Any


DEMO_STUDENTS: list[dict[str, Any]] = [
    {
        "user_id": "demo-basic",
        "aliases": ["demo-student-zhangsan", "basic", "基础薄弱型", "张三"],
        "student_name": "张三",
        "profile_type": "基础薄弱型",
        "course_id": 1,
        "course_name": "Python 程序设计",
        "current_level": "基础薄弱",
        "learning_goal": "两周内补齐 Python 循环、函数和文件操作基础，能独立完成小练习。",
        "learning_preference": "短讲义 + 可运行案例 + 分层练习",
        "weak_points": ["循环边界", "函数参数与返回值", "文件读写", "异常处理"],
        "risk_level": "高风险",
        "score": 62,
        "progress": 38,
        "resource_usage": 52,
        "recommended_strategy": "先补概念和最小案例，再用 10 分钟练习形成正反馈。",
    },
    {
        "user_id": "demo-advanced",
        "aliases": ["advanced", "进阶提升型", "李四"],
        "student_name": "李四",
        "profile_type": "进阶提升型",
        "course_id": 1,
        "course_name": "Python 程序设计",
        "current_level": "中等偏上",
        "learning_goal": "把列表、字典、文件和异常处理串成项目能力，完成可展示小项目。",
        "learning_preference": "项目实践 + 代码案例 + 复盘清单",
        "weak_points": ["工程封装", "数据结构选择", "代码健壮性"],
        "risk_level": "稳定",
        "score": 84,
        "progress": 72,
        "resource_usage": 78,
        "recommended_strategy": "用项目任务替代单点刷题，重点强化迁移应用和代码质量。",
    },
    {
        "user_id": "demo-exam",
        "aliases": ["exam", "考试冲刺型", "王五"],
        "student_name": "王五",
        "profile_type": "考试冲刺型",
        "course_id": 1,
        "course_name": "Python 程序设计",
        "current_level": "中等",
        "learning_goal": "围绕章节高频考点进行错题二刷，期末测验达到 85 分以上。",
        "learning_preference": "诊断测验 + 错题卡 + 高频考点清单",
        "weak_points": ["递归分析", "文件操作选择题", "循环复杂度", "异常处理"],
        "risk_level": "需关注",
        "score": 74,
        "progress": 61,
        "resource_usage": 66,
        "recommended_strategy": "先做诊断测验定位错因，再按薄弱点刷题和生成错题复盘卡。",
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
    for student in DEMO_STUDENTS:
        if student["user_id"] == normalized:
            return student
    return DEMO_STUDENTS[0]


def get_demo_users() -> list[dict[str, Any]]:
    return [
        {
            "user_id": item["user_id"],
            "student_name": item["student_name"],
            "profile_type": item["profile_type"],
            "current_level": item["current_level"],
            "learning_goal": item["learning_goal"],
            "weak_points": item["weak_points"],
            "risk_level": item["risk_level"],
            "score": item["score"],
        }
        for item in DEMO_STUDENTS
    ]


def demo_profile_to_api(student: dict[str, Any]) -> dict[str, Any]:
    profile_json = {
        "user_id": student["user_id"],
        "profile_type": student["profile_type"],
        "diagnosis": f"{student['student_name']}属于{student['profile_type']}，主要薄弱点集中在{'、'.join(student['weak_points'][:3])}。",
        "risk_level": student["risk_level"],
        "score": student["score"],
        "progress": student["progress"],
        "resource_usage": student["resource_usage"],
        "recommended_strategy": student["recommended_strategy"],
        "weak_points": student["weak_points"],
    }


# Stable demo learning profiles used by the user-context/profile/path/resource chain.
# These definitions intentionally override older competition demo snippets above
# without changing their public function names or requiring a database migration.
DEMO_STUDENTS = [
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


def _now_iso() -> str:
    from datetime import datetime

    return datetime.utcnow().isoformat()


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
        "updated_at": raw.get("updated_at") or _now_iso(),
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
            {
                "stage_name": "RAG 项目链路拆解",
                "knowledge_points": ["RAG", "向量检索", "提示词编排"],
                "resources": ["RAG 项目案例", "检索接口文档"],
                "tasks": ["复现一个课程资料问答接口", "记录检索、生成、引用三个日志点"],
                "estimated_time": "2 小时",
                "check_method": "接口返回引用来源且能回答 3 个项目问题",
                "title": "RAG 项目链路拆解",
                "goal": normalized["learning_goal"],
                "practice": "完成一个最小 RAG API 并接入前端调用。",
                "completion_rule": "接口可运行，返回 answer、citations、confidence。",
                "estimated_minutes": 120,
                "ai_suggestion": normalized["recommended_strategy"],
                "status": "进行中",
            },
            {
                "stage_name": "部署与工程化冲刺",
                "knowledge_points": ["后端工程化", "系统部署"],
                "resources": ["部署清单", "FastAPI 接口文档", "项目任务板"],
                "tasks": ["整理环境变量", "补齐启动脚本和健康检查"],
                "estimated_time": "2 小时",
                "check_method": "本地前后端可启动，关键接口返回 200",
                "title": "部署与工程化冲刺",
                "goal": "把项目从功能演示推进到可交付状态。",
                "practice": "完成部署检查清单并修复 2 个工程化问题。",
                "completion_rule": "启动命令、接口文档和演示流程可复现。",
                "estimated_minutes": 120,
                "ai_suggestion": "优先打通可运行链路，再补工程细节。",
                "status": "推荐",
            },
        ]
    elif normalized["user_id"] == "demo-exam":
        tasks = [
            {
                "stage_name": "高频考点速记",
                "knowledge_points": ["高频考点", "概念辨析"],
                "resources": ["高频考点清单", "概念辨析卡"],
                "tasks": ["完成 20 分钟考点复盘", "标记 5 个易混概念"],
                "estimated_time": "45 分钟",
                "check_method": "考点自测正确率达到 80%",
                "title": "高频考点速记",
                "goal": normalized["learning_goal"],
                "practice": "完成考点判断题和概念配对题。",
                "completion_rule": "错题数不超过 2 题。",
                "estimated_minutes": 45,
                "ai_suggestion": normalized["recommended_strategy"],
                "status": "进行中",
            },
            {
                "stage_name": "错题二刷与模拟题",
                "knowledge_points": ["错题", "审题"],
                "resources": ["错题集", "模拟题", "复习清单"],
                "tasks": ["重做错题", "完成一组模拟题"],
                "estimated_time": "45 分钟",
                "check_method": "写出每道错题的主错因",
                "title": "错题二刷与模拟题",
                "goal": "稳定期末冲刺得分。",
                "practice": "完成 8 道模拟题并复盘错因。",
                "completion_rule": "模拟题正确率达到 85%。",
                "estimated_minutes": 45,
                "ai_suggestion": "先审题圈关键词，再选择知识点。",
                "status": "推荐",
            },
        ]
    else:
        tasks = [
            {
                "stage_name": "Python 函数基础补齐",
                "knowledge_points": ["Python 函数", "参数与返回值"],
                "resources": ["基础讲义", "函数知识点卡片"],
                "tasks": ["阅读步骤化讲义", "完成 6 道基础函数题"],
                "estimated_time": "1 小时",
                "check_method": "能独立解释参数、返回值和调用顺序",
                "title": "Python 函数基础补齐",
                "goal": normalized["learning_goal"],
                "practice": "用 3 个小例题练习函数封装。",
                "completion_rule": "基础题正确率达到 80%。",
                "estimated_minutes": 60,
                "ai_suggestion": normalized["recommended_strategy"],
                "status": "进行中",
            },
            {
                "stage_name": "SQL 与接口入门",
                "knowledge_points": ["SQL 查询", "接口基础"],
                "resources": ["SQL 知识点卡片", "接口图解"],
                "tasks": ["完成 SELECT/WHERE 基础题", "画出一次请求响应流程"],
                "estimated_time": "1 小时",
                "check_method": "能写出基础查询并说明接口输入输出",
                "title": "SQL 与接口入门",
                "goal": "补齐数据库和接口基础。",
                "practice": "完成 5 道 SQL 基础题和 1 张接口流程图。",
                "completion_rule": "SQL 查询无语法错误，接口流程说明完整。",
                "estimated_minutes": 60,
                "ai_suggestion": "用图解先理解流程，再写最小例题。",
                "status": "推荐",
            },
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
    return {
        "id": abs(hash(student["user_id"])) % 10000 + 1000,
        "user_id": student["user_id"],
        "student_name": student["student_name"],
        "course_id": student["course_id"],
        "course_name": student["course_name"],
        "current_level": student["current_level"],
        "learning_goal": student["learning_goal"],
        "weak_points": student["weak_points"],
        "learning_preference": student["learning_preference"],
        "profile_json": profile_json,
        "created_at": None,
        "updated_at": None,
    }


def get_demo_profiles(user_id: str | int | None = None) -> list[dict[str, Any]]:
    if user_id:
        return [demo_profile_to_api(get_demo_student(user_id))]
    return [demo_profile_to_api(item) for item in DEMO_STUDENTS]


def build_learning_tasks(user_id: str | int | None = None, profile_type: str | None = None) -> dict[str, Any]:
    student = get_demo_student(user_id or profile_type)
    weak = student["weak_points"]
    if student["profile_type"] == "基础薄弱型":
        tasks = [
            {
                "title": "循环边界修复任务",
                "goal": "能判断 for/while 的起止条件并解释循环次数。",
                "knowledge_points": [weak[0], "条件语句"],
                "resources": ["循环边界专项微课", "for/while 对比练习", "变量变化表模板"],
                "practice": "完成 6 道循环边界题并提交 1 个九九乘法表程序。",
                "completion_rule": "练习正确率达到 80%，且代码通过 3 个边界用例。",
                "estimated_minutes": 30,
                "ai_suggestion": "先手写前三轮变量变化，再运行代码验证。",
                "status": "进行中",
            },
            {
                "title": "函数封装入门",
                "goal": "把重复逻辑抽取为函数，说明参数和返回值。",
                "knowledge_points": [weak[1], "变量与数据类型"],
                "resources": ["函数封装案例包", "参数与返回值导学单"],
                "practice": "封装成绩平均分、最高分、及格率三个函数。",
                "completion_rule": "完成函数定义并通过样例输入输出。",
                "estimated_minutes": 25,
                "ai_suggestion": "用输入、处理、输出三列拆解函数职责。",
                "status": "推荐",
            },
        ]
    elif student["profile_type"] == "进阶提升型":
        tasks = [
            {
                "title": "成绩文件分析器项目",
                "goal": "读取 CSV 成绩文件，输出统计结果和风险学生名单。",
                "knowledge_points": ["列表", "字典", "文件操作", weak[0]],
                "resources": ["CSV 成绩分析 Notebook", "字典计数案例", "异常兜底清单"],
                "practice": "实现文件读取、统计、异常处理和结果写出。",
                "completion_rule": "项目通过 5 个测试数据文件，提交运行截图和复盘。",
                "estimated_minutes": 60,
                "ai_suggestion": "先完成最小可运行版本，再补充异常处理和输出格式。",
                "status": "进行中",
            },
            {
                "title": "代码健壮性提升",
                "goal": "为项目补充参数校验、异常提示和函数拆分。",
                "knowledge_points": [weak[1], weak[2]],
                "resources": ["工程封装范例", "单元测试入门卡"],
                "practice": "把一个长函数拆成 3 个职责清晰的小函数。",
                "completion_rule": "函数命名清晰，异常信息可读，完成 3 个测试样例。",
                "estimated_minutes": 45,
                "ai_suggestion": "用评审清单检查输入、处理、输出和异常分支。",
                "status": "推荐",
            },
        ]
    else:
        tasks = [
            {
                "title": "章节诊断测验",
                "goal": "定位递归、文件操作、循环复杂度三类高频失分点。",
                "knowledge_points": weak[:3],
                "resources": ["Python 章节诊断卷", "错题原因标签说明"],
                "practice": "完成 8 道章节练习题并标注每题错因。",
                "completion_rule": "提交测验并查看错因分析。",
                "estimated_minutes": 20,
                "ai_suggestion": "不要立即看答案，先标注每道题的卡点。",
                "status": "进行中",
            },
            {
                "title": "错题二刷与考点卡",
                "goal": "把错因转化为可执行检查清单。",
                "knowledge_points": weak,
                "resources": ["文件读写错题集", "递归调用树模板", "异常处理情境卡"],
                "practice": "重做错题并写出每题 1 条防错规则。",
                "completion_rule": "二刷正确率达到 90%。",
                "estimated_minutes": 35,
                "ai_suggestion": "每道错题只记录一个主错因，避免复盘过载。",
                "status": "推荐",
            },
        ]

    return {
        "student_id": student["user_id"],
        "student_name": student["student_name"],
        "course_name": student["course_name"],
        "active_profile_type": student["profile_type"],
        "paths": [
            {
                "profile_type": student["profile_type"],
                "summary": f"{student['profile_type']}路径：{student['recommended_strategy']}",
                "ai_recommendation": student["recommended_strategy"],
                "tasks": tasks,
            }
        ],
    }


def build_resource_pack(payload: dict[str, Any]) -> dict[str, Any]:
    student = get_demo_student(payload.get("studentId") or payload.get("student_id") or payload.get("user_id"))
    course_name = payload.get("courseName") or payload.get("course_name") or student["course_name"]
    incoming_points = payload.get("knowledgePoints") or payload.get("knowledge_points") or payload.get("weakPoints") or payload.get("weak_points")
    weak_points = [str(item) for item in incoming_points] if incoming_points else student["weak_points"]
    level = payload.get("level") or payload.get("studentLevel") or student["current_level"]
    goal = payload.get("goal") or payload.get("learningGoal") or student["learning_goal"]
    main_point = weak_points[0]
    resources = [
        {
            "resourceType": "个性化讲义",
            "title": f"{main_point} 分步讲义",
            "content": f"面向{level}学生，先解释 {main_point} 的概念和常见误区，再给出 2 个基础例题和 1 个自检清单。",
            "reason": f"匹配学习目标：{goal}",
            "relatedKnowledgePoints": weak_points[:3],
            "difficulty": "基础" if level == "基础薄弱" else "中等",
            "estimatedMinutes": 18,
        },
        {
            "resourceType": "练习题",
            "title": f"{main_point} 分层练习 8 题",
            "content": "包含基础题、变式题和综合题，每题带提示、答案解析和错因标签。",
            "reason": "用形成性练习检查薄弱点是否真正掌握。",
            "relatedKnowledgePoints": weak_points,
            "difficulty": "中等",
            "estimatedMinutes": 25,
        },
        {
            "resourceType": "代码案例或实验任务",
            "title": f"{course_name} 小实验：{main_point} 应用",
            "content": "提供可运行样例、待补全代码和扩展任务，要求提交运行截图和关键步骤说明。",
            "reason": "把单点知识迁移到可展示产物。",
            "relatedKnowledgePoints": weak_points[:4],
            "difficulty": "进阶",
            "estimatedMinutes": 35,
        },
        {
            "resourceType": "思维导图文本",
            "title": f"{main_point} 结构化复盘图",
            "content": f"中心主题：{main_point}\n一级节点：概念定义、解题步骤、常见错误、典型例题、复盘问题。",
            "reason": "帮助学生建立知识点之间的关系。",
            "relatedKnowledgePoints": weak_points[:3],
            "difficulty": "基础",
            "estimatedMinutes": 12,
        },
        {
            "resourceType": "视频脚本或项目任务书",
            "title": f"{course_name} 8 分钟讲解脚本与任务书",
            "content": "脚本结构：问题引入、核心概念、例题演示、课后任务；任务书包含目标、步骤、提交物和评分点。",
            "reason": "可进入管理员审核流程，审核通过后发布到学生端。",
            "relatedKnowledgePoints": weak_points,
            "difficulty": "中等",
            "estimatedMinutes": 20,
        },
    ]
    return {
        "studentId": student["user_id"],
        "studentName": student["student_name"],
        "profileType": student["profile_type"],
        "courseId": payload.get("courseId") or payload.get("course_id") or student["course_id"],
        "courseName": course_name,
        "studentLevel": level,
        "learningGoal": goal,
        "weakPoints": weak_points,
        "packageTitle": f"{student['student_name']}的{course_name}个性化资源包",
        "resources": resources,
        "resourceCount": len(resources),
        "mode": "profile-aware-demo",
        "auditFlow": ["ResourceAgent 生成", "AuditAgent 初审", "管理员复核", "发布到学生端"],
    }


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
            if item["risk_level"] in {"高风险", "需关注"}
        ],
        "resource_usage": [
            {
                "student_name": item["student_name"],
                "profile_type": item["profile_type"],
                "usage_rate": item["resource_usage"],
                "recommended_count": 5,
                "completed_count": max(1, round(item["resource_usage"] / 20)),
            }
            for item in DEMO_STUDENTS
        ],
    }


def build_agent_steps(user_id: str | int | None = None) -> list[dict[str, Any]]:
    student = get_demo_student(user_id)
    return [
        {
            "key": "profile_agent",
            "name": "画像 Agent",
            "input_summary": f"user_id={student['user_id']}，课程={student['course_name']}",
            "output_summary": f"识别为{student['profile_type']}，薄弱点：{'、'.join(student['weak_points'][:3])}",
            "duration_ms": 180,
            "duration": "180ms",
            "status": "success",
        },
        {
            "key": "resource_agent",
            "name": "资源 Agent",
            "input_summary": "画像、课程、知识点、学习目标",
            "output_summary": "生成讲义、练习、实验、思维导图、视频脚本 5 类资源",
            "duration_ms": 260,
            "duration": "260ms",
            "status": "success",
        },
        {
            "key": "qa_agent",
            "name": "问答 Agent",
            "input_summary": "学生问题、课程知识库、薄弱点",
            "output_summary": "返回带引用、置信度和练习建议的 RAG 回答",
            "duration_ms": 220,
            "duration": "220ms",
            "status": "success",
        },
        {
            "key": "diagnosis_agent",
            "name": "诊断 Agent",
            "input_summary": "测评、答疑日志、资源完成情况",
            "output_summary": f"标记风险等级：{student['risk_level']}，生成教师干预建议",
            "duration_ms": 210,
            "duration": "210ms",
            "status": "success",
        },
        {
            "key": "audit_agent",
            "name": "审核 Agent",
            "input_summary": "AI 生成资源、引用来源、审核策略",
            "output_summary": "输出风险标签、引用覆盖率和待管理员复核状态",
            "duration_ms": 160,
            "duration": "160ms",
            "status": "success",
        },
    ]


def build_content_review_items() -> dict[str, Any]:
    items = []
    for index, student in enumerate(DEMO_STUDENTS, start=1):
        status = ["待审核", "已通过", "已驳回"][index - 1]
        items.append(
            {
                "id": f"cr-demo-{index:03d}",
                "title": f"{student['student_name']}的{student['weak_points'][0]}个性化资源包",
                "resource_type": "AI 个性化资源包",
                "source": "ResourceAgent -> AuditAgent",
                "risk_tags": ["引用覆盖检查", "诊断结论需谨慎"] if status != "已通过" else ["已补充引用", "难度匹配"],
                "status": status,
                "review_opinion": (
                    "等待管理员确认资源难度、引用来源和诊断措辞。"
                    if status == "待审核"
                    else "已通过审核，可发布到学生端。"
                    if status == "已通过"
                    else "诊断语气过于确定，需改为教学辅助建议后重生成。"
                ),
                "student_name": student["student_name"],
                "profile_type": student["profile_type"],
                "audit_flow": ["AI 生成", "AuditAgent 初审", "管理员复核", "发布/驳回"],
            }
        )
    return {
        "items": items,
        "policy": "AI 生成内容必须经过 AuditAgent 初审和管理员复核，引用不足、诊断绝对化或难度不匹配的资源不得发布。",
    }
