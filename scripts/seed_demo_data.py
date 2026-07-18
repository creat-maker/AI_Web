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

try:
    from docx import Document  # noqa: E402
except ModuleNotFoundError:  # pragma: no cover - optional export dependency
    Document = None  # type: ignore[assignment]

from app.core.config import settings  # noqa: E402
from app.db.session import Base, SessionLocal, engine  # noqa: E402
from app.models import (  # noqa: E402
    AgentRun,
    AuditLog,
    Course,
    CourseDocument,
    GeneratedResource,
    LearningPath,
    LearningReport,
    Quiz,
    QuizSubmission,
    StudentProfile,
    SystemLog,
    TutorQuestionLog,
)
from app.services.json_utils import dumps, loads  # noqa: E402
from sqlalchemy import inspect, text  # noqa: E402


DEMO_MARK = "EduMind final demo seed v5"
NOW = datetime.utcnow()

CORE_STUDENTS = ["李明", "张三", "李四", "王五"]
CORE_TEACHERS = ["王老师", "陈老师", "张老师"]
CORE_COURSES = ["Python 爬虫基础与实践", "人工智能导论", "数据结构与算法", "Web 开发技术"]
CORE_CLASSES = ["计科大三 1 班", "计科大三 2 班"]


def _stats() -> dict[str, dict[str, int]]:
    return defaultdict(lambda: {"created": 0, "reused": 0})


def _touch(stats: dict[str, dict[str, int]], name: str, created: bool) -> None:
    stats[name]["created" if created else "reused"] += 1


def _created_at(days: int = 0, hours: int = 0) -> datetime:
    return NOW - timedelta(days=days, hours=hours)


def _ensure_demo_file(relative_path: str, content: str) -> Path:
    target = ROOT_DIR / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text(content, encoding="utf-8")
    return target


