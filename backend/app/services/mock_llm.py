from __future__ import annotations

import json
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
            {
                "resource_type": "mindmap",
                "title": f"{topic}知识结构思维导图",
                "difficulty": "基础",
                "content": self._build_mindmap_content(topic, profile),
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

    def _build_mindmap_content(self, topic: str, profile: dict[str, Any]) -> str:
        """构建思维导图结构化 JSON 内容。"""
        weak_points = profile.get("weak_points", ["核心概念"])[:3]
        concept_children = [{"label": w} for w in weak_points] + [
            {"label": "关键流程"},
            {"label": "常见模式"},
        ]
        tree = {
            "root": {
                "label": topic,
                "children": [
                    {"label": "核心概念", "children": concept_children},
                    {
                        "label": "知识关联",
                        "children": [
                            {"label": "概念层：术语定义与使用场景"},
                            {"label": "应用层：案例与练习的映射"},
                            {"label": "诊断层：错误类型与修正策略"},
                        ],
                    },
                    {
                        "label": "学习路径",
                        "children": [
                            {"label": "1. 掌握核心概念节点"},
                            {"label": "2. 通过案例连接概念与应用"},
                            {"label": "3. 用练习巩固，用诊断查漏"},
                        ],
                    },
                ],
            }
        }
        return json.dumps(tree, ensure_ascii=False)
