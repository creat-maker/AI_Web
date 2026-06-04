from __future__ import annotations

from typing import Any


KNOWLEDGE_POINTS = [
    {
        "id": "variables",
        "name": "变量与数据类型",
        "status": "mastered",
        "status_label": "已掌握",
        "mastery": 92,
        "description": "理解变量命名、数字/字符串/布尔值类型转换和基础输入输出。",
        "resources": ["变量命名规范速查", "类型转换 10 分钟微课"],
        "exercises": ["完成 5 道类型转换选择题", "编写 BMI 计算小程序"],
        "ai_suggestion": "已具备后续学习基础，可通过小项目巩固变量命名和类型边界。",
    },
    {
        "id": "conditions",
        "name": "条件语句",
        "status": "learning",
        "status_label": "学习中",
        "mastery": 76,
        "description": "掌握 if/elif/else 分支、布尔表达式和嵌套条件拆解。",
        "resources": ["分支结构案例讲义", "条件表达式错题集"],
        "exercises": ["成绩等级判断", "会员折扣规则实现"],
        "ai_suggestion": "建议先画条件表，再写代码，减少漏分支问题。",
    },
    {
        "id": "loops",
        "name": "循环结构",
        "status": "weak",
        "status_label": "薄弱",
        "mastery": 58,
        "description": "理解 for/while、循环控制、嵌套循环和边界条件。",
        "resources": ["循环边界专项微课", "for/while 对比练习"],
        "exercises": ["九九乘法表", "统计列表中满足条件的元素"],
        "ai_suggestion": "先写循环不变量和停止条件，再补充循环体，避免死循环和少算一次。",
    },
    {
        "id": "functions",
        "name": "函数",
        "status": "learning",
        "status_label": "学习中",
        "mastery": 69,
        "description": "掌握函数定义、参数、返回值、作用域和模块化拆分。",
        "resources": ["函数封装案例包", "参数与返回值导学单"],
        "exercises": ["封装成绩统计函数", "拆分温度转换程序"],
        "ai_suggestion": "把重复代码先圈出来，再抽象输入、处理和输出。",
    },
    {
        "id": "lists",
        "name": "列表",
        "status": "mastered",
        "status_label": "已掌握",
        "mastery": 88,
        "description": "掌握列表索引、切片、遍历、增删改查和常用方法。",
        "resources": ["列表操作速查表", "列表推导式入门"],
        "exercises": ["学生成绩排序", "筛选偶数列表"],
        "ai_suggestion": "可以进入列表与循环结合的综合题，提升数据处理速度。",
    },
    {
        "id": "dicts",
        "name": "字典",
        "status": "not_started",
        "status_label": "未学习",
        "mastery": 34,
        "description": "理解键值对、字典遍历、统计计数和嵌套数据结构。",
        "resources": ["字典计数案例", "JSON 与字典对照讲义"],
        "exercises": ["词频统计", "课程成绩表查询"],
        "ai_suggestion": "建议在掌握列表遍历后进入，重点理解 key 的唯一性。",
    },
    {
        "id": "files",
        "name": "文件操作",
        "status": "weak",
        "status_label": "薄弱",
        "mastery": 52,
        "description": "掌握 with open、读写模式、编码、CSV 读写和异常边界。",
        "resources": ["文件读写分步讲义", "CSV 成绩分析 Notebook"],
        "exercises": ["读取日志并统计关键字", "学生成绩 CSV 汇总"],
        "ai_suggestion": "先复习异常处理，再练习文件不存在、空文件、编码错误三类边界。",
    },
    {
        "id": "exceptions",
        "name": "异常处理",
        "status": "not_started",
        "status_label": "未学习",
        "mastery": 28,
        "description": "理解 try/except/finally、异常类型和可恢复错误处理。",
        "resources": ["异常处理情境卡", "常见异常类型清单"],
        "exercises": ["输入合法性校验", "文件读取异常兜底"],
        "ai_suggestion": "结合文件操作一起练，重点区分错误提示和程序崩溃。",
    },
]

KNOWLEDGE_LINKS = [
    {"source": "variables", "target": "conditions", "relation": "表达式基础"},
    {"source": "conditions", "target": "loops", "relation": "循环控制"},
    {"source": "loops", "target": "functions", "relation": "封装重复逻辑"},
    {"source": "loops", "target": "lists", "relation": "遍历数据"},
    {"source": "lists", "target": "dicts", "relation": "结构化数据"},
    {"source": "dicts", "target": "files", "relation": "持久化数据"},
    {"source": "files", "target": "exceptions", "relation": "边界兜底"},
    {"source": "functions", "target": "files", "relation": "工程封装"},
]

