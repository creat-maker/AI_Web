from __future__ import annotations

from typing import Any


KNOWLEDGE_POINTS = [
    {
        "id": "syntax",
        "name": "基础语法",
        "status": "mastered",
        "status_label": "已掌握",
        "mastery": 86,
        "description": "变量、表达式、输入输出和基础运算，是循环结构学习的前置基础。",
        "resources": ["基础语法速查卡"],
        "exercises": ["变量命名判断题"],
        "ai_suggestion": "保持复习即可，不作为当前重点薄弱点。",
    },
    {
        "id": "conditions",
        "name": "条件判断",
        "status": "learning",
        "status_label": "学习中",
        "mastery": 76,
        "description": "if/elif/else、布尔表达式和条件拆解。",
        "resources": ["条件判断导学单"],
        "exercises": ["成绩等级判断"],
        "ai_suggestion": "先画条件表，再写代码，为 while 条件判断做准备。",
    },
    {
        "id": "for-loop",
        "name": "for 循环",
        "status": "learning",
        "status_label": "学习中",
        "mastery": 70,
        "description": "掌握 range、遍历和循环次数判断。",
        "resources": ["for 循环边界讲义"],
        "exercises": ["输出指定范围内的偶数"],
        "ai_suggestion": "先判断起点、终点和步长。",
    },
    {
        "id": "while-loop",
        "name": "while 循环",
        "status": "weak",
        "status_label": "薄弱",
        "mastery": 48,
        "description": "理解循环条件、变量更新和死循环风险。",
        "resources": ["while 死循环修复案例"],
        "exercises": ["while 循环补全题"],
        "ai_suggestion": "先手写前三轮变量变化，再运行代码验证。",
    },
    {
        "id": "break-continue",
        "name": "break / continue",
        "status": "weak",
        "status_label": "薄弱",
        "mastery": 58,
        "description": "区分跳出循环和跳过本轮循环。",
        "resources": ["break / continue 对比卡"],
        "exercises": ["控制语句判断题"],
        "ai_suggestion": "用输出结果反推控制语句的作用。",
    },
    {
        "id": "nested-loop",
        "name": "循环嵌套",
        "status": "weak",
        "status_label": "薄弱",
        "mastery": 54,
        "description": "跟踪内外层循环变量变化和执行顺序。",
        "resources": ["循环嵌套变量变化表"],
        "exercises": ["九九乘法表补全"],
        "ai_suggestion": "把外层变量和内层变量分列记录。",
    },
    {
        "id": "loop-practice",
        "name": "循环综合实操",
        "status": "not_started",
        "status_label": "后续章节",
        "mastery": 35,
        "description": "后续用于封装循环任务，不作为当前重点薄弱点。",
        "resources": ["后续章节预告"],
        "exercises": ["封装循环统计逻辑"],
        "ai_suggestion": "完成循环结构后再进入。",
    },
]

KNOWLEDGE_LINKS = [
    {"source": "syntax", "target": "conditions", "relation": "表达式基础"},
    {"source": "conditions", "target": "for-loop", "relation": "循环控制"},
    {"source": "conditions", "target": "while-loop", "relation": "循环条件"},
    {"source": "while-loop", "target": "break-continue", "relation": "控制语句"},
    {"source": "for-loop", "target": "nested-loop", "relation": "嵌套遍历"},
    {"source": "break-continue", "target": "nested-loop", "relation": "复杂控制"},
    {"source": "nested-loop", "target": "functions", "relation": "后续封装"},
]

LEARNING_TASKS = [
    {
        "profile_type": "基础薄弱 + 代码实操偏好型",
        "summary": "围绕循环结构薄弱点，先修复 while 死循环，再区分 break / continue，最后完成循环嵌套实操。",
        "ai_recommendation": "每天 25-30 分钟，用短代码和变量变化表建立可见进步。",
        "tasks": [
            {
                "title": "while 循环终止条件补全",
                "goal": "能判断循环是否会终止，并解释变量如何更新。",
                "knowledge_points": ["while 循环", "循环结构"],
                "resources": ["while 死循环修复案例", "循环条件检查清单"],
                "practice": "完成 3 道 while 循环补全题。",
                "completion_rule": "正确率达到 80%，且能写出前三轮变量变化。",
                "estimated_minutes": 30,
                "ai_suggestion": "先检查初始值、条件和更新语句。",
                "status": "进行中",
            },
            {
                "title": "break / continue 对比练习",
                "goal": "区分跳出循环和跳过本轮循环。",
                "knowledge_points": ["break / continue"],
                "resources": ["break / continue 对比卡"],
                "practice": "完成 6 道输出结果判断题。",
                "completion_rule": "能解释每次输出变化。",
                "estimated_minutes": 20,
                "ai_suggestion": "把每轮输出写在表格中。",
                "status": "推荐",
            },
            {
                "title": "循环嵌套变量追踪",
                "goal": "能跟踪内外层循环执行顺序。",
                "knowledge_points": ["循环嵌套", "for 循环"],
                "resources": ["循环嵌套变量变化表"],
                "practice": "补全九九乘法表程序。",
                "completion_rule": "代码通过 3 个边界用例。",
                "estimated_minutes": 35,
                "ai_suggestion": "外层变量一列，内层变量一列。",
                "status": "未开始",
            },
        ],
    },
    {
        "profile_type": "教师干预路径",
        "summary": "教师端围绕需重点关注学生李明进行短时讲解和课后跟踪。",
        "ai_recommendation": "课堂讲解 10 分钟，课后布置 3 道 while 循环补全题。",
        "tasks": [
            {
                "title": "10 分钟代码讲解",
                "goal": "用一段 while 死循环示例讲清变量更新位置。",
                "knowledge_points": ["while 循环"],
                "resources": ["while 死循环讲解脚本"],
                "practice": "课堂即时修改错误代码。",
                "completion_rule": "李明能口头解释死循环原因。",
                "estimated_minutes": 10,
                "ai_suggestion": "从错误代码入手，不直接给最终答案。",
                "status": "推荐",
            }
        ],
    },
]

