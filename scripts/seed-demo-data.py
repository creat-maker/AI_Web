from __future__ import annotations

import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from docx import Document  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.db.session import Base, SessionLocal, engine  # noqa: E402
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
from app.services.json_utils import dumps, loads  # noqa: E402


DEMO_MARK = "P2-3 Demo Seed"
NOW = datetime.utcnow()


def _stats() -> dict[str, dict[str, int]]:
    return defaultdict(lambda: {"created": 0, "reused": 0})


def _touch_stat(stats: dict[str, dict[str, int]], name: str, created: bool) -> None:
    stats[name]["created" if created else "reused"] += 1


def _created_at(days: int, hours: int = 0) -> datetime:
    return NOW - timedelta(days=days, hours=hours)


def _ensure_demo_file(relative_path: str, content: str) -> Path:
    target = ROOT_DIR / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text(content, encoding="utf-8")
    return target


def _ensure_docx(path: Path, title: str, paragraphs: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    doc = Document()
    doc.add_heading(title, level=1)
    for paragraph in paragraphs:
        doc.add_paragraph(paragraph)
    doc.save(path)


def _json_has_demo_marker(value: str | None) -> bool:
    data = loads(value, {})
    return isinstance(data, dict) and data.get("demo_seed") == DEMO_MARK


def ensure_course(db, stats, data: dict[str, str]) -> Course:
    course = db.query(Course).filter(Course.title == data["title"]).first()
    created = False
    if not course:
        course = Course(**data, created_at=_created_at(7))
        db.add(course)
        db.commit()
        db.refresh(course)
        created = True
    _touch_stat(stats, "courses", created)
    return course


def ensure_profile(db, stats, course: Course, data: dict[str, Any], created_at: datetime) -> StudentProfile:
    profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.course_id == course.id, StudentProfile.student_name == data["student_name"])
        .first()
    )
    created = False
    if not profile:
        profile = StudentProfile(
            course_id=course.id,
            student_name=data["student_name"],
            current_level=data["current_level"],
            learning_goal=data["learning_goal"],
            weak_points=dumps(data["weak_points"]),
            learning_preference=data["learning_preference"],
            profile_json=dumps(
                {
                    "demo_seed": DEMO_MARK,
                    "diagnosis": data["diagnosis"],
                    "risk_level": data["risk_level"],
                    "recommended_strategy": data["recommended_strategy"],
                }
            ),
            created_at=created_at,
            updated_at=created_at,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        created = True
    _touch_stat(stats, "student_profiles", created)
    return profile


def ensure_document(db, stats, course: Course, filename: str, file_type: str, chunk_count: int, created_at: datetime) -> CourseDocument:
    item = (
        db.query(CourseDocument)
        .filter(CourseDocument.course_id == course.id, CourseDocument.filename == filename)
        .first()
    )
    created = False
    demo_file = _ensure_demo_file(
        f"storage/demo/{filename.replace(':', '-').replace('：', '-')}.txt",
        f"{filename}\n\n{DEMO_MARK}\n课程：{course.title}\n用于本地演示的知识库元信息占位文本，不包含敏感信息。\n",
    )
    if not item:
        item = CourseDocument(
            course_id=course.id,
            filename=filename,
            file_path=str(demo_file),
            file_type=file_type,
            parse_status="parsed",
            chunk_count=chunk_count,
            created_at=created_at,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        created = True
    _touch_stat(stats, "course_documents", created)
    return item


def ensure_learning_path(db, stats, profile: StudentProfile, course: Course, stages: list[dict[str, str]]) -> LearningPath:
    path = (
        db.query(LearningPath)
        .filter(LearningPath.student_profile_id == profile.id, LearningPath.course_id == course.id)
        .all()
    )
    existing = next((item for item in path if _json_has_demo_marker(item.path_json)), None)
    created = False
    if not existing:
        existing = LearningPath(
            student_profile_id=profile.id,
            course_id=course.id,
            path_json=dumps({"demo_seed": DEMO_MARK, "stages": stages}),
            created_at=_created_at(4),
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)
        created = True
    _touch_stat(stats, "learning_paths", created)
    return existing


def ensure_resource(db, stats, course: Course, profile: StudentProfile, title: str, resource_type: str, content: str) -> GeneratedResource:
    existing = (
        db.query(GeneratedResource)
        .filter(
            GeneratedResource.course_id == course.id,
            GeneratedResource.student_profile_id == profile.id,
            GeneratedResource.title == title,
        )
        .first()
    )
    created = False
    if not existing:
        existing = GeneratedResource(
            course_id=course.id,
            student_profile_id=profile.id,
            resource_type=resource_type,
            title=title,
            content=content,
            difficulty="中等",
            source_agent="DemoSeedAgent",
            created_at=_created_at(3),
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)
        created = True
    _touch_stat(stats, "generated_resources", created)
    return existing


def ensure_question_log(
    db,
    stats,
    course: Course,
    question: str,
    answer: dict[str, Any],
    contexts: list[dict[str, Any]],
    created_at: datetime,
) -> TutorQuestionLog:
    existing = (
        db.query(TutorQuestionLog)
        .filter(TutorQuestionLog.course_id == course.id, TutorQuestionLog.question == question)
        .first()
    )
    created = False
    if not existing:
        existing = TutorQuestionLog(
            course_id=course.id,
            question=question,
            answer_json=dumps({"demo_seed": DEMO_MARK, **answer}),
            contexts_json=dumps(contexts),
            mode="mock-demo",
            created_at=created_at,
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)
        created = True
    _touch_stat(stats, "tutor_question_logs", created)
    return existing


def ensure_quiz(db, stats, course: Course, profile: StudentProfile, title: str, questions: list[dict[str, Any]]) -> Quiz:
    quizzes = (
        db.query(Quiz)
        .filter(Quiz.course_id == course.id, Quiz.student_profile_id == profile.id)
        .all()
    )
    existing = next((item for item in quizzes if loads(item.quiz_json, {}).get("title") == title), None)
    created = False
    if not existing:
        existing = Quiz(
            course_id=course.id,
            student_profile_id=profile.id,
            quiz_json=dumps({"demo_seed": DEMO_MARK, "title": title, "questions": questions}),
            created_at=_created_at(5),
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)
        created = True
    _touch_stat(stats, "quizzes", created)
    return existing


def ensure_submission(
    db,
    stats,
    quiz: Quiz,
    profile: StudentProfile,
    score: float,
    weak_points: list[str],
    created_at: datetime,
) -> QuizSubmission:
    existing = (
        db.query(QuizSubmission)
        .filter(QuizSubmission.quiz_id == quiz.id, QuizSubmission.student_profile_id == profile.id)
        .first()
    )
    created = False
    if not existing:
        existing = QuizSubmission(
            quiz_id=quiz.id,
            student_profile_id=profile.id,
            answers_json=dumps({"demo_seed": DEMO_MARK, "answers": {"q1": "B", "q2": "递归边界", "q3": "向量检索"}}),
            score=score,
            feedback_json=dumps(
                {
                    "demo_seed": DEMO_MARK,
                    "score": score,
                    "weak_points": weak_points,
                    "mistake_analysis": f"{profile.student_name} 对 {', '.join(weak_points[:3])} 仍需加强。",
                    "suggestions": ["先复盘概念边界", "再完成 3 道分层练习", "最后用错题解释法复述思路"],
                }
            ),
            created_at=created_at,
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)
        created = True
    _touch_stat(stats, "quiz_submissions", created)
    return existing


def ensure_report(
    db,
    stats,
    course: Course,
    profile: StudentProfile,
    title: str,
    summary: dict[str, Any],
    created_at: datetime,
) -> LearningReport:
    existing = (
        db.query(LearningReport)
        .filter(LearningReport.course_id == course.id, LearningReport.report_title == title)
        .first()
    )
    created = False
    report_path = settings.path_from_root(settings.report_dir) / f"demo_report_{course.id}_{profile.id}.docx"
    _ensure_docx(
        report_path,
        title,
        [
            f"学生：{profile.student_name}",
            f"课程：{course.title}",
            summary.get("profile_summary", "阶段学习表现稳定。"),
            f"薄弱点：{summary.get('weak_points', '暂无')}",
            "本文件由演示数据脚本生成，不包含敏感信息。",
        ],
    )
    if not existing:
        existing = LearningReport(
            student_profile_id=profile.id,
            course_id=course.id,
            report_title=title,
            report_path=str(report_path),
            report_json=dumps({"demo_seed": DEMO_MARK, **summary}),
            created_at=created_at,
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)
        created = True
    _touch_stat(stats, "learning_reports", created)
    return existing


def _workflow_steps(status: str, failed_step: str | None = None) -> list[dict[str, Any]]:
    names = [
        ("task_receive", "任务接收", "校验课程、学生与学习目标。"),
        ("intent_recognition", "意图识别", "识别为个性化学习支持任务。"),
        ("knowledge_retrieval", "知识库检索", "召回课程讲义与案例片段。"),
        ("answer_generation", "答案生成", "生成结构化答疑或讲解。"),
        ("learning_analysis", "学情分析", "汇总测评结果和薄弱知识点。"),
        ("teaching_advice", "教学建议", "生成分层练习和教师干预建议。"),
        ("report_generation", "报告生成", "沉淀为学习报告和展示入口。"),
    ]
    rows = []
    for index, (key, name, output) in enumerate(names):
        step_status = "failed" if failed_step == key else "success" if status == "success" else "waiting"
        rows.append(
            {
                "key": key,
                "name": name,
                "status": step_status,
                "input_summary": f"演示输入 #{index + 1}",
                "output_summary": output if step_status != "failed" else "演示数据中的可恢复失败，用于日志中心错误态展示。",
                "duration_ms": 220 + index * 95,
                "duration": f"{220 + index * 95}ms",
                "error": "知识库命中不足，已建议补充课程资料。" if step_status == "failed" else "",
            }
        )
    return rows


def ensure_agent_run(
    db,
    stats,
    course: Course,
    profile: StudentProfile,
    workflow_name: str,
    task_name: str,
    status: str,
    report: LearningReport | None,
    created_at: datetime,
) -> AgentRun:
    runs = (
        db.query(AgentRun)
        .filter(AgentRun.course_id == course.id, AgentRun.student_profile_id == profile.id, AgentRun.workflow_name == workflow_name)
        .all()
    )
    existing = next((item for item in runs if _json_has_demo_marker(item.input_json)), None)
    created = False
    failed_step = "knowledge_retrieval" if status == "failed" else None
    steps = _workflow_steps(status, failed_step)
    duration_ms = sum(item["duration_ms"] for item in steps)
    artifacts = {
        "tutor_answer": {"title": "答疑结果", "summary": "已生成结构化讲解，并关联课程知识片段。"},
        "knowledge_references": {
            "title": "知识库引用",
            "count": 3,
            "items": [
                {"source": f"{course.title} 讲义", "content": "命中概念解释、典型例题和复习建议。"},
                {"source": "课堂案例", "content": "用于说明从问题到解法的步骤。"},
            ],
        },
        "weak_points": {"title": "薄弱点分析", "summary": "需要加强概念边界、步骤拆解和迁移应用。"},
        "teaching_suggestions": {
            "title": "教学建议",
            "items": [
                {"title": "课前复盘", "content": "用 5 分钟概念卡片回顾核心知识点。"},
                {"title": "课堂练习", "content": "安排一题基础题和一题迁移题。"},
            ],
        },
        "report": {
            "title": "报告入口",
            "report_id": report.id if report else None,
            "path": report.report_path if report else "",
            "entry": f"/reports?report_id={report.id}" if report else "/reports",
        },
    }
    output = {
        "demo_seed": DEMO_MARK,
        "workflow_summary": {
            "status": status,
            "duration_ms": duration_ms,
            "duration": f"{duration_ms / 1000:.1f}s",
            "success_rate": 100 if status == "success" else 0,
            "artifact_count": 7 if status == "success" else 2,
        },
        "steps": steps,
        "artifacts": artifacts,
        "report_id": report.id if report else None,
        "report_path": report.report_path if report else "",
        "error": "知识库命中不足，已建议补充课程资料。" if status == "failed" else "",
    }
    if not existing:
        existing = AgentRun(
            course_id=course.id,
            student_profile_id=profile.id,
            workflow_name=workflow_name,
            input_json=dumps({"demo_seed": DEMO_MARK, "learning_goal": task_name, "student_name": profile.student_name}),
            output_json=dumps(output),
            status=status,
            created_at=created_at,
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)
        created = True
    _touch_stat(stats, "agent_runs", created)
    return existing


def seed() -> dict[str, dict[str, int]]:
    print("即将写入 EduMind 演示数据：课程、学生画像、知识库记录、问答日志、测评、报告和 Agent 运行记录。")
    print("脚本不会清空数据库，不会删除用户数据，不会写入真实 API Key。")

    Base.metadata.create_all(bind=engine)
    stats = _stats()
    db = SessionLocal()
    try:
        courses = {
            "python": ensure_course(
                db,
                stats,
                {
                    "title": "Python 程序设计",
                    "description": "面向零基础学生的 Python 语法、函数、文件操作和爬虫入门课程。",
                    "subject": "计算机基础",
                    "teacher_name": "李老师",
                },
            ),
            "ds": ensure_course(
                db,
                stats,
                {
                    "title": "数据结构与算法",
                    "description": "覆盖栈、队列、树、递归和复杂度分析的算法基础课程。",
                    "subject": "计算机科学",
                    "teacher_name": "王老师",
                },
            ),
            "ai": ensure_course(
                db,
                stats,
                {
                    "title": "人工智能导论",
                    "description": "介绍机器学习、RAG、智能体和 AI 应用伦理的导论课程。",
                    "subject": "人工智能",
                    "teacher_name": "陈老师",
                },
            ),
        }

        profiles = [
            ensure_profile(
                db,
                stats,
                courses["python"],
                {
                    "student_name": "张明",
                    "current_level": "基础薄弱",
                    "learning_goal": "两周内掌握函数、模块和文件读写的基本用法",
                    "weak_points": ["函数参数", "文件操作", "异常处理"],
                    "learning_preference": "案例驱动",
                    "diagnosis": "能跟随示例完成代码，但对参数传递和错误定位缺少稳定方法。",
                    "risk_level": "需关注",
                    "recommended_strategy": "先用短例题建立概念，再用调试任务巩固。",
                },
                _created_at(6),
            ),
            ensure_profile(
                db,
                stats,
                courses["python"],
                {
                    "student_name": "刘欣",
                    "current_level": "中等",
                    "learning_goal": "完成一个简单网页数据采集小项目",
                    "weak_points": ["HTTP 请求", "HTML 解析", "代码组织"],
                    "learning_preference": "项目制学习",
                    "diagnosis": "语法基础较稳，项目拆解和异常处理还需要模板支撑。",
                    "risk_level": "稳定",
                    "recommended_strategy": "按请求、解析、保存三个阶段推进小项目。",
                },
                _created_at(5, 3),
            ),
            ensure_profile(
                db,
                stats,
                courses["ds"],
                {
                    "student_name": "赵一航",
                    "current_level": "中等偏弱",
                    "learning_goal": "理解栈、队列、树和递归题的解题套路",
                    "weak_points": ["递归边界", "树遍历", "复杂度分析"],
                    "learning_preference": "图示讲解",
                    "diagnosis": "能背诵定义，但把数据结构映射到题目场景时不够熟练。",
                    "risk_level": "需关注",
                    "recommended_strategy": "用流程图和手算跟踪训练递归与遍历。",
                },
                _created_at(4, 2),
            ),
            ensure_profile(
                db,
                stats,
                courses["ai"],
                {
                    "student_name": "周雨婷",
                    "current_level": "入门",
                    "learning_goal": "理解 RAG、向量检索和智能体工作流的核心概念",
                    "weak_points": ["向量检索", "提示词设计", "Agent 编排"],
                    "learning_preference": "概念类比",
                    "diagnosis": "对 AI 应用感兴趣，但需要把抽象概念和教学案例联系起来。",
                    "risk_level": "稳定",
                    "recommended_strategy": "通过问答系统案例理解 RAG 和 Agent 分工。",
                },
                _created_at(3, 6),
            ),
            ensure_profile(
                db,
                stats,
                courses["ds"],
                {
                    "student_name": "陈思源",
                    "current_level": "较好",
                    "learning_goal": "提升算法题表达和复杂度分析能力",
                    "weak_points": ["复杂度证明", "边界条件", "题解表达"],
                    "learning_preference": "挑战题训练",
                    "diagnosis": "解题速度较快，但解释过程容易跳步。",
                    "risk_level": "优秀提升",
                    "recommended_strategy": "增加题解复述和复杂度对比训练。",
                },
                _created_at(2, 8),
            ),
        ]

        documents = [
            (courses["python"], "Python 函数与模块讲义.pdf", "pdf", 18, _created_at(6)),
            (courses["python"], "Python 文件操作与异常处理.md", "md", 12, _created_at(5)),
            (courses["ds"], "数据结构：栈、队列与树.md", "md", 22, _created_at(4)),
            (courses["ds"], "递归与复杂度分析课堂练习.txt", "txt", 10, _created_at(3)),
            (courses["ai"], "RAG 与智能体教学案例.docx", "docx", 20, _created_at(2)),
            (courses["ai"], "向量检索与提示词设计讲义.md", "md", 14, _created_at(1, 4)),
        ]
        for args in documents:
            ensure_document(db, stats, *args)

        path_stages = [
            {"name": "概念复盘", "target": "用自己的话解释核心概念和适用场景。"},
            {"name": "例题拆解", "target": "完成两道基础题并标出关键步骤。"},
            {"name": "迁移应用", "target": "把方法迁移到一个小项目或综合题。"},
        ]
        for profile in profiles:
            course = db.query(Course).filter(Course.id == profile.course_id).first()
            ensure_learning_path(db, stats, profile, course, path_stages)
            ensure_resource(
                db,
                stats,
                course,
                profile,
                f"{profile.student_name} 分层练习包",
                "practice",
                "包含概念判断、步骤排序和综合应用三类练习，用于课后巩固。",
            )

        questions = [
            (courses["python"], "Python 函数参数如何理解？", "函数参数可以理解为函数运行时接收的输入，先区分形参和实参，再观察默认值和关键字参数。", ["函数参数", "默认参数"], _created_at(6, 2)),
            (courses["python"], "模块导入时 from import 和 import 有什么区别？", "import 保留模块命名空间，from import 直接导入成员；课堂建议优先使用 import 提升可读性。", ["模块导入", "命名空间"], _created_at(5, 5)),
            (courses["python"], "读取文件时为什么要使用 with open？", "with open 能自动关闭文件，减少忘记 close 造成的资源泄漏，也让异常场景更安全。", ["文件操作", "异常处理"], _created_at(4, 1)),
            (courses["python"], "爬虫请求失败时应该先检查什么？", "先检查 URL、状态码、请求头和网络连通性，再看页面是否需要登录或反爬限制。", ["HTTP 请求", "调试"], _created_at(3, 6)),
            (courses["ds"], "栈和队列有什么区别？", "栈是后进先出，适合括号匹配和递归模拟；队列是先进先出，适合 BFS 和排队调度。", ["栈", "队列"], _created_at(6, 6)),
            (courses["ds"], "学生如何复习递归？", "先写清递归含义、终止条件和状态变化，再用小规模样例手动跟踪调用栈。", ["递归边界", "调用栈"], _created_at(2, 4)),
            (courses["ds"], "二叉树遍历为什么容易混淆？", "前中后序的差异在访问根节点的时机，建议用同一棵树画出三种访问序列对比。", ["树遍历", "递归"], _created_at(1, 8)),
            (courses["ai"], "RAG 为什么需要向量检索？", "向量检索能把问题和文档片段映射到语义空间，帮助模型找到更相关的课程依据。", ["RAG", "向量检索"], _created_at(5, 1)),
            (courses["ai"], "智能体工作流和普通问答有什么不同？", "智能体工作流会拆分任务并沉淀中间产物，普通问答通常只返回一次回答。", ["Agent 编排", "任务拆解"], _created_at(3, 2)),
            (courses["ai"], "提示词设计应该关注哪些要素？", "需要明确角色、任务、输入约束、输出格式和评价标准，避免开放式模糊指令。", ["提示词设计", "输出格式"], _created_at(1, 2)),
        ]
        for course, question, answer, points, created_at in questions:
            ensure_question_log(
                db,
                stats,
                course,
                question,
                {
                    "answer": answer,
                    "steps": ["定位概念", "结合课程片段解释", "给出练习建议"],
                    "confidence": 0.86,
                },
                [
                    {
                        "source_file": f"{course.title} 演示讲义",
                        "content": f"{'、'.join(points)} 相关知识片段，用于支撑答疑解释。",
                        "score": 0.82,
                    }
                ],
                created_at,
            )

        quiz_specs = [
            (profiles[0], courses["python"], "Python 基础诊断测验", 72, ["函数参数", "异常处理"], _created_at(5, 4)),
            (profiles[1], courses["python"], "Python 爬虫入门测验", 84, ["HTML 解析", "代码组织"], _created_at(3, 3)),
            (profiles[2], courses["ds"], "数据结构递归测验", 68, ["递归边界", "树遍历"], _created_at(4, 5)),
            (profiles[3], courses["ai"], "人工智能导论概念测验", 88, ["向量检索", "Agent 编排"], _created_at(2, 2)),
            (profiles[4], courses["ds"], "算法复杂度提升测验", 91, ["复杂度证明", "题解表达"], _created_at(1, 3)),
        ]
        for profile, course, title, score, weak_points, created_at in quiz_specs:
            quiz = ensure_quiz(
                db,
                stats,
                course,
                profile,
                title,
                [
                    {"stem": "请判断核心概念的适用场景。", "type": "single_choice"},
                    {"stem": "请写出关键步骤并说明理由。", "type": "short_answer"},
                    {"stem": "请完成一个小型迁移应用题。", "type": "application"},
                ],
            )
            ensure_submission(db, stats, quiz, profile, score, weak_points, created_at)

        reports = [
            ensure_report(
                db,
                stats,
                courses["python"],
                profiles[0],
                "Python 阶段学习诊断报告",
                {
                    "profile_summary": "张明已能完成基础语法练习，但函数参数和异常处理仍需用例题巩固。",
                    "weak_points": ["函数参数", "异常处理", "文件读写"],
                    "stages": path_stages,
                    "evaluation_summary": "最近测验得分 72，主要失分来自参数传递和错误定位。",
                    "teaching_suggestions": [
                        {"title": "参数专项", "content": "用 4 个短函数对比位置参数、关键字参数和默认参数。"},
                        {"title": "调试训练", "content": "安排一次文件读取异常定位练习。"},
                    ],
                    "references": ["学生画像", "Python 基础诊断测验", "智能答疑记录"],
                    "score": 82.5,
                },
                _created_at(3, 1),
            ),
            ensure_report(
                db,
                stats,
                courses["ds"],
                profiles[2],
                "数据结构薄弱点分析报告",
                {
                    "profile_summary": "赵一航对栈和队列定义掌握较好，但递归边界和树遍历迁移不足。",
                    "weak_points": ["递归边界", "树遍历", "复杂度分析"],
                    "stages": path_stages,
                    "evaluation_summary": "建议先用图示和手算跟踪补齐递归理解。",
                    "teaching_suggestions": [
                        {"title": "递归跟踪", "content": "每题要求画出前三层调用栈。"},
                        {"title": "树遍历对比", "content": "固定一棵树对比前中后序结果。"},
                    ],
                    "references": ["数据结构递归测验", "知识库讲义", "Agent 工作流"],
                    "score": 79.0,
                },
                _created_at(2, 5),
            ),
            ensure_report(
                db,
                stats,
                courses["ai"],
                profiles[3],
                "AI 导论学习建议报告",
                {
                    "profile_summary": "周雨婷能理解 AI 应用场景，但 RAG 与智能体编排还需要案例化讲解。",
                    "weak_points": ["向量检索", "提示词设计", "Agent 编排"],
                    "stages": path_stages,
                    "evaluation_summary": "概念题表现稳定，建议增加项目式案例。",
                    "teaching_suggestions": [
                        {"title": "RAG 案例", "content": "用课程问答系统解释检索增强生成流程。"},
                        {"title": "Agent 分工", "content": "画出规划、检索、生成、评价四类节点。"},
                    ],
                    "references": ["人工智能导论概念测验", "RAG 与智能体教学案例", "问答日志"],
                    "score": 87.5,
                },
                _created_at(1, 1),
            ),
            ensure_report(
                db,
                stats,
                courses["python"],
                profiles[1],
                "Python 爬虫项目复盘报告",
                {
                    "profile_summary": "刘欣能完成请求和解析流程，下一步应加强项目结构和错误处理。",
                    "weak_points": ["代码组织", "异常处理", "数据保存"],
                    "stages": path_stages,
                    "evaluation_summary": "项目拆解能力提升明显，适合进入小型综合任务。",
                    "teaching_suggestions": [{"title": "项目模板", "content": "提供请求、解析、存储三个模块的文件结构模板。"}],
                    "references": ["Python 爬虫入门测验", "课程知识库", "教师分析"],
                    "score": 85.0,
                },
                _created_at(0, 8),
            ),
        ]

        agent_specs = [
            (courses["python"], profiles[0], "full-learning-flow", "Python 函数与文件操作完整学习流", "success", reports[0], _created_at(2, 1)),
            (courses["python"], profiles[1], "tutor-answer-flow", "Python 爬虫智能答疑流", "success", reports[3], _created_at(1, 12)),
            (courses["ds"], profiles[2], "learning-analysis-flow", "数据结构递归学情分析流", "success", reports[1], _created_at(1, 6)),
            (courses["ai"], profiles[3], "report-generation-flow", "AI 导论报告生成流", "success", reports[2], _created_at(0, 5)),
            (courses["ai"], profiles[3], "knowledge-retrieval-diagnosis-flow", "RAG 知识库检索诊断流", "failed", None, _created_at(0, 2)),
        ]
        for args in agent_specs:
            ensure_agent_run(db, stats, *args)

        db.commit()
        return dict(stats)
    finally:
        db.close()


def print_stats(stats: dict[str, dict[str, int]]) -> None:
    print("\n演示数据初始化完成：")
    for name in sorted(stats):
        row = stats[name]
        print(f"- {name}: 创建 {row['created']}，复用 {row['reused']}")


if __name__ == "__main__":
    print_stats(seed())