LEARNING_TASKS = [
    {
        "profile_type": "基础薄弱型",
        "summary": "先补齐变量、条件、循环和函数的概念断点，用短任务建立可见进步。",
        "ai_recommendation": "每天 25 分钟，优先完成可自动判分的小练习，降低挫败感。",
        "tasks": [
            {
                "title": "循环边界修复任务",
                "goal": "能判断 for/while 的起止条件并解释循环次数。",
                "knowledge_points": ["循环结构", "条件语句"],
                "resources": ["循环边界专项微课", "for/while 对比练习"],
                "practice": "完成 6 道循环边界题并提交 1 个九九乘法表程序。",
                "completion_rule": "练习正确率达到 80%，且代码通过 3 个边界用例。",
                "estimated_minutes": 30,
                "ai_suggestion": "先手写前三轮循环变量变化，再运行代码验证。",
                "status": "进行中",
            },
            {
                "title": "函数封装入门",
                "goal": "把重复逻辑抽取为函数，说明参数和返回值。",
                "knowledge_points": ["函数", "变量与数据类型"],
                "resources": ["函数封装案例包", "参数与返回值导学单"],
                "practice": "封装成绩平均分、最高分、及格率三个函数。",
                "completion_rule": "完成函数定义并通过样例输入输出。",
                "estimated_minutes": 25,
                "ai_suggestion": "用输入、处理、输出三列拆解函数职责。",
                "status": "未开始",
            },
        ],
    },
    {
        "profile_type": "考试冲刺型",
        "summary": "围绕高频考点和错题分布安排测评、纠错和二次练习。",
        "ai_recommendation": "先做诊断测验，再按薄弱知识点刷题，最后生成错题复盘卡。",
        "tasks": [
            {
                "title": "章节诊断测验",
                "goal": "定位循环、函数、文件操作三类高频失分点。",
                "knowledge_points": ["循环结构", "函数", "文件操作"],
                "resources": ["Python 章节诊断卷", "错题原因标签说明"],
                "practice": "完成 8 道章节练习题。",
                "completion_rule": "提交测验并查看错因分析。",
                "estimated_minutes": 20,
                "ai_suggestion": "不要立即看答案，先标注每道题的卡点。",
                "status": "推荐",
            },
            {
                "title": "错题二刷",
                "goal": "把错因从概念不清转化为可执行检查清单。",
                "knowledge_points": ["文件操作", "异常处理"],
                "resources": ["文件读写错题集", "异常处理情境卡"],
                "practice": "重做错题并写出每题 1 条防错规则。",
                "completion_rule": "二刷正确率达到 90%。",
                "estimated_minutes": 35,
                "ai_suggestion": "每道错题只记录一个主错因，避免复盘过载。",
                "status": "未开始",
            },
        ],
    },
    {
        "profile_type": "项目实践型",
        "summary": "用小项目串联列表、字典、文件和异常处理，强化迁移应用。",
        "ai_recommendation": "适合已有基础的学生，建议用项目产物替代单点刷题。",
        "tasks": [
            {
                "title": "成绩文件分析器",
                "goal": "读取 CSV 成绩文件，输出统计结果和风险学生名单。",
                "knowledge_points": ["列表", "字典", "文件操作", "异常处理"],
                "resources": ["CSV 成绩分析 Notebook", "字典计数案例"],
                "practice": "实现文件读取、异常兜底、平均分统计和结果写出。",
                "completion_rule": "项目通过 5 个测试数据文件，提交运行截图。",
                "estimated_minutes": 60,
                "ai_suggestion": "先完成最小可运行版本，再补充异常处理和输出格式。",
                "status": "推荐",
            }
        ],
    },
]

QUIZ = {
    "quiz_id": "python-chapter-1",
    "title": "Python 程序设计章节练习",
    "chapter": "基础语法到文件操作",
    "questions": [
        {
            "id": "q1",
            "type": "single",
            "stem": "以下哪个写法最适合安全读取文本文件？",
            "options": ["open('a.txt').read()", "with open('a.txt', encoding='utf-8') as f", "eval(open('a.txt'))", "input('a.txt')"],
            "answer": "with open('a.txt', encoding='utf-8') as f",
            "knowledge_point": "文件操作",
            "reason_tag": "文件资源管理不熟",
        },
        {
            "id": "q2",
            "type": "single",
            "stem": "while 循环最容易出现的典型错误是？",
            "options": ["忘记更新循环变量", "变量名太短", "注释太少", "函数名重复"],
            "answer": "忘记更新循环变量",
            "knowledge_point": "循环结构",
            "reason_tag": "循环终止条件不清",
        },
        {
            "id": "q3",
            "type": "single",
            "stem": "函数 return 的主要作用是？",
            "options": ["打印结果", "结束程序", "返回计算结果给调用方", "创建变量"],
            "answer": "返回计算结果给调用方",
            "knowledge_point": "函数",
            "reason_tag": "参数与返回值混淆",
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
            "not_started": "未学习",
        },
        "nodes": KNOWLEDGE_POINTS,
        "links": KNOWLEDGE_LINKS,
        "recommendation_policy": "根据掌握率、错题标签和学习路径任务综合推荐资源。",
    }


def get_learning_tasks(profile_type: str | None = None) -> dict[str, Any]:
    selected = LEARNING_TASKS
    if profile_type:
        selected = [item for item in LEARNING_TASKS if item["profile_type"] == profile_type] or LEARNING_TASKS
    return {
        "student_id": "demo-student-zhangsan",
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
                    "recommendation": f"复习「{question['knowledge_point']}」资源包，并完成 2 道同类变式题。",
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
            {"type": "概念理解", "detail": "对函数返回值、循环终止条件或文件上下文管理存在混淆。"},
            {"type": "边界意识", "detail": "文件不存在、循环少一次/多一次等边界检查不足。"},
        ]
        if wrong_items
        else [{"type": "稳定掌握", "detail": "本次章节练习全部正确，可进入项目实践任务。"}],
        "recommended_resources": [
            {"title": "循环边界专项微课", "knowledge_point": "循环结构", "minutes": 10},
            {"title": "文件读写分步讲义", "knowledge_point": "文件操作", "minutes": 18},
            {"title": "函数封装案例包", "knowledge_point": "函数", "minutes": 15},
        ],
        "next_step": "系统已把薄弱知识点写入学习路径，建议完成错题二刷后再进入项目任务。",
    }


