from __future__ import annotations

from typing import Any


class MockLLM:
    mode_label = "演示 mock 模式"

    def generate_profile(self, payload: dict[str, Any]) -> dict[str, Any]:
        weak_points = payload.get("weak_points") or []
        return {
            "student_name": payload.get("student_name", "学生"),
            "current_level": payload.get("current_level", "待评估"),
            "learning_goal": payload.get("learning_goal", ""),
            "weak_points": weak_points,
            "learning_preference": payload.get("learning_preference", "案例驱动"),
            "diagnosis": f"当前主要短板集中在{', '.join(weak_points) if weak_points else '基础概念'}。",
            "strategy": "采用短讲义、可运行案例、即时测验和错因反馈的组合。",
        }

    def generate_learning_path(self, profile: dict[str, Any], course_title: str) -> dict[str, Any]:
        goal = profile.get("learning_goal") or f"掌握{course_title}核心内容"
        return {
            "course_title": course_title,
            "goal": goal,
            "stages": [
                {
                    "name": "阶段一：基础补齐",
                    "target": "理解核心概念和工具链",
                    "resources": ["概念讲义", "最小可运行示例"],
                    "practice": "完成 3 道基础题",
                    "mastery": "能独立解释关键术语",
                },
                {
                    "name": "阶段二：案例迁移",
                    "target": "用案例串联知识点",
                    "resources": ["案例拆解", "代码模板"],
                    "practice": "改造一个示例任务",
                    "mastery": "能按步骤完成同类任务",
                },
                {
                    "name": "阶段三：综合应用",
                    "target": "完成一个小型综合任务",
                    "resources": ["任务清单", "自评表"],
                    "practice": "提交任务结果和反思",
                    "mastery": "能说明方案选择和错误修正过程",
                },
            ],
        }

    def generate_resources(self, profile: dict[str, Any], path: dict[str, Any]) -> list[dict[str, Any]]:
        topic = path.get("course_title", "课程")
        return [
            {
                "resource_type": "handout",
                "title": f"{topic}个性化讲义",
                "difficulty": "基础到进阶",
                "content": (
                    f"## 学习目标\n{path.get('goal', '')}\n\n"
                    "## 学习建议\n先运行最小案例，再逐步替换参数和输入数据。\n\n"
                    "## 关键提醒\n把每个错误信息记录为问题、原因、修正三列。"
                ),
            },
            {
                "resource_type": "example",
                "title": f"{topic}案例练习",
                "difficulty": "中等",
                "content": "1. 阅读资料片段。\n2. 标出输入、处理、输出。\n3. 修改一个参数并观察结果。",
            },
            {
                "resource_type": "quiz",
                "title": f"{topic}形成性测验",
                "difficulty": "基础",
                "content": "包含概念题、流程题和一个简短实践题。",
            },
            {
                "resource_type": "task",
                "title": f"{topic}综合任务",
                "difficulty": "进阶",
                "content": "围绕真实学习目标完成一个可展示的小任务，并写出复盘。",
            },
        ]

    def generate_quiz(self, course_title: str) -> dict[str, Any]:
        return {
            "title": f"{course_title}形成性测验",
            "questions": [
                {
                    "id": "q1",
                    "type": "short",
                    "question": "请说明该主题中最核心的一个概念。",
                    "reference_answer": "能够准确说明概念、使用场景和注意事项。",
                    "score": 30,
                },
                {
                    "id": "q2",
                    "type": "short",
                    "question": "遇到报错时，你会按什么步骤定位问题？",
                    "reference_answer": "读取错误信息，定位行号，复现问题，逐步缩小范围。",
                    "score": 30,
                },
                {
                    "id": "q3",
                    "type": "task",
                    "question": "设计一个小练习，把今天的知识点用于一个新场景。",
                    "reference_answer": "练习目标明确，有输入输出，有检查标准。",
                    "score": 40,
                },
            ],
        }

    def answer_tutor(self, question: str, contexts: list[dict[str, Any]]) -> dict[str, Any]:
        citations = [
            {"source_file": item.get("source_file"), "content": item.get("content", "")[:160]}
            for item in contexts
        ]
        basis = contexts[0]["content"] if contexts else "当前课程资料中没有检索到直接片段。"
        return {
            "answer": f"根据课程资料，可先抓住这个要点：{basis[:220]}。针对你的问题：{question}，建议先回到资料中的定义或示例，再做一个最小案例验证。",
            "citations": citations,
            "mode": self.mode_label,
        }

    def profile_dialog(self, payload: dict[str, Any]) -> dict[str, Any]:
        """对话式画像构建：根据用户消息和已抽取信息，返回回复和新抽取的维度。"""
        action = payload.get("action", "continue")
        student_name = payload.get("student_name", "同学")
        extracted = payload.get("extracted", {})
        user_message = payload.get("user_message", "")

        if action == "opening":
            return {
                "reply": f"你好 {student_name}！我来帮你构建学习画像，这样后续可以为你提供更个性化的学习内容。先聊聊，你目前对这门课程的掌握情况怎么样？是完全零基础、有一些了解、还是已经比较熟练了？",
                "extracted": {},
                "ready": False,
            }

        # 基于关键词的智能抽取
        new_extracted: dict[str, Any] = {}
        msg = user_message.lower()

        if not extracted.get("current_level"):
            level_map = {
                "零基础": "零基础", "没有基础": "零基础", "完全不会": "零基础",
                "有一些": "有基础", "了解一点": "有基础", "学过一点": "有基础",
                "比较熟练": "较熟练", "掌握": "较熟练", "熟悉": "较熟练",
            }
            for kw, level in level_map.items():
                if kw in msg:
                    new_extracted["current_level"] = level
                    break
            if not new_extracted.get("current_level") and any(w in msg for w in ["python", "java", "编程", "代码", "学过"]):
                new_extracted["current_level"] = "有基础"

        if not extracted.get("learning_goal"):
            goal_map = {"考试": "通过考试", "期末": "通过考试", "项目": "完成项目", "工作": "职业发展", "兴趣": "兴趣学习"}
            for kw, goal in goal_map.items():
                if kw in msg:
                    new_extracted["learning_goal"] = goal
                    break

        if not extracted.get("weak_points"):
            if any(w in msg for w in ["困难", "不会", "不懂", "薄弱", "难"]):
                new_extracted["weak_points"] = [user_message.strip()]

        if not extracted.get("learning_preference"):
            pref_map = {"视频": "视频学习", "动手": "动手实践", "案例": "案例驱动", "文档": "阅读文档"}
            for kw, pref in pref_map.items():
                if kw in msg:
                    new_extracted["learning_preference"] = pref
                    break

        if not extracted.get("diagnosis"):
            diag_map = {"概念": "概念理解困难", "应用": "实践应用不足", "时间": "时间安排问题", "基础": "基础薄弱"}
            for kw, diag in diag_map.items():
                if kw in msg:
                    new_extracted["diagnosis"] = diag
                    break

        if not extracted.get("strategy"):
            strat_map = {"查资料": "自主查资料", "问同学": "请教他人", "跳过": "回避问题", "多练": "反复练习"}
            for kw, strat in strat_map.items():
                if kw in msg:
                    new_extracted["strategy"] = strat
                    break

        # 生成回复
        combined = {**extracted, **new_extracted}
        all_dims = {"current_level", "learning_goal", "weak_points", "learning_preference", "diagnosis", "strategy"}
        ready = all_dims.issubset(set(combined.keys()))

        confirm = "、".join(f"{k}：{v}" if isinstance(v, str) else f"{k}：{'、'.join(v)}" for k, v in new_extracted.items())
        missing = [d for d in all_dims if d not in combined]

        if confirm and missing:
            reply = f"了解了，{confirm}。接下来想了解一下你的{missing[0]}。"
        elif confirm and not missing:
            reply = f"好的，{confirm}。我已经对你的学习情况有了全面的了解，可以生成画像了。"
        elif not confirm and missing:
            prompts = {
                "current_level": "你目前对这门课程的掌握程度怎么样？",
                "learning_goal": "你学习这门课的目标是什么呢？",
                "weak_points": "你觉得哪些知识点比较困难？",
                "learning_preference": "你更喜欢哪种学习方式？",
                "diagnosis": "你觉得学习中最大的障碍是什么？",
                "strategy": "遇到不会的问题你一般怎么处理？",
            }
            reply = prompts.get(missing[0], f"能聊聊你的{missing[0]}吗？")
        else:
            reply = "好的，我已经对你的学习情况有了全面的了解，可以生成画像了。"

        return {
            "reply": reply,
            "extracted": new_extracted,
            "ready": ready,
        }

    def evaluate(self, quiz: dict[str, Any], answers: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
        questions = quiz.get("questions", [])
        answered = sum(1 for q in questions if str(answers.get(q.get("id"), "")).strip())
        score = round((answered / max(len(questions), 1)) * 100, 1)
        return {
            "score": score,
            "mistake_analysis": "已按答题完整度给出演示评分；真实 AI 模式会结合参考答案做语义评价。",
            "weak_points": profile.get("weak_points", []),
            "next_steps": ["复盘空题或低信心题", "围绕薄弱点再生成 1 组练习", "用课程资料继续追问 TutorAgent"],
        }