def _ensure_docx(path: Path, title: str, paragraphs: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if Document is None:
        fallback = path.with_suffix(".md")
        if not fallback.exists():
            fallback.write_text("\n\n".join([f"# {title}", *paragraphs]) + "\n", encoding="utf-8")
        return fallback
    if path.exists():
        return path
    doc = Document()
    doc.add_heading(title, level=1)
    for paragraph in paragraphs:
        doc.add_paragraph(paragraph)
    doc.save(path)
    return path


def ensure_course(db, stats, *, title: str, description: str, subject: str, teacher_name: str) -> Course:
    item = db.query(Course).filter(Course.title == title).first()
    created = False
    if not item:
        item = Course(title=title, description=description, subject=subject, teacher_name=teacher_name, created_at=_created_at(8))
        db.add(item)
        db.commit()
        db.refresh(item)
        created = True
    _touch(stats, "courses", created)
    return item


def ensure_profile(db, stats, course: Course, data: dict[str, Any], created_at: datetime) -> StudentProfile:
    item = db.query(StudentProfile).filter(StudentProfile.course_id == course.id, StudentProfile.student_name == data["student_name"]).first()
    created = False
    if not item:
        item = StudentProfile(
            course_id=course.id,
            owner_user_id=data["owner_user_id"],
            demo_profile_key=data.get("demo_profile_key"),
            student_name=data["student_name"],
            current_level=data["current_level"],
            learning_goal=data["learning_goal"],
            weak_points=dumps(data["weak_points"]),
            learning_preference=data["learning_preference"],
            profile_json=dumps(
                {
                    "demo_seed": DEMO_MARK,
                    "user_id": data["owner_user_id"],
                    "class_name": data["class_name"],
                    "diagnosis": data["diagnosis"],
                    "risk_level": data["risk_level"],
                    "recommended_strategy": data["recommended_strategy"],
                }
            ),
            created_at=created_at,
            updated_at=created_at,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        created = True
    else:
        changed = False
        if not item.owner_user_id:
            item.owner_user_id = data["owner_user_id"]
            changed = True
        if not item.demo_profile_key:
            item.demo_profile_key = data.get("demo_profile_key")
            changed = True
        raw = loads(item.profile_json, {})
        if raw.get("user_id") != data["owner_user_id"]:
            raw["user_id"] = data["owner_user_id"]
            item.profile_json = dumps(raw)
            changed = True
        if changed:
            db.commit()
            db.refresh(item)
    _touch(stats, "student_profiles", created)
    return item


def ensure_document(db, stats, course: Course, filename: str, file_type: str, chunk_count: int) -> None:
    item = db.query(CourseDocument).filter(CourseDocument.course_id == course.id, CourseDocument.filename == filename).first()
    created = False
    demo_file = _ensure_demo_file(
        f"storage/demo/{filename.replace('/', '-')}.txt",
        f"{filename}\n\n课程：{course.title}\n用途：EduMind 本地演示知识库安全样例，不包含敏感信息。\n",
    )
    if not item:
        item = CourseDocument(
            course_id=course.id,
            filename=filename,
            file_path=str(demo_file),
            file_type=file_type,
            parse_status="parsed",
            chunk_count=chunk_count,
            created_at=_created_at(5),
        )
        db.add(item)
        db.commit()
        created = True
    _touch(stats, "course_documents", created)


def ensure_learning_path(db, stats, profile: StudentProfile, course: Course, weak_points: list[str]) -> LearningPath:
    existing = db.query(LearningPath).filter(LearningPath.student_profile_id == profile.id, LearningPath.course_id == course.id).first()
    created = False
    stages = [
        {"name": "概念复盘", "target": f"复盘 {weak_points[0]} 的核心概念与适用场景。", "status": "doing"},
        {"name": "例题拆解", "target": "完成 2 道基础题并标出关键步骤。", "status": "todo"},
        {"name": "迁移应用", "target": "完成一个小项目或综合题，形成学习报告证据。", "status": "todo"},
    ]
    if not existing:
        existing = LearningPath(
            student_profile_id=profile.id,
            course_id=course.id,
            path_json=dumps({"demo_seed": DEMO_MARK, "course_title": course.title, "stages": stages}),
            created_at=_created_at(4),
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)
        created = True
    _touch(stats, "learning_paths", created)
    return existing


def ensure_resource(db, stats, course: Course, profile: StudentProfile, title: str, resource_type: str, content: str) -> None:
    item = db.query(GeneratedResource).filter(
        GeneratedResource.course_id == course.id,
        GeneratedResource.student_profile_id == profile.id,
        GeneratedResource.title == title,
    ).first()
    created = False
    if not item:
        item = GeneratedResource(
            course_id=course.id,
            student_profile_id=profile.id,
            resource_type=resource_type,
            title=title,
            content=content,
            difficulty="分层",
            source_agent="DemoSeedAgent",
            created_at=_created_at(3),
        )
        db.add(item)
        db.commit()
        created = True
    _touch(stats, "generated_resources", created)


def ensure_question_log(db, stats, course: Course, question: str, answer: str, points: list[str], created_at: datetime) -> None:
    item = db.query(TutorQuestionLog).filter(TutorQuestionLog.course_id == course.id, TutorQuestionLog.question == question).first()
    created = False
    if not item:
        item = TutorQuestionLog(
            course_id=course.id,
            question=question,
            answer_json=dumps({"demo_seed": DEMO_MARK, "answer": answer, "confidence": 0.86}),
            contexts_json=dumps(
                [{"source_file": f"{course.title} 演示讲义", "content": "、".join(points), "score": 0.82}]
            ),
            mode="mock-demo",
            created_at=created_at,
        )
        db.add(item)
        db.commit()
        created = True
    _touch(stats, "tutor_question_logs", created)


def ensure_quiz_and_submission(db, stats, course: Course, profile: StudentProfile, title: str, score: float, weak_points: list[str]) -> None:
    quiz = db.query(Quiz).filter(Quiz.course_id == course.id, Quiz.student_profile_id == profile.id).first()
    quiz_created = False
    if not quiz:
        quiz = Quiz(
            course_id=course.id,
            student_profile_id=profile.id,
            quiz_json=dumps(
                {
                    "demo_seed": DEMO_MARK,
                    "title": title,
                    "questions": [
                        {"stem": "判断核心概念适用场景。", "type": "single_choice"},
                        {"stem": "写出关键步骤并说明理由。", "type": "short_answer"},
                    ],
                }
            ),
            created_at=_created_at(5),
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        quiz_created = True
    _touch(stats, "quizzes", quiz_created)

    submission = db.query(QuizSubmission).filter(QuizSubmission.quiz_id == quiz.id, QuizSubmission.student_profile_id == profile.id).first()
    sub_created = False
    if not submission:
        submission = QuizSubmission(
            quiz_id=quiz.id,
            student_profile_id=profile.id,
            answers_json=dumps({"demo_seed": DEMO_MARK, "answers": {"q1": "B", "q2": "分步骤说明"}}),
            score=score,
            feedback_json=dumps(
                {
                    "demo_seed": DEMO_MARK,
                    "score": score,
                    "weak_points": weak_points,
                    "mistake_analysis": f"{profile.student_name} 对 {', '.join(weak_points[:2])} 仍需加强。",
                    "suggestions": ["先复盘概念", "再完成分层练习", "最后用错题解释法复述思路"],
                }
            ),
            created_at=_created_at(3),
        )
        db.add(submission)
        db.commit()
        sub_created = True
    _touch(stats, "quiz_submissions", sub_created)


def ensure_report(db, stats, course: Course, profile: StudentProfile, title: str, weak_points: list[str], score: float) -> LearningReport:
    item = db.query(LearningReport).filter(LearningReport.course_id == course.id, LearningReport.student_profile_id == profile.id, LearningReport.report_title == title).first()
    created = False
    report_path = _ensure_docx(
        settings.path_from_root(settings.report_dir) / f"demo_report_{course.id}_{profile.id}.docx",
        title,
        [
            f"学生：{profile.student_name}",
            f"课程：{course.title}",
            f"薄弱点：{'、'.join(weak_points)}",
            "建议：围绕薄弱点完成分层练习，并在智能答疑中进行追问复盘。",
        ],
    )
    if not item:
        item = LearningReport(
            student_profile_id=profile.id,
            course_id=course.id,
            report_title=title,
            report_path=str(report_path),
            report_json=dumps(
                {
                    "demo_seed": DEMO_MARK,
                    "profile_summary": f"{profile.student_name} 在 {course.title} 中整体表现稳定，仍需针对薄弱点进行补强。",
                    "weak_points": weak_points,
                    "score": score,
                    "references": ["学生画像", "测验结果", "智能答疑记录", "学习路径"],
                    "teaching_suggestions": [{"title": "补强任务", "content": "安排 20 分钟分层练习并要求学生提交错题解释。"}],
                }
            ),
            created_at=_created_at(2),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        created = True
    _touch(stats, "learning_reports", created)
    return item


def ensure_agent_run(db, stats, course: Course, profile: StudentProfile, report: LearningReport, workflow_name: str) -> None:
    item = db.query(AgentRun).filter(AgentRun.course_id == course.id, AgentRun.student_profile_id == profile.id, AgentRun.workflow_name == workflow_name).first()
    created = False
    if not item:
        steps = [
            {"key": "profile", "name": "画像分析", "status": "success", "output_summary": "识别学生水平、目标和薄弱点。"},
            {"key": "retrieve", "name": "知识检索", "status": "success", "output_summary": "召回课程讲义与练习片段。"},
            {"key": "resource", "name": "资源生成", "status": "success", "output_summary": "生成分层练习与讲解材料。"},
            {"key": "path", "name": "路径规划", "status": "success", "output_summary": "更新阶段任务和完成条件。"},
            {"key": "report", "name": "报告生成", "status": "success", "output_summary": "沉淀学习报告和证据链。"},
        ]
        item = AgentRun(
            course_id=course.id,
            student_profile_id=profile.id,
            workflow_name=workflow_name,
            input_json=dumps({"demo_seed": DEMO_MARK, "student_name": profile.student_name, "course_title": course.title}),
            output_json=dumps(
                {
                    "demo_seed": DEMO_MARK,
                    "workflow_summary": {"status": "success", "duration_ms": 1860, "artifact_count": 5},
                    "steps": steps,
                    "artifacts": {"report": {"report_id": report.id, "path": report.report_path}},
                    "report_id": report.id,
                    "report_path": report.report_path,
                }
            ),
            status="success",
            created_at=_created_at(1),
        )
        db.add(item)
        db.commit()
        created = True
    _touch(stats, "agent_runs", created)


def ensure_log(db, stats, *, type: str, title: str, content: str, module: str, level: str = "INFO", related_id: str = "", metadata: dict | None = None) -> None:
    item = db.query(SystemLog).filter(SystemLog.type == type, SystemLog.title == title, SystemLog.related_id == related_id).first()
    created = False
    if not item:
        item = SystemLog(
            type=type,
            title=title,
            content=content,
            level=level,
            module=module,
            user="王老师",
            related_id=related_id,
            duration_ms=int((metadata or {}).get("duration_ms") or 0),
            status="success",
            metadata_json=dumps({"demo_seed": DEMO_MARK, **(metadata or {})}),
            created_at=_created_at(0, 8),
        )
        db.add(item)
        db.commit()
        created = True
    _touch(stats, "system_logs", created)


def ensure_audit_log(db, stats, *, action: str, target_id: str, detail: str, status: str = "success", risk_level: str = "medium", arbitration_status: str = "none", retry_count: int = 0) -> None:
    item = db.query(AuditLog).filter(AuditLog.action == action, AuditLog.target_id == target_id).first()
    created = False
    if not item:
        item = AuditLog(
            actor_id="teacher_001",
            actor_name="王老师",
            actor_role="teacher",
            action=action,
            target_type="demo_governance",
            target_id=target_id,
            status=status,
            detail=detail,
            retry_count=retry_count,
            rule_engine_result=dumps({"dimensions": ["事实准确性", "课程对齐度", "超纲风险", "隐私风险", "不当内容", "幻觉风险", "学段适配"]}),
            xfyun_result=dumps({"status": "not_configured", "message": "讯飞安全 API 未配置，使用本地规则 fallback。"}),
            risk_level=risk_level,
            arbitration_status=arbitration_status,
            created_at=_created_at(0, 6),
        )
        db.add(item)
        db.commit()
        created = True
    _touch(stats, "audit_logs", created)


def seed() -> dict[str, dict[str, int]]:
    print("即将写入 EduMind 第五阶段统一演示数据。脚本不清空数据库，不删除用户数据。")
    Base.metadata.create_all(bind=engine)
    ensure_compatible_columns()
    stats = _stats()
    db = SessionLocal()
    try:
        courses = {
            "python_programming": ensure_course(db, stats, title="Python 程序设计", description="围绕 Python 基础语法、条件分支、循环结构和代码调试组织的程序设计课程。", subject="程序设计", teacher_name="王老师"),
            "python": ensure_course(db, stats, title="Python 爬虫基础与实践", description="围绕 HTTP 请求、网页解析、数据保存和异常处理组织的项目化课程。", subject="计算机科学", teacher_name="王老师"),
            "ai": ensure_course(db, stats, title="人工智能导论", description="介绍机器学习、RAG、智能体和 AI 应用伦理的导论课程。", subject="人工智能", teacher_name="张老师"),
            "ds": ensure_course(db, stats, title="数据结构与算法", description="覆盖栈、队列、树、递归和复杂度分析的算法基础课程。", subject="计算机科学", teacher_name="陈老师"),
            "web": ensure_course(db, stats, title="Web 开发技术", description="覆盖前端基础、接口调用、状态管理和工程化实践的技术课程。", subject="软件工程", teacher_name="张老师"),
        }

        profiles = [
            ensure_profile(db, stats, courses["python_programming"], {"owner_user_id": "student_001", "demo_profile_key": "demo-basic", "student_name": "李明", "class_name": "计算机类 1 班", "current_level": "基础薄弱", "learning_goal": "两周内补齐 Python 循环结构，完成课程作业和基础代码实操", "weak_points": ["while 循环", "循环嵌套", "break / continue"], "learning_preference": "代码实操案例 + 变量变化图解", "diagnosis": "基础概念能跟随讲解理解，但 while 循环终止条件、break/continue 和嵌套循环变量追踪不稳定。", "risk_level": "medium", "recommended_strategy": "先用动画和讲义补基础，再通过代码案例、小项目和分层练习巩固。"}, _created_at(6)),
            ensure_profile(db, stats, courses["python"], {"owner_user_id": "demo_student_zhangsan", "demo_profile_key": "demo-zhangsan", "student_name": "张三", "class_name": "计科大三 1 班", "current_level": "基础薄弱", "learning_goal": "两周内掌握 Python 爬虫基础与 HTTP 请求流程", "weak_points": ["HTTP 请求", "数据解析", "异常处理"], "learning_preference": "案例驱动", "diagnosis": "能跟随示例完成代码，但对请求参数、页面解析和错误定位缺少稳定方法。", "risk_level": "需关注", "recommended_strategy": "先拆解请求、解析、保存三步，再用小型采集任务巩固。"}, _created_at(6)),
            ensure_profile(db, stats, courses["python"], {"owner_user_id": "demo_student_lisi", "demo_profile_key": "demo-lisi", "student_name": "李四", "class_name": "计科大三 1 班", "current_level": "中等", "learning_goal": "完成一个简单网页数据采集小项目", "weak_points": ["HTML 解析", "代码组织", "数据保存"], "learning_preference": "项目制学习", "diagnosis": "语法基础较稳，项目拆解和异常处理仍需要模板支撑。", "risk_level": "稳定", "recommended_strategy": "按请求、解析、保存三个阶段推进小项目。"}, _created_at(5)),
            ensure_profile(db, stats, courses["ds"], {"owner_user_id": "demo_student_wangwu", "demo_profile_key": "demo-wangwu", "student_name": "王五", "class_name": "计科大三 2 班", "current_level": "中等偏弱", "learning_goal": "理解栈、队列、树和递归题的解题套路", "weak_points": ["递归边界", "树遍历", "复杂度分析"], "learning_preference": "图示讲解", "diagnosis": "能背诵定义，但把数据结构映射到题目场景时不够熟练。", "risk_level": "需关注", "recommended_strategy": "用流程图和手算跟踪训练递归与遍历。"}, _created_at(4)),
        ]

        docs = [
            (courses["python_programming"], "Python 程序设计-循环结构讲义.md", "md", 24),
            (courses["python_programming"], "for 循环与 while 循环案例.txt", "txt", 16),
            (courses["python_programming"], "break_continue_课堂练习.md", "md", 12),
            (courses["python"], "Python 爬虫 HTTP 请求讲义.pdf", "pdf", 18),
            (courses["python"], "网页解析与异常处理案例.md", "md", 14),
            (courses["ds"], "递归与树遍历课堂练习.md", "md", 22),
            (courses["ai"], "RAG 与智能体教学案例.docx", "docx", 20),
            (courses["web"], "Web 接口调用与前端工程化清单.pdf", "pdf", 16),
        ]
        for args in docs:
            ensure_document(db, stats, *args)

        for profile in profiles:
            course = db.query(Course).filter(Course.id == profile.course_id).first()
            weak_points = loads(profile.weak_points, [])
            ensure_learning_path(db, stats, profile, course, weak_points)
            ensure_resource(db, stats, course, profile, f"{profile.student_name} 分层练习包", "practice", f"围绕 {', '.join(weak_points)} 生成概念判断、步骤排序和综合应用练习。")
            ensure_resource(db, stats, course, profile, f"{profile.student_name} 个性化讲义", "handout", f"针对 {', '.join(weak_points)} 的个性化讲义，包含概念梳理、关键提醒和最小可运行示例。")
            ensure_resource(db, stats, course, profile, f"{profile.student_name} 案例练习", "example", f"围绕 {', '.join(weak_points)} 的案例练习，标注输入、处理和输出。")
            ensure_resource(db, stats, course, profile, f"{profile.student_name} 知识结构思维导图", "mindmap", f"以 {', '.join(weak_points)} 为核心的知识结构思维导图，展示概念关联和学习路径建议。")
            ensure_quiz_and_submission(db, stats, course, profile, f"{course.title} 阶段测验", 72 if profile.student_name != "李四" else 84, weak_points)
            report = ensure_report(db, stats, course, profile, f"{profile.student_name} {course.title} 阶段学习报告", weak_points, 82.5 if profile.student_name != "王五" else 79.0)
            ensure_agent_run(db, stats, course, profile, report, "full-learning-flow")

            if profile.student_name == "李明":
                profile.dimension_scores = dumps({
                    "知识基础": {"score": 48, "label": "需补强", "explanation": "while 循环和控制语句掌握度偏低。", "confidence": 0.82},
                    "学习节奏": {"score": 62, "label": "稳定", "explanation": "能按任务推进，但遇到代码调试会放慢。", "confidence": 0.76},
                    "学习偏好": {"score": 84, "label": "代码实操偏好", "explanation": "更偏好代码案例和动画。", "confidence": 0.88},
                    "代码实操能力": {"score": 58, "label": "需补强", "explanation": "变量更新和输出判断仍需练习。", "confidence": 0.8},
                    "易错知识点": {"score": 45, "label": "需补强", "explanation": "while、break/continue、循环嵌套为主要易错点。", "confidence": 0.86},
                    "学习风险": {"score": 64, "label": "中风险", "explanation": "存在连续错误但仍能完成基础任务。", "confidence": 0.81},
                })
                profile.cognitive_state = dumps({
                    "model": "lightweight-dkvmn-fallback",
                    "value_memory": {
                        "for_loop": {"mastery": 0.72, "attempts": 3, "correct_streak": 2, "wrong_streak": 0},
                        "while_loop": {"mastery": 0.44, "attempts": 4, "correct_streak": 0, "wrong_streak": 2},
                        "break_continue": {"mastery": 0.49, "attempts": 3, "correct_streak": 0, "wrong_streak": 2},
                        "nested_loop": {"mastery": 0.46, "attempts": 2, "correct_streak": 0, "wrong_streak": 1},
                    },
                    "update_log": [{"concept_id": "while_loop", "is_correct": False, "before": 0.5, "after": 0.44}],
                })
                profile.evidence_items = dumps([
                    {"source_type": "quiz", "description": "循环结构测验 while 题连续错误 2 次。", "related_field": "cognitive_state", "confidence": 0.86},
                    {"source_type": "profile_dialog", "description": "学生表示更喜欢代码案例和图解。", "related_field": "learning_preference", "confidence": 0.82},
                ])
                profile.profile_history = dumps([{"time": NOW.isoformat(), "trigger": "seed_demo", "mastery_average": 0.57}])
                profile.risk_level = "medium"
                db.commit()

        questions = [
            (courses["python"], "爬虫请求失败时应该先检查什么？", "先检查 URL、状态码、请求头和网络连通性，再看页面是否需要登录或存在反爬限制。", ["HTTP 请求", "状态码", "请求头"]),
            (courses["python"], "with open 为什么更适合读取文件？", "with open 可以自动关闭文件，减少资源泄露，并让异常场景更安全。", ["文件操作", "异常处理"]),
            (courses["ds"], "如何复习递归边界？", "先写清递归含义、终止条件和状态变化，再用小规模样例手动跟踪调用栈。", ["递归边界", "调用栈"]),
            (courses["ai"], "RAG 为什么需要向量检索？", "向量检索能把问题和文档片段映射到语义空间，帮助模型找到更相关的课程依据。", ["RAG", "向量检索"]),
            (courses["web"], "前端调用接口时最常见的问题是什么？", "常见问题包括跨域、请求方法不匹配、参数格式错误和接口状态码处理不完整。", ["接口调用", "跨域", "状态码"]),
        ]
        for index, args in enumerate(questions):
            ensure_question_log(db, stats, *args, created_at=_created_at(2, index))

        business_events = [
            ("profile_generated", "画像生成", "张三画像已生成并写入学习闭环。"),
            ("resource_generated", "资源包生成", "已生成 Python 爬虫基础与实践分层资源包。"),
            ("resource_added_to_path", "资源加入路径", "资源包已加入张三学习路径。"),
            ("path_updated", "学习路径更新", "根据测验结果更新学习路径。"),
            ("teacher_intervention_created", "教师干预", "王老师为张三创建补强干预。"),
            ("task_assigned", "任务布置", "补强任务已同步到学生端。"),
            ("quiz_completed", "测验完成", "张三完成阶段测验并沉淀薄弱点。"),
            ("question_answered", "智能答疑", "智能答疑返回带引用的回答。"),
            ("admin_review_completed", "管理员审核", "管理员完成报告审核演示。"),
        ]
        for event_type, title, content in business_events:
            ensure_log(
                db,
                stats,
                type="business_event",
                title=title,
                content=content,
                module="BusinessEvent",
                related_id=f"seed-{event_type}",
                metadata={"event_type": event_type, "target_id": f"seed-{event_type}", "related_student": "张三", "related_course": "Python 爬虫基础与实践"},
            )

        ensure_log(db, stats, type="qa", title="智能答疑引用生成", content="学生围绕 Python 爬虫请求失败提问，系统生成带引用的引导式回答。", module="TutorChat", level="SUCCESS", related_id="demo-qa-001")
        ensure_log(db, stats, type="agent_workflow", title="Agent 学习闭环运行", content="画像、检索、资源、路径和报告节点完成一次模拟运行。", module="AgentWorkflow", level="SUCCESS", related_id="demo-agent-001")
        ensure_log(db, stats, type="report_generation", title="学习报告生成完成", content="报告中心根据画像、测验、问答和 Agent 产物生成阶段报告。", module="ReportCenter", level="SUCCESS", related_id="demo-report-001")
        ensure_audit_log(db, stats, action="content_rule_check", target_id="li-ming-rag-answer", detail="RAG 回答完成 7 维规则审核，课程对齐度合格。", risk_level="low")
        ensure_audit_log(db, stats, action="audit_retry", target_id="li-ming-resource-pack", detail="资源包第一次审核提示引用说明不足，已回流 ResourceAgent 修订。", status="needs_review", risk_level="medium", arbitration_status="none", retry_count=1)
        ensure_audit_log(db, stats, action="teacher_arbitration_decision", target_id="li-ming-path-adjustment", detail="教师同意中风险路径补弱调整，允许推送给学生。", status="approve", risk_level="medium", arbitration_status="completed")

        db.commit()
        return dict(stats)
    finally:
        db.close()


def ensure_compatible_columns() -> None:
    table_columns = {
        "student_profiles": {
            "owner_user_id": "VARCHAR(100)",
            "demo_profile_key": "VARCHAR(100)",
            "dimension_scores": "TEXT",
            "evidence_items": "TEXT",
            "cognitive_state": "TEXT",
            "profile_history": "TEXT",
            "risk_level": "VARCHAR(50)",
        },
        "learning_paths": {
            "adjustment_log": "TEXT",
            "current_difficulty": "VARCHAR(50)",
            "inserted_tasks": "TEXT",
            "teacher_arbitration_required": "BOOLEAN DEFAULT 0 NOT NULL",
        },
        "generated_resources": {
            "recommend_reason": "TEXT",
            "file_path": "VARCHAR(500)",
            "resource_url": "VARCHAR(500)",
            "preview_type": "VARCHAR(50)",
            "rating": "FLOAT",
            "generation_status": "VARCHAR(50) DEFAULT 'generated' NOT NULL",
            "audit_status": "VARCHAR(50) DEFAULT 'pending_review' NOT NULL",
        },
        "audit_logs": {
            "retry_count": "INTEGER DEFAULT 0 NOT NULL",
            "xfyun_result": "TEXT",
            "rule_engine_result": "TEXT",
            "risk_level": "VARCHAR(50)",
            "arbitration_status": "VARCHAR(50)",
        },
        "agent_runs": {
            "run_id": "VARCHAR(100)",
            "current_node": "VARCHAR(100)",
            "state": "TEXT",
            "messages": "TEXT",
            "audit_result": "TEXT",
            "retry_count": "INTEGER DEFAULT 0 NOT NULL",
            "teacher_arbitration_result": "TEXT",
            "started_at": "DATETIME",
            "finished_at": "DATETIME",
        },
    }
    with engine.connect() as conn:
        insp = inspect(engine)
        tables = set(insp.get_table_names())
        for table_name, columns in table_columns.items():
            if table_name not in tables:
                continue
            existing = {col["name"] for col in insp.get_columns(table_name)}
            for column_name, column_type in columns.items():
                if column_name not in existing:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
        conn.commit()


def print_stats(stats: dict[str, dict[str, int]]) -> None:
    print("\n演示数据初始化完成：")
    print(f"- 学生：{'、'.join(CORE_STUDENTS)}")
    print(f"- 教师：{'、'.join(CORE_TEACHERS)}")
    print(f"- 课程：{'、'.join(CORE_COURSES)}")
    print(f"- 班级：{'、'.join(CORE_CLASSES)}")
    for name in sorted(stats):
        row = stats[name]
        print(f"- {name}: 创建 {row['created']}，复用 {row['reused']}")


def main() -> None:
    print_stats(seed())


if __name__ == "__main__":
    main()
