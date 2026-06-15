from __future__ import annotations

from typing import Any


DEFAULT_WEAK_POINTS = ["while 循环终止条件", "break / continue 区分", "循环嵌套变量变化"]


def _join_answers(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("answer", "message", "dialog", "profileAnswer"):
        value = payload.get(key)
        if isinstance(value, str):
            parts.append(value)
    answers = payload.get("answers") or payload.get("dialogAnswers")
    if isinstance(answers, list):
        for item in answers:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.extend(str(item.get(k, "")) for k in ("question", "answer", "content") if item.get(k))
    return " ".join(parts).strip()


def _detect_weak_points(text: str, incoming: list[str] | None = None) -> list[str]:
    points = list(incoming or [])
    mapping = [
        ("极限", "极限计算与等价变形"),
        ("导数", "导数应用题建模"),
        ("死循环", "循环边界与变量更新"),
        ("栈", "栈和队列操作过程"),
        ("队列", "栈和队列操作过程"),
        ("英语", "英语长难句阅读"),
        ("阅读", "英语阅读定位"),
        ("Python", "Python 循环结构代码实操"),
        ("函数", "循环结构综合实操"),
        ("文件", "循环结构案例复盘"),
        ("代码", "代码调试与边界条件"),
    ]
    for keyword, point in mapping:
        if keyword.lower() in text.lower() and point not in points:
            points.append(point)
    if not points:
        points = DEFAULT_WEAK_POINTS.copy()
    return points[:5]


def _detect_preference(text: str) -> str:
    if any(word in text for word in ["视频", "讲解", "老师讲"]):
        return "偏好短视频讲解和例题拆解"
    if any(word in text for word in ["项目", "实验", "代码", "动手"]):
        return "偏好项目实践、代码案例和可操作任务"
    if any(word in text for word in ["题", "刷题", "练习"]):
        return "偏好分层练习和错题复盘"
    return "偏好图文讲义、分步示例和短练习结合"


def run_profile_dialog(payload: dict[str, Any]) -> dict[str, Any]:
    text = _join_answers(payload)
    weak_points = _detect_weak_points(text, payload.get("weakPoints") or payload.get("weak_points"))
    preference = _detect_preference(text)
    student_name = payload.get("studentName") or payload.get("student_name") or "李明"
    course_name = payload.get("courseName") or payload.get("course_name") or "Python 程序设计"
    time_arrangement = "每天 30 分钟专项练习，周末 1 次综合复盘"
    if any(word in text for word in ["时间少", "忙", "碎片"]):
        time_arrangement = "工作日每天 15 分钟碎片学习，周末集中 45 分钟补强"
    foundation = "中等基础"
    if any(word in text for word in ["基础差", "跟不上", "不会"]):
        foundation = "基础薄弱"
    elif any(word in text for word in ["还可以", "比较好", "熟悉"]):
        foundation = "基础较好"
    risk = "中等风险：薄弱点集中，需要连续两周跟踪任务完成率"
    if len(weak_points) >= 4 or foundation == "基础薄弱":
        risk = "较高风险：建议教师关注并安排低门槛补强任务"

    dimensions = [
        {"name": "学习目标", "value": f"围绕 {course_name} 完成薄弱点补强，并提升综合应用能力"},
        {"name": "基础水平", "value": foundation},
        {"name": "薄弱知识点", "value": "、".join(weak_points)},
        {"name": "学习偏好", "value": preference},
        {"name": "时间安排", "value": time_arrangement},
        {"name": "学习风险", "value": risk},
        {"name": "推荐策略", "value": "先讲义补概念，再练习题巩固，最后用实验任务完成迁移应用"},
    ]
    return {
        "studentId": payload.get("studentId") or payload.get("student_id") or "demo-student-zhangsan",
        "studentName": student_name,
        "courseId": payload.get("courseId") or payload.get("course_id") or "demo-course-python",
        "courseName": course_name,
        "summary": f"{student_name} 当前画像已生成，建议围绕 {weak_points[0]} 开始补强。",
        "dimensions": dimensions,
        "learningGoal": dimensions[0]["value"],
        "foundationLevel": foundation,
        "weakKnowledgePoints": weak_points,
        "learningPreference": preference,
        "timeArrangement": time_arrangement,
        "learningRisk": risk,
        "recommendedStrategy": dimensions[-1]["value"],
        "mode": "rule-based-demo",
    }


def generate_resource_pack(payload: dict[str, Any]) -> dict[str, Any]:
    weak_points = _detect_weak_points(" ".join(payload.get("weakPoints") or payload.get("weak_points") or []), payload.get("weakPoints") or payload.get("weak_points"))
    course_name = payload.get("courseName") or payload.get("course_name") or "Python 程序设计"
    student_id = payload.get("studentId") or payload.get("student_id") or "demo-student-zhangsan"
    course_id = payload.get("courseId") or payload.get("course_id") or "demo-course-python"
    main_point = weak_points[0]
    resources = [
        {
            "resourceType": "个性化讲义",
            "title": f"{course_name}：{main_point} 分步讲义",
            "content": f"先用概念卡片解释 {main_point}，再给出 2 个基础例题和 1 个易错点对照，最后附 5 分钟自检清单。",
            "reason": "适合先补齐概念和步骤，降低直接刷题的挫败感。",
            "relatedKnowledgePoints": weak_points[:3],
            "difficulty": "基础",
            "estimatedMinutes": 18,
        },
        {
            "resourceType": "练习题",
            "title": f"{main_point} 分层练习 8 题",
            "content": "包含 3 道基础题、3 道变式题和 2 道综合题，每题提供提示、标准答案和错因标签。",
            "reason": "通过分层练习检查是否真正掌握薄弱知识点。",
            "relatedKnowledgePoints": weak_points,
            "difficulty": "中等",
            "estimatedMinutes": 25,
        },
        {
            "resourceType": "代码案例或实验任务",
            "title": f"{course_name} 小实验：从示例到迁移",
            "content": "给出可运行样例、待补全代码和扩展任务，要求学生解释关键步骤并提交运行截图或结果说明。",
            "reason": "把知识点迁移到可展示的实践任务，适合形成学习闭环。",
            "relatedKnowledgePoints": weak_points[:4],
            "difficulty": "进阶",
            "estimatedMinutes": 35,
        },
        {
            "resourceType": "思维导图文本",
            "title": f"{main_point} 思维导图",
            "content": f"中心主题：{main_point}\n一级节点：概念定义、解题步骤、常见错误、典型例题、复盘问题。\n二级节点：每个节点附 2 个关键词和 1 个自测问题。",
            "reason": "帮助学生建立结构化认知，便于课后复盘和教师讲解。",
            "relatedKnowledgePoints": weak_points[:3],
            "difficulty": "基础",
            "estimatedMinutes": 12,
        },
        {
            "resourceType": "视频脚本或项目任务书",
            "title": f"{course_name} 8 分钟讲解脚本与任务书",
            "content": "脚本结构：问题引入 1 分钟、核心概念 3 分钟、例题演示 3 分钟、课后任务 1 分钟；任务书包含目标、步骤、提交物和评分点。",
            "reason": "可直接用于教师端资源生成展示，也便于学生端按步骤完成任务。",
            "relatedKnowledgePoints": weak_points,
            "difficulty": "中等",
            "estimatedMinutes": 20,
        },
    ]
    return {
        "studentId": student_id,
        "courseId": course_id,
        "courseName": course_name,
        "weakPoints": weak_points,
        "packageTitle": f"{course_name} 个性化资源包",
        "resources": resources,
        "resourceCount": len(resources),
        "mode": "rule-based-demo",
    }