def generate_teacher_workbench(payload: dict[str, Any]) -> dict[str, Any]:
    generate_type = payload.get("type", "lesson_plan")
    course = payload.get("course") or "Python 程序设计"
    chapter = payload.get("chapter") or "循环结构与函数"
    foundation = payload.get("student_foundation") or "基础差异较大"
    goal = payload.get("teaching_goal") or "掌握核心语法并能完成小任务"
    title_map = {
        "lesson_plan": "AI 生成教案",
        "quiz": "AI 生成测验",
        "analysis": "AI 生成学情分析",
    }
    return {
        "type": generate_type,
        "title": title_map.get(generate_type, "AI 教学建议"),
        "course": course,
        "chapter": chapter,
        "input_summary": f"学生基础：{foundation}；教学目标：{goal}",
        "teaching_objectives": [goal, "识别本章薄弱知识点并形成可干预任务", "完成测评、诊断、推荐闭环记录"],
        "key_difficulties": ["循环边界条件", "函数参数与返回值", "文件操作异常兜底"],
        "class_activities": ["5 分钟错题导入", "15 分钟案例拆解", "10 分钟随堂测验", "8 分钟同伴互评"],
        "in_class_quiz": ["判断 while 循环是否会终止", "把重复代码封装为函数", "指出文件读取代码的风险点"],
        "after_class_tasks": ["完成错题二刷", "提交成绩文件分析器最小版本", "在 AI 助教中追问 1 个薄弱知识点"],
        "teaching_suggestions": ["生成内容需教师审核后发布", "高风险学生优先推送补救任务", "测验结果仅作为诊断参考，不直接替代教师评价"],
        "review_required": True,
    }


def get_content_review_items() -> dict[str, Any]:
    return {
        "items": [
            {
                "id": "cr-001",
                "title": "循环结构专项微课脚本",
                "resource_type": "微课脚本",
                "source": "教师工作台生成",
                "risk_tags": ["需核对示例代码", "避免直接给答案"],
                "status": "待审核",
                "review_opinion": "等待课程负责人确认代码样例与教学目标一致。",
            },
            {
                "id": "cr-002",
                "title": "文件操作章节测验",
                "resource_type": "测验",
                "source": "AI 生成测验",
                "risk_tags": ["题目难度需校准"],
                "status": "已通过",
                "review_opinion": "已补充答案解析，可发布到学生端。",
            },
            {
                "id": "cr-003",
                "title": "异常处理学习建议",
                "resource_type": "个性化推荐",
                "source": "练后分析生成",
                "risk_tags": ["诊断结论不可绝对化"],
                "status": "已驳回",
                "review_opinion": "建议语气过于确定，需改为教学辅助建议。",
            },
        ],
        "policy": "AI 生成内容仅作为教学辅助，关键资源、测评结果和干预结论需教师或管理员审核后使用。",
    }


def get_platform_quality() -> dict[str, Any]:
    return {
        "summary": {
            "course_completion_rate": 76.8,
            "average_quiz_score": 82.4,
            "resource_usage_rate": 68.5,
            "weak_point_concentration": 42.0,
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
            {"name": "课程完成率", "value": 76.8, "suggestion": "关注进度低于 50% 的课程。"},
            {"name": "测验均分", "value": 82.4, "suggestion": "保持章节测验难度梯度。"},
            {"name": "资源使用率", "value": 68.5, "suggestion": "提升薄弱知识点资源曝光。"},
            {"name": "薄弱知识点集中度", "value": 42.0, "suggestion": "集中在循环、文件、异常处理，建议专项治理。"},
        ],
        "ai_boundary": "AI 生成内容仅作为教学辅助，关键教学资源、测评结论和学生干预建议必须经教师或管理员审核。",
    }