QUIZ = {
    "quiz_id": "python-loop-quiz-1",
    "title": "Python 循环结构专项测验",
    "chapter": "循环结构",
    "questions": [
        {
            "id": "q1",
            "type": "single",
            "stem": "while 循环最容易出现的典型错误是？",
            "options": ["忘记更新循环变量", "变量名太短", "注释太少", "缩进太整齐"],
            "answer": "忘记更新循环变量",
            "knowledge_point": "while 循环",
            "reason_tag": "没有把循环条件和变量更新联系起来",
        },
        {
            "id": "q2",
            "type": "single",
            "stem": "continue 的作用是？",
            "options": ["跳出整个循环", "跳过本轮剩余语句进入下一轮", "结束程序", "定义变量"],
            "answer": "跳过本轮剩余语句进入下一轮",
            "knowledge_point": "break / continue",
            "reason_tag": "把 continue 误认为直接结束循环",
        },
        {
            "id": "q3",
            "type": "single",
            "stem": "分析循环嵌套时最推荐先记录什么？",
            "options": ["内外层变量变化", "电脑型号", "注释数量", "文件名"],
            "answer": "内外层变量变化",
            "knowledge_point": "循环嵌套",
            "reason_tag": "没有逐轮跟踪内外层变量变化",
        },
    ],
}


def get_knowledge_graph() -> dict[str, Any]:
    return {
        "course_id": "python-programming",
        "course_name": "Python 程序设计",
        "status_legend": {
            "mastered": "已掌握",
            "learning": "学习中",
            "weak": "薄弱",
            "not_started": "后续章节",
        },
        "nodes": KNOWLEDGE_POINTS,
        "links": KNOWLEDGE_LINKS,
        "recommendation_policy": "围绕李明的画像、测验错因、学习路径任务和 AI 学伴问答综合推荐循环结构补弱资源。",
    }


def get_learning_tasks(profile_type: str | None = None) -> dict[str, Any]:
    selected = LEARNING_TASKS
    if profile_type:
        selected = [item for item in LEARNING_TASKS if item["profile_type"] == profile_type] or LEARNING_TASKS
    return {
        "student_id": "demo-basic",
        "student_name": "李明",
        "course_name": "Python 程序设计",
        "active_profile_type": selected[0]["profile_type"],
        "paths": selected,
    }


def submit_quiz_answers(answers: dict[str, str]) -> dict[str, Any]:
    total = len(QUIZ["questions"])
    wrong_items = []
    correct_count = 0
    for question in QUIZ["questions"]:
        selected = answers.get(question["id"])
        is_correct = selected == question["answer"]
        if is_correct:
            correct_count += 1
        else:
            wrong_items.append(
                {
                    "question_id": question["id"],
                    "stem": question["stem"],
                    "selected": selected or "未作答",
                    "correct_answer": question["answer"],
                    "knowledge_point": question["knowledge_point"],
                    "reason": question["reason_tag"],
                    "recommendation": f"复习「{question['knowledge_point']}」资源，并完成 2 道同类变式题。",
                }
            )
    weak_points = sorted({item["knowledge_point"] for item in wrong_items})
    score = round(correct_count / total * 100)
    return {
        "quiz_id": QUIZ["quiz_id"],
        "score": score,
        "correct_count": correct_count,
        "total": total,
        "wrong_items": wrong_items,
        "weak_points": weak_points,
        "cause_analysis": [
            {"type": "概念理解", "detail": "知道循环语法形式，但对终止条件、控制语句或变量变化理解不稳定。"},
            {"type": "代码应用", "detail": "读代码时没有逐轮跟踪变量变化，容易漏掉边界条件。"},
        ]
        if wrong_items
        else [{"type": "稳定掌握", "detail": "本次循环结构测验全部正确，可进入循环嵌套综合任务。"}],
        "recommended_resources": [
            {"title": "while 死循环修复案例", "knowledge_point": "while 循环", "minutes": 12},
            {"title": "break / continue 对比卡", "knowledge_point": "break / continue", "minutes": 10},
            {"title": "循环嵌套变量变化表", "knowledge_point": "循环嵌套", "minutes": 15},
        ],
        "next_step": "系统已把薄弱知识点写入李明的学习路径，建议先完成 while 循环补全题，再进入 break / continue 对比练习。",
    }


