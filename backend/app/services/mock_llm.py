from __future__ import annotations

from typing import Any


def _join(values: list[Any], fallback: str = "基础概念") -> str:
    items = [str(item).strip() for item in values if str(item).strip()]
    return "、".join(items) if items else fallback


def _citation_ids(contexts: list[dict[str, Any]], limit: int = 3) -> list[str]:
    refs: list[str] = []
    for item in contexts[:limit]:
        citation_id = item.get("citation_id")
        source = item.get("source_file") or item.get("document_id")
        if citation_id:
            refs.append(str(citation_id))
        elif source:
            refs.append(str(source))
    return refs


def _confidence_from_evidence(evidence: dict[str, Any], contexts: list[dict[str, Any]]) -> float:
    if evidence.get("confidence") is not None:
        return round(float(evidence.get("confidence") or 0), 2)
    if not contexts:
        return 0.0
    values = [float(item.get("confidence", item.get("score", 0)) or 0) for item in contexts]
    return round(sum(values) / max(len(values), 1), 2)


class MockLLM:
    mode_label = "演示 mock 模式"

    def generate_profile(self, payload: dict[str, Any]) -> dict[str, Any]:
        weak_points = payload.get("weak_points") or []
        current_level = payload.get("current_level", "待评估")
        learning_goal = payload.get("learning_goal", "")
        preference = payload.get("learning_preference", "案例驱动")
        weak_text = _join(weak_points)
        dimensions = [
            {"name": "知识基础", "value": current_level, "evidence": "来自对话中的当前水平描述"},
            {"name": "学习目标", "value": learning_goal or "完成本课程核心能力训练", "evidence": "来自学习目标输入"},
            {"name": "知识短板", "value": weak_text, "evidence": "来自学生自述薄弱点"},
            {"name": "认知风格", "value": "示例优先、从运行结果反推概念", "evidence": f"学习偏好为{preference}"},
            {"name": "易错点偏好", "value": f"容易在{weak_text}相关任务中忽略边界条件和调试步骤", "evidence": "由薄弱点推断"},
            {"name": "资源偏好", "value": preference, "evidence": "来自对话输入"},
            {"name": "练习节奏", "value": "短讲义后立即配套 10-20 分钟练习", "evidence": "面向循环结构学习的默认练习节奏"},
            {"name": "风险等级", "value": "中" if weak_points else "低", "evidence": "由薄弱点数量估计"},
        ]
        return {
            "student_name": payload.get("student_name", "学生"),
            "current_level": current_level,
            "learning_goal": learning_goal,
            "weak_points": weak_points,
            "learning_preference": preference,
            "cognitive_style": "案例驱动 + 可运行代码验证",
            "error_tendency": f"在{weak_text}处可能出现概念会背但迁移困难的问题",
            "available_time": "建议按 3 个学习单元推进，每个单元 30-45 分钟",
            "risk_level": "medium" if weak_points else "low",
            "dimensions": dimensions,
            "diagnosis": f"当前主要短板集中在{weak_text}，适合用 RAG 证据讲义、代码实操和形成性测验闭环推进。",
            "strategy": "采用短讲义、思维导图、可运行案例、即时测验、拓展阅读和项目任务的组合，并随测评结果更新画像。",
            "dynamic_update_rule": "每次答疑、测验和资源反馈后更新薄弱点、掌握度、资源偏好与下一步学习路径。",
        }

    def generate_learning_path(
        self,
        profile: dict[str, Any],
        course_title: str,
        contexts: list[dict[str, Any]] | None = None,
        knowledge_evidence: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        contexts = contexts or []
        knowledge_evidence = knowledge_evidence or {}
        refs = _citation_ids(contexts)
        confidence = _confidence_from_evidence(knowledge_evidence, contexts)
        goal = profile.get("learning_goal") or f"掌握{course_title}核心内容"
        weak_text = _join(profile.get("weak_points", []))
        return {
            "course_title": course_title,
            "goal": goal,
            "evidence_confidence": confidence,
            "personalization_basis": {
                "weak_points": profile.get("weak_points", []),
                "learning_preference": profile.get("learning_preference", "案例驱动"),
                "citation_refs": refs,
            },
            "latest_adjustment_reason": (
                f"根据知识库检索到的 {len(contexts)} 条证据，将学习顺序调整为：先补齐{weak_text}，再进入代码案例和综合项目。"
            ),
            "stages": [
                {
                    "sequence": 1,
                    "name": "阶段一：概念补齐",
                    "target": f"建立{weak_text}的最小概念框架",
                    "resources": ["课程讲解文档", "知识点思维导图"],
                    "practice": "完成 3 道基础判断/简答题，确认术语和使用场景",
                    "mastery": "能用自己的话解释关键概念，并指出适用边界",
                    "evidence_refs": refs[:2],
                },
                {
                    "sequence": 2,
                    "name": "阶段二：代码实操",
                    "target": "通过可运行案例把概念迁移到真实任务",
                    "resources": ["代码类实操案例", "调试清单"],
                    "practice": "运行示例，修改一个输入条件，并记录输出变化",
                    "mastery": "能按输入、处理、输出三步复现同类任务",
                    "evidence_refs": refs,
                },
                {
                    "sequence": 3,
                    "name": "阶段三：题库巩固",
                    "target": "通过形成性测验发现残余薄弱点",
                    "resources": ["不同类型练习题目", "错因反馈卡"],
                    "practice": "完成选择题、简答题和小实践题各 1 组",
                    "mastery": "正确率达到 80%，且能说明错因修正方式",
                    "evidence_refs": refs[:2],
                },
                {
                    "sequence": 4,
                    "name": "阶段四：项目整合",
                    "target": "完成一个可展示的小型综合任务",
                    "resources": ["实践项目学习材料", "拓展阅读材料"],
                    "practice": "提交任务结果、运行截图和复盘记录",
                    "mastery": "能解释方案选择、依赖资料和改进方向",
                    "evidence_refs": refs,
                },
            ],
        }

    def generate_resource_plan(
        self,
        profile: dict[str, Any],
        path: dict[str, Any],
        contexts: list[dict[str, Any]] | None = None,
        knowledge_evidence: dict[str, Any] | None = None,
        course_title: str = "课程",
    ) -> dict[str, Any]:
        contexts = contexts or []
        knowledge_evidence = knowledge_evidence or {}
        refs = _citation_ids(contexts, limit=5)
        weak_points = profile.get("weak_points", []) or ["核心概念"]
        goal = path.get("goal") or profile.get("learning_goal") or f"掌握{course_title}"
        base_items = [
            ("handout", "个性化课程讲解文档", "Markdown 短讲义"),
            ("mindmap", "知识点思维导图", "Mermaid mindmap"),
            ("quiz", "分层练习题目", "选择题、简答题、实践题"),
            ("video_script", "多模态教学视频脚本", "分镜脚本，可对接视频生成工具"),
            ("code_case", "代码类实操案例", "可运行 Python 代码与调试步骤"),
            ("reading", "拓展阅读材料", "延伸阅读和关键词"),
            ("project", "实践项目学习材料", "项目任务书与评价量规"),
        ]
        items = []
        for index, (resource_type, title, output_format) in enumerate(base_items):
            weak_point = weak_points[index % len(weak_points)]
            items.append(
                {
                    "resource_type": resource_type,
                    "title": f"{course_title} · {title}",
                    "target_weak_point": weak_point,
                    "output_format": output_format,
                    "evidence_refs": refs,
                    "recommendation_reason": f"围绕“{weak_point}”补齐，服务于学习目标：{goal}",
                }
            )
        return {
            "agent": "ResourcePlannerAgent",
            "course_title": course_title,
            "goal": goal,
            "evidence_confidence": _confidence_from_evidence(knowledge_evidence, contexts),
            "coverage": ["讲解文档", "思维导图", "练习题", "视频/动画脚本", "代码实操", "拓展阅读", "实践项目"],
            "items": items,
        }

    def generate_resources(
        self,
        profile: dict[str, Any],
        path: dict[str, Any],
        resource_plan: dict[str, Any] | None = None,
        contexts: list[dict[str, Any]] | None = None,
        knowledge_evidence: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        contexts = contexts or []
        knowledge_evidence = knowledge_evidence or {}
        resource_plan = resource_plan or {}
        topic = path.get("course_title") or resource_plan.get("course_title") or "课程"
        refs = _citation_ids(contexts, limit=5)
        weak_text = _join(profile.get("weak_points", []))
        confidence = _confidence_from_evidence(knowledge_evidence, contexts)
        plan_items = resource_plan.get("items") or []
        reason_by_type = {
            str(item.get("resource_type")): item.get("recommendation_reason")
            for item in plan_items
            if item.get("resource_type")
        }

        def item(
            resource_type: str,
            title: str,
            difficulty: str,
            content: str,
            default_reason: str,
        ) -> dict[str, Any]:
            reason = reason_by_type.get(resource_type, default_reason)
            return {
                "resource_type": resource_type,
                "title": title,
                "difficulty": difficulty,
                "content": content,
                "recommendation_reason": reason,
                "recommend_reason": reason,
                "source_refs": refs,
                "confidence": confidence,
                "source_agent": "ResourceAgent",
            }

        return [
            item(
                "handout",
                f"{topic}个性化讲义",
                "基础到进阶",
                (
                    f"## 学习目标\n{path.get('goal', '')}\n\n"
                    f"## 当前短板\n{weak_text}\n\n"
                    "## 学习建议\n先阅读知识库证据对应章节，再运行最小案例，最后用练习题检查掌握度。\n\n"
                    "## 关键提醒\n把每一个错误信息记录为“问题、原因、修正”三列，便于画像随学随新。"
                ),
                f"用短讲义帮助学生先建立{weak_text}的结构化认识。",
            ),
            item(
                "mindmap",
                f"{topic}知识点思维导图",
                "基础",
                (
                    "```mermaid\n"
                    "mindmap\n"
                    f"  root(({topic}))\n"
                    "    概念理解\n"
                    "      定义\n"
                    "      使用场景\n"
                    "      常见误区\n"
                    "    代码实践\n"
                    "      输入\n"
                    "      处理\n"
                    "      输出\n"
                    "    测评反馈\n"
                    "      形成性测验\n"
                    "      错因复盘\n"
                    "```\n"
                ),
                "用图结构降低新手在概念和实践之间切换的认知负担。",
            ),
            item(
                "quiz",
                f"{topic}分层练习题",
                "基础到中等",
                (
                    "1. 概念题：请解释本知识点的适用场景。\n"
                    "2. 判断题：给出一个容易混淆的说法，并说明是否正确。\n"
                    "3. 实践题：修改一个示例输入，观察输出并写出原因。\n"
                    "4. 迁移题：把同一方法用于一个新的学习任务。"
                ),
                "用不同题型检测概念、流程和迁移三类掌握情况。",
            ),
            item(
                "video_script",
                f"{topic}三分钟微课脚本",
                "基础",
                (
                    "镜头 1：展示学生常见困惑，引出本节目标。\n"
                    "镜头 2：用一段代码或流程图解释核心概念。\n"
                    "镜头 3：标注易错点，并给出修正前后对比。\n"
                    "镜头 4：布置一个 5 分钟练习，提示查看知识库引用资料。"
                ),
                "视频/动画脚本便于后续对接多模态生成工具，满足多模态资源展示。",
            ),
            item(
                "code_case",
                f"{topic}可运行代码实操案例",
                "中等",
                (
                    "```python\n"
                    "def summarize_items(items):\n"
                    "    \"\"\"最小案例：统计列表元素出现次数。\"\"\"\n"
                    "    result = {}\n"
                    "    for item in items:\n"
                    "        result[item] = result.get(item, 0) + 1\n"
                    "    return result\n\n"
                    "if __name__ == \"__main__\":\n"
                    "    print(summarize_items([\"http\", \"file\", \"http\", \"dict\"]))\n"
                    "```\n\n"
                    "调试任务：把输入替换成自己的薄弱知识点列表，观察字典统计结果。"
                ),
                "用最小可运行代码把抽象概念落到输入、处理、输出。",
            ),
            item(
                "reading",
                f"{topic}拓展阅读材料",
                "进阶",
                (
                    "阅读顺序：先看课程讲义对应小节，再看代码示例，最后检索官方文档关键词。\n\n"
                    "推荐关键词：while 循环终止条件、变量更新、break / continue、循环嵌套、变量变化表。\n"
                    "阅读产出：写出 3 条“我原来不知道，但现在能解释”的知识点。"
                ),
                "为学有余力的学生提供继续探索的入口。",
            ),
            item(
                "project",
                f"{topic}实践项目任务书",
                "进阶",
                (
                    "项目任务：选择一个学习资料网页或本地文本，完成读取、解析、整理和结果展示。\n\n"
                    "交付物：代码文件、运行截图、错误记录、知识点复盘。\n"
                    "评价量规：正确运行 40%，结构清晰 25%，错因复盘 20%，引用资料说明 15%。"
                ),
                "用可展示项目整合讲义、代码、题库和评价反馈。",
            ),
        ]

    def generate_quiz(self, course_title: str) -> dict[str, Any]:
        return {
            "title": f"{course_title}形成性测验",
            "questions": [
                {
                    "id": "q1",
                    "type": "short",
                    "question": "请说明该主题中最核心的一个概念、适用场景和常见误区。",
                    "reference_answer": "能够准确说明概念、使用场景、边界条件和注意事项。",
                    "score": 30,
                },
                {
                    "id": "q2",
                    "type": "short",
                    "question": "遇到报错时，你会按什么步骤定位问题？",
                    "reference_answer": "读取错误信息，定位行号，复现问题，逐步缩小范围，再验证修复。",
                    "score": 30,
                },
                {
                    "id": "q3",
                    "type": "task",
                    "question": "设计一个小练习，把今天的知识点用于一个新场景。",
                    "reference_answer": "练习目标明确，有输入输出，有检查标准，并能说明迁移依据。",
                    "score": 40,
                },
            ],
        }

    def answer_tutor(self, question: str, contexts: list[dict[str, Any]]) -> dict[str, Any]:
        citations = [
            {
                "source_file": item.get("source_file"),
                "content": item.get("content", "")[:160],
                "confidence": item.get("confidence", item.get("score", 0)),
                "citation_id": item.get("citation_id"),
                "section_title": item.get("section_title"),
                "knowledge_point": item.get("knowledge_point"),
            }
            for item in contexts
        ]
        if not contexts:
            return {
                "answer": (
                    f"当前课程知识库没有检索到与“{question}”直接相关的片段。"
                    "建议先上传课程讲义、实验指导或换一个更具体的关键词；我可以先给出通用学习建议，"
                    "但需要标记为低依据回答。"
                ),
                "citations": [],
                "mode": self.mode_label,
                "unsupported_answer_risk": True,
            }
        basis = contexts[0]["content"]
        return {
            "answer": (
                f"根据课程资料，可以先抓住这个要点：{basis[:220]}。"
                f"针对你的问题“{question}”，建议先回到资料中的定义或示例，再做一个最小案例验证。"
            ),
            "citations": citations,
            "mode": self.mode_label,
            "unsupported_answer_risk": False,
        }

    def evaluate(self, quiz: dict[str, Any], answers: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
        questions = quiz.get("questions", [])
        answered = sum(1 for q in questions if str(answers.get(q.get("id"), "")).strip())
        score = round((answered / max(len(questions), 1)) * 100, 1)
        weak_points = profile.get("weak_points", [])
        needs_adjustment = score < 80
        detected_new = [] if not needs_adjustment else (weak_points[:2] or ["核心概念"])
        return {
            "score": score,
            "mistake_analysis": "已按答题完整度给出演示评分；真实 AI 模式会结合参考答案做语义评价。",
            "weak_points": weak_points,
            "mastery_level": "达标" if score >= 80 else "需要巩固",
            "path_adjustment_needed": needs_adjustment,
            "detected_new_weak_points": detected_new,
            "resolved_weak_points": weak_points[:1] if score >= 80 and weak_points else [],
            "adjustment_reason": "测验表现低于达标线，建议重新规划薄弱点练习。" if needs_adjustment else "测验达标，保留当前学习路径。",
            "next_steps": [
                "复盘空题或低信心题",
                "围绕薄弱点再生成 1 组练习",
                "用课程资料继续追问 TutorAgent",
            ],
            "profile_update": {
                "weak_points": weak_points,
                "recommended_preference": profile.get("learning_preference", "案例驱动"),
                "reason": "根据本次形成性测验结果更新下一轮学习路径。",
            },
        }

    def audit_generation(self, payload: dict[str, Any]) -> dict[str, Any]:
        resources = payload.get("generated_resources", []) or []
        contexts = payload.get("retrieved_context", []) or []
        evidence = payload.get("knowledge_evidence", {}) or {}
        tutor_answer = payload.get("tutor_answer", {}) or {}
        citation_count = int(evidence.get("citation_count") or len(contexts))
        resource_count = len(resources)
        confidence = _confidence_from_evidence(evidence, contexts)
        unsupported_answer_risk = bool(evidence.get("unsupported_answer_risk") or tutor_answer.get("unsupported_answer_risk"))
        missing_ref_count = sum(1 for item in resources if not item.get("source_refs"))
        resource_types = sorted({str(item.get("resource_type", "resource")) for item in resources})
        low_coverage = resource_count < 5 or len(resource_types) < 5
        risk_level = "medium" if unsupported_answer_risk or missing_ref_count or low_coverage or confidence < 0.25 else "low"
        return {
            "agent": "AuditAgent",
            "review_status": "需要人工复核" if risk_level != "low" else "可用于演示",
            "risk_level": risk_level,
            "citation_count": citation_count,
            "resource_count": resource_count,
            "resource_types": resource_types,
            "average_evidence_confidence": confidence,
            "unsupported_answer_risk": unsupported_answer_risk,
            "checks": [
                {
                    "name": "RAG 引用覆盖",
                    "status": "pass" if citation_count else "warning",
                    "detail": f"本轮检索命中 {citation_count} 条课程证据。",
                },
                {
                    "name": "资源类型覆盖",
                    "status": "pass" if not low_coverage else "warning",
                    "detail": f"已生成 {resource_count} 个资源，覆盖 {len(resource_types)} 类。",
                },
                {
                    "name": "防幻觉风险",
                    "status": "pass" if not unsupported_answer_risk else "warning",
                    "detail": "所有答疑均带课程引用。" if not unsupported_answer_risk else "存在低依据回答，需要人工复核。",
                },
                {
                    "name": "内容安全",
                    "status": "pass",
                    "detail": "演示模式未发现敏感违规内容；正式模式建议接入平台安全审核接口。",
                },
            ],
            "suggestions": [
                "提交文档中标注知识库来源、授权和协议。",
                "正式演示时优先选择 citation_count 大于 3 的问题。",
                "多模态视频脚本可后续对接讯飞或其他获准工具生成实际视频。",
            ],
        }
