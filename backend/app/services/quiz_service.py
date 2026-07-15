from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.models import Course, LearningPath, Quiz, QuizSubmission, StudentProfile
from app.services.dkvmn_tracker import dkvmn_tracker
from app.services.json_utils import dumps, loads
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


DEMO_QUIZZES = [
    {
        "id": "loop-basic-001",
        "course_id": "python-programming",
        "topic": "循环结构",
        "title": "循环结构基础测验",
        "questions": [
            {"id": "q1", "stem": "while 循环避免死循环的关键是什么？", "correctAnswer": "更新条件变量", "concept_id": "while_loop"},
            {"id": "q2", "stem": "break 的作用是什么？", "correctAnswer": "跳出循环", "concept_id": "break_continue"},
            {"id": "q3", "stem": "for range(3) 会执行几次？", "correctAnswer": "3", "concept_id": "for_loop"},
        ],
    }
]


def create_quiz(db: Session, course: Course, profile: StudentProfile | None = None) -> Quiz:
    quiz_json = llm_service.generate_json("quiz", {"course_title": course.title})
    quiz = Quiz(
        course_id=course.id,
        student_profile_id=profile.id if profile else None,
        quiz_json=dumps(quiz_json),
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def get_quiz_list(course_id: int | str | None = None, topic: str | None = None) -> list[dict]:
    rows = DEMO_QUIZZES
    if course_id:
        rows = [item for item in rows if str(item.get("course_id")) == str(course_id) or str(course_id) in {"1", "python-programming"}]
    if topic:
        rows = [item for item in rows if topic in item.get("topic", "") or topic in item.get("title", "")]
    return rows


def map_question_to_concept(question: dict, index: int = 0) -> str:
    return _question_concept(question, index)


def grade_answers(questions: list[dict], answers: dict) -> dict:
    total = len(questions)
    rows = []
    correct_count = 0
    for index, question in enumerate(questions):
        is_correct = _answer_correctness(question, answers, index, 0)
        correct_count += 1 if is_correct else 0
        qid = str(question.get("id") or f"q{index + 1}")
        rows.append(
            {
                "question_id": qid,
                "concept_id": map_question_to_concept(question, index),
                "answer": answers.get(qid) or answers.get(f"q{index + 1}"),
                "correct_answer": question.get("answer") or question.get("correct_answer") or question.get("correctAnswer"),
                "is_correct": is_correct,
            }
        )
    score = round(correct_count / max(total, 1) * 100, 1)
    return {"score": score, "correct_count": correct_count, "total_count": total, "items": rows}


def build_wrong_reason_analysis(graded_items: list[dict]) -> list[dict]:
    reasons = []
    for item in graded_items:
        if item.get("is_correct"):
            continue
        concept = item.get("concept_id")
        reason = "概念理解不稳或关键条件遗漏。"
        if concept == "while_loop":
            reason = "可能遗漏循环条件更新，容易形成死循环。"
        elif concept == "break_continue":
            reason = "可能混淆 break 跳出循环与 continue 跳过本轮。"
        reasons.append({"question_id": item.get("question_id"), "concept_id": concept, "reason": reason})
    return reasons


def update_dkvmn_after_submit(student_id: int | str, graded_items: list[dict]) -> dict:
    state = dkvmn_tracker.state_from_fallback(student_id)
    deltas: dict[str, float] = {}
    for item in graded_items:
        concept = dkvmn_tracker.normalize_concept(item.get("concept_id"))
        before = dkvmn_tracker.predict_mastery(student_id, concept, state)
        state = dkvmn_tracker.update(student_id, concept, bool(item.get("is_correct")), 0.12 if item.get("is_correct") else -0.14, state)
        after = dkvmn_tracker.predict_mastery(student_id, concept, state)
        deltas[concept] = round(after - before, 3)
    dkvmn_tracker.persist_fallback_state(student_id, state)
    cognitive_state = dkvmn_tracker.get_cognitive_state(student_id, state)
    return {
        "dkvmn_updated": True,
        "concept_mastery_delta": deltas,
        "cognitive_state": cognitive_state,
        "weak_concepts": cognitive_state["weak_concepts"],
        "mastery_vector": dkvmn_tracker.get_mastery_vector(student_id, state),
    }


def recommend_path_adjustment(score: float, weak_concepts: list[dict]) -> list[dict]:
    if score >= 85 and not weak_concepts:
        return [{"type": "advance", "title": "进入循环嵌套拓展练习", "reason": "当前测验达标。"}]
    tasks = []
    for item in weak_concepts[:3] or [{"name": "while 循环条件更新", "concept_id": "while_loop"}]:
        tasks.append({"type": "remedial", "title": f"{item.get('name')}专项练习", "concept_id": item.get("concept_id"), "reason": "测验或 DKVMN 显示掌握度偏低。"})
    return tasks


class QuizService:
    get_quiz_list = staticmethod(get_quiz_list)
    grade_answers = staticmethod(grade_answers)
    map_question_to_concept = staticmethod(map_question_to_concept)
    build_wrong_reason_analysis = staticmethod(build_wrong_reason_analysis)
    update_dkvmn_after_submit = staticmethod(update_dkvmn_after_submit)
    recommend_path_adjustment = staticmethod(recommend_path_adjustment)

    def submit_quiz(self, student_id: int | str, quiz_id: int | str, answers: dict) -> dict:
        quiz = next((item for item in DEMO_QUIZZES if str(item["id"]) == str(quiz_id)), DEMO_QUIZZES[0])
        graded = grade_answers(quiz["questions"], answers)
        dkvmn = update_dkvmn_after_submit(student_id, graded["items"])
        weak = dkvmn["weak_concepts"]
        wrong = build_wrong_reason_analysis(graded["items"])
        tasks = recommend_path_adjustment(graded["score"], weak)
        return {
            "student_id": student_id,
            "quiz_id": quiz_id,
            "score": graded["score"],
            "correct_count": graded["correct_count"],
            "total_count": graded["total_count"],
            "concept_mastery_delta": dkvmn["concept_mastery_delta"],
            "weak_concepts": weak,
            "wrong_reason_analysis": wrong,
            "recommended_tasks": tasks,
            "dkvmn_updated": dkvmn["dkvmn_updated"],
            "dkvmn": dkvmn,
        }


def submit_quiz(db: Session, quiz: Quiz, profile: StudentProfile, answers: dict) -> QuizSubmission:
    quiz_json = loads(quiz.quiz_json, {})
    result = llm_service.generate_json(
        "evaluate",
        {
            "quiz": quiz_json,
            "answers": answers,
            "profile": loads(profile.profile_json, {}),
        },
    )
    result["dkvmn"] = _update_dkvmn_from_quiz(db, profile, quiz_json, answers, result)
    submission = QuizSubmission(
        quiz_id=quiz.id,
        student_profile_id=profile.id,
        answers_json=dumps(answers),
        score=float(result.get("score", 0)),
        feedback_json=dumps(result),
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # 测评后自动检测是否需要调整学习路径，并把调整摘要写回反馈 JSON。
    path_adjustment = _try_adjust_path_after_quiz(db, profile, result)
    result["path_adjustment"] = path_adjustment
    submission.feedback_json = dumps(result)
    db.commit()
    db.refresh(submission)

    return submission


def _question_concept(question: dict, index: int) -> str:
    return (
        question.get("concept_id")
        or question.get("conceptId")
        or question.get("knowledge_point_id")
        or question.get("knowledgePoint")
        or question.get("knowledge_point")
        or ["for_loop", "while_loop", "break_continue", "nested_loop", "list_iteration"][index % 5]
    )


def _answer_correctness(question: dict, answers: dict, index: int, fallback_score: float) -> bool:
    qid = str(question.get("id") or question.get("qid") or f"q{index + 1}")
    answer = answers.get(qid)
    if answer is None:
        answer = answers.get(f"q{index + 1}")
    correct_answer = question.get("answer") or question.get("correct_answer") or question.get("correctAnswer")
    if correct_answer is not None and answer is not None:
        return str(answer).strip().lower() == str(correct_answer).strip().lower()
    correctness = answers.get(f"{qid}_correct")
    if correctness is not None:
        return bool(correctness)
    return fallback_score >= 70


def _update_dkvmn_from_quiz(db: Session, profile: StudentProfile, quiz_json: dict, answers: dict, evaluation_result: dict) -> dict:
    questions = quiz_json.get("questions") or quiz_json.get("items") or []
    if not isinstance(questions, list) or not questions:
        questions = [
            {"id": "q1", "concept_id": "for_loop"},
            {"id": "q2", "concept_id": "while_loop"},
            {"id": "q3", "concept_id": "break_continue"},
        ]
    state = dkvmn_tracker.state_from_profile(profile)
    score = float(evaluation_result.get("score", 0) or 0)
    updates = []
    for index, raw_question in enumerate(questions):
        question = raw_question if isinstance(raw_question, dict) else {}
        concept_id = _question_concept(question, index)
        normalized = dkvmn_tracker.normalize_concept(concept_id)
        is_correct = _answer_correctness(question, answers, index, score)
        state = dkvmn_tracker.update(profile.id, normalized, is_correct, score_delta=0.12 if is_correct else -0.12, state=state)
        updates.append(
            {
                "concept_id": normalized,
                "concept_name": dkvmn_tracker.key_memory[normalized]["name"],
                "is_correct": is_correct,
            }
        )
    cognitive_state = dkvmn_tracker.get_cognitive_state(profile.id, state)
    dkvmn_tracker.persist_profile_state(
        db,
        profile,
        state,
        {
            "source_type": "quiz",
            "description": f"测验得分 {score}，已按题目 concept_id 更新 DKVMN 掌握状态。",
            "related_field": "cognitive_state",
            "confidence": 0.84,
        },
    )
    weak = cognitive_state["weak_concepts"]
    evaluation_result["detected_new_weak_points"] = list(
        dict.fromkeys([*(evaluation_result.get("detected_new_weak_points") or []), *[item["name"] for item in weak]])
    )
    evaluation_result["path_adjustment_needed"] = bool(evaluation_result.get("path_adjustment_needed") or score < 90 or weak)
    if not evaluation_result.get("adjustment_reason"):
        evaluation_result["adjustment_reason"] = "DKVMN 识别到薄弱知识点，已触发路径动态调整。"
    return {
        "updates": updates,
        "cognitive_state": cognitive_state,
        "mastery_distribution": dkvmn_tracker.get_mastery_distribution(profile.id, state),
        "dimension_scores": dkvmn_tracker.map_to_profile_dimensions(state),
    }


def _try_adjust_path_after_quiz(db: Session, profile: StudentProfile, evaluation_result: dict) -> dict:
    """测评提交后，若薄弱点发生变化，自动触发路径调整。"""
    if not evaluation_result.get("path_adjustment_needed"):
        return {
            "adjusted": False,
            "reason": evaluation_result.get("adjustment_reason", "测验达标，保留当前学习路径。"),
            "added_tasks": [],
            "difficulty_change": "保持当前难度",
            "recommended_resources": [],
            "next_learning_step": "按当前学习路径继续推进。",
        }

    course = db.query(Course).filter(Course.id == profile.course_id).first()
    if not course:
        return {
            "adjusted": False,
            "reason": "未找到课程，无法自动调整学习路径。",
            "added_tasks": [],
            "difficulty_change": "未调整",
            "recommended_resources": [],
            "next_learning_step": "请先确认学生画像关联课程。",
        }

    path = (
        db.query(LearningPath)
        .filter(LearningPath.student_profile_id == profile.id)
        .order_by(LearningPath.id.desc())
        .first()
    )
    if not path:
        path = LearningPath(
            student_profile_id=profile.id,
            course_id=course.id,
            path_json=dumps({"course_title": course.title, "stages": []}),
        )
        db.add(path)
        db.commit()
        db.refresh(path)

    from app.services.learning_path_service import adjust_learning_path

    detected_new = evaluation_result.get("detected_new_weak_points", [])
    resolved = evaluation_result.get("resolved_weak_points", [])
    reason = evaluation_result.get("adjustment_reason", "测验后自动调整")

    try:
        adjusted_path = adjust_learning_path(
            db,
            path,
            profile,
            course,
            trigger="quiz_submission",
            detected_new=detected_new,
            resolved=resolved,
            reason=reason,
        )
        logger.info(
            "学生 %s 测评后自动调整路径：新增薄弱点 %s，已掌握 %s",
            profile.student_name,
            detected_new,
            resolved,
        )
        added_tasks = [
            f"{point}专项练习" for point in detected_new
        ] or ["while 循环条件更新专项练习"]
        return {
            "adjusted": True,
            "reason": reason,
            "added_tasks": added_tasks,
            "difficulty_change": "降低到基础巩固" if (evaluation_result.get("score") or 0) < 70 else "保持中等难度并追加变式练习",
            "recommended_resources": [
                {"title": "while 循环条件更新专项练习", "type": "quiz"},
                {"title": "break / continue 对比资源", "type": "handout"},
            ],
            "next_learning_step": "先完成 while 循环条件更新练习，再进入 break / continue 对比复盘。",
            "learning_path_id": adjusted_path.id,
        }
    except Exception:
        logger.exception("自动调整学习路径失败，学生 %s", profile.student_name)
        return {
            "adjusted": False,
            "reason": "学习路径自动调整失败，已保留测评结果供人工复核。",
            "added_tasks": [],
            "difficulty_change": "未调整",
            "recommended_resources": [],
            "next_learning_step": "请在学习路径页手动重新规划。",
        }


def list_quizzes(db: Session, course_id: int | None = None) -> list[Quiz]:
    query = db.query(Quiz)
    if course_id:
        query = query.filter(Quiz.course_id == course_id)
    return query.order_by(Quiz.id.desc()).all()