def generate_teacher_workbench(payload: dict[str, Any]) -> dict[str, Any]:
    generate_type = payload.get("type", "lesson_plan")
    course = payload.get("course") or "Python 程序设计"
    chapter = payload.get("chapter") or "循环结构"
    foundation = payload.get("student_foundation") or "李明在循环结构上还需要加强，偏好代码实操"
    goal = payload.get("teaching_goal") or "掌握 for 循环、while 循环、break / continue 和循环嵌套"
    title_map = {
        "lesson_plan": "AI 生成循环结构教案",
        "quiz": "AI 生成循环结构测验",
        "analysis": "AI 生成循环结构学情分析",
    }
    return {
        "type": generate_type,
        "title": title_map.get(generate_type, "AI 教学建议"),
        "course": course,
        "chapter": chapter,
        "input_summary": f"学生基础：{foundation}；教学目标：{goal}",
        "teaching_objectives": [
            goal,
            "识别 while 循环、循环嵌套和 break / continue 薄弱点并形成可干预任务",
            "完成测评、诊断、推荐、审核闭环记录",
        ],
        "key_difficulties": ["while 循环条件更新", "循环嵌套变量变化", "break / continue 区分"],
        "class_activities": ["5 分钟错题导入", "10 分钟 while 死循环代码讲解", "10 分钟控制语句练习", "8 分钟变量变化表复盘"],
        "in_class_quiz": ["判断 while 循环是否会终止", "解释 break 和 continue 的输出差异", "补全嵌套循环变量变化表"],
        "after_class_tasks": ["完成 3 道 while 循环补全题", "提交循环嵌套变量变化表", "在 AI 学伴中追问 1 个薄弱知识点"],
        "teaching_suggestions": [
            "生成内容需教师审核后发布",
            "需重点关注学生李明优先推送循环结构补弱资源包",
            "测验结果仅作为诊断参考，不直接替代教师评价",
        ],
        "review_required": True,
    }


def get_content_review_items() -> dict[str, Any]:
    return {
        "items": [
            {
                "id": "cr-001",
                "title": "Python 循环结构个性化补弱资源包",
                "resource_type": "资源包",
                "source": "ResourcePackageAgent",
                "risk_tags": ["引用依据完整", "适配李明画像"],
                "status": "通过",
                "review_opinion": "可发布到学生端，引用依据为 Python 程序设计课程知识库 / 循环结构章节。",
            },
            {
                "id": "cr-002",
                "title": "AI 学伴回答：while 循环为什么会死循环",
                "resource_type": "AI 学伴回答",
                "source": "TutorAgent",
                "risk_tags": ["需补充变量更新示例"],
                "status": "需修改",
                "review_opinion": "建议增加代码片段和变量变化表。",
            },
            {
                "id": "cr-003",
                "title": "while 死循环讲解内容",
                "resource_type": "微课视频脚本",
                "source": "TeachingScriptAgent",
                "risk_tags": ["需教师复核示例代码"],
                "status": "人工复核",
                "review_opinion": "教师确认后再进入发布流程。",
            },
            {
                "id": "cr-004",
                "title": "未经引用的循环结构结论",
                "resource_type": "个性化推荐",
                "source": "EvaluationAgent",
                "risk_tags": ["引用依据不足"],
                "status": "风险拦截",
                "review_opinion": "缺少可追溯引用，不允许直接发布到学生端。",
            },
        ],
        "policy": "AI 生成内容仅作为教学辅助，关键资源、测评结论和学生干预建议需教师或管理员审核后使用。",
    }


def get_platform_quality() -> dict[str, Any]:
    return {
        "summary": {
            "course_completion_rate": 76.8,
            "average_quiz_score": 74.2,
            "resource_usage_rate": 68.5,
            "weak_point_concentration": 52.0,
            "teacher_ai_tool_uses": 286,
            "content_review_pass_rate": 91.2,
        },
        "ai_metrics": {
            "qa_count": 18620,
            "resource_generation_count": 1324,
            "quiz_completion_count": 4286,
            "review_pass_rate": 91.2,
        },
        "quality_dimensions": [
            {"name": "循环结构任务完成率", "value": 76.8, "suggestion": "关注 while 循环补全题未完成学生。"},
            {"name": "专项测验均分", "value": 74.2, "suggestion": "继续降低循环嵌套入门题难度。"},
            {"name": "补弱资源使用率", "value": 68.5, "suggestion": "提高讲解文档和代码实操案例曝光。"},
            {"name": "薄弱知识点集中度", "value": 52.0, "suggestion": "集中治理 while 循环、循环嵌套和 break / continue。"},
        ],
        "ai_boundary": "AI 生成内容仅作为教学辅助。数字人能力当前描述为讲解脚本 / TTS 或数字人 API 预留，不描述为完整实时数字人系统。",
    }
