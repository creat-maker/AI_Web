"""对话式画像构建服务：通过自由多轮对话智能抽取学生 6 维画像。

与旧版固定 6 问模式不同，新版采用自然对话流程：
- AI 根据用户回复动态决定追问、确认或跳转维度
- 每轮从对话中增量抽取维度值
- 用户可以随时补充或修正已抽取的信息
- AI 判断信息足够时主动提议完成画像
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from app.services.llm_service import llm_service

# 内存中的对话会话存储（演示级，重启丢失）
_sessions: dict[str, dict[str, Any]] = {}

# 赛题要求的 6 个画像维度及其标签（用于展示和 LLM 提示）
PROFILE_DIMENSIONS = [
    {"key": "knowledge_base", "label": "知识基础", "description": "学生对课程先修知识和当前章节基础概念的掌握情况"},
    {"key": "cognitive_style", "label": "认知风格", "description": "学生更适合图示、案例、推理、练习等哪类学习方式"},
    {"key": "learning_preference", "label": "学习偏好", "description": "学生偏好的资源形式、练习方式和学习节奏"},
    {"key": "error_prone_points", "label": "易错点", "description": "学生在条件判断、循环边界、变量更新等方面的高频错误"},
    {"key": "learning_progress", "label": "学习进度", "description": "学生当前课程章节完成度、测验结果和学习路径状态"},
    {"key": "emotional_motivation", "label": "情感动机", "description": "学生学习信心、兴趣、焦虑程度和目标驱动力"},
]

DIMENSION_MAP = {d["key"]: d["label"] for d in PROFILE_DIMENSIONS}
LEGACY_FIELD_MAP = {
    "current_level": "knowledge_base",
    "weak_points": "error_prone_points",
    "diagnosis": "learning_progress",
    "strategy": "emotional_motivation",
}

SYSTEM_PROMPT = """你是 EduMind 的学习画像构建助手。你的任务是通过自然对话了解学生的学习情况，从中抽取 6 个维度的画像信息。

画像维度：
- knowledge_base（知识基础）：学生已有知识基础、当前水平和前置知识掌握情况
- cognitive_style（认知风格）：学生理解知识时偏概念、步骤、图解、案例还是动手探索
- learning_preference（学习偏好）：学生喜欢的学习方式
- error_prone_points（易错点）：学生容易出错或觉得困难的知识点
- learning_progress（学习进度）：学生当前学习阶段、完成度和近期表现
- emotional_motivation（情感动机）：学习目标、动机、信心、焦虑或坚持方式

对话规则：
1. 用自然、友好的语气与学生交流，不要机械地逐个提问
2. 根据学生的回复灵活追问，可以一次对话中了解多个维度
3. 如果学生已经提到某个维度的信息，主动确认并记录
4. 当所有维度信息都已收集到，或学生表示没有更多要补充时，提议完成画像
5. 每次回复都要简洁，不要一次说太多

你的回复必须是 JSON 格式：
{
  "reply": "你的回复文本",
  "extracted": {
    "维度key": "抽取到的值（可以是字符串或字符串数组）"
  },
  "ready": false
}

其中：
- reply: 你对学生说的话
- extracted: 本轮对话中新抽取到的维度信息（只包含本轮新增或更新的）
- ready: 是否所有维度信息已足够，可以完成画像"""


def start_dialog(student_name: str, course_id: int) -> dict[str, Any]:
    """开启一个对话式画像会话，返回会话 ID 和开场白。"""
    session_id = uuid.uuid4().hex[:12]
    _sessions[session_id] = {
        "student_name": student_name,
        "course_id": course_id,
        "extracted": {},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
        ],
        "completed": False,
    }

    # 生成开场白
    opening = _generate_opening(student_name)
    _sessions[session_id]["messages"].append({"role": "assistant", "content": opening})

    return {
        "session_id": session_id,
        "reply": opening,
        "extracted": {},
        "ready": False,
        "completed": False,
    }


def continue_dialog(session_id: str, user_message: str) -> dict[str, Any]:
    """处理用户回复，增量抽取维度信息，返回 AI 回复。"""
    session = _sessions.get(session_id)
    if not session:
        return {"error": "会话不存在或已过期", "session_id": session_id}

    if session["completed"]:
        return {"error": "该会话已完成", "session_id": session_id}

    # 记录用户消息
    session["messages"].append({"role": "user", "content": user_message})

    # 调用 LLM/Mock 生成回复并抽取维度
    result = _dialog_turn(session, user_message)

    # 更新抽取的维度信息
    new_extracted = result.get("extracted", {})
    new_extracted = _normalize_extracted(new_extracted)
    session["extracted"].update(new_extracted)

    # 记录 AI 回复
    reply = result.get("reply", "好的，我了解了。")
    session["messages"].append({"role": "assistant", "content": reply})

    # 检查是否可以完成画像
    ready = result.get("ready", False)
    completed = False

    if ready:
        completed = True
        session["completed"] = True

    return {
        "session_id": session_id,
        "reply": reply,
        "extracted": session["extracted"],
        "new_extracted": new_extracted,
        "ready": ready,
        "completed": completed,
        "profile": _build_profile(session) if completed else None,
    }


def finish_dialog(session_id: str) -> dict[str, Any]:
    """强制完成画像构建（用户主动确认完成）。"""
    session = _sessions.get(session_id)
    if not session:
        return {"error": "会话不存在或已过期", "session_id": session_id}

    session["completed"] = True
    profile = _build_profile(session)
    return {
        "session_id": session_id,
        "completed": True,
        "profile": profile,
    }


def get_session(session_id: str) -> dict[str, Any] | None:
    """获取会话状态。"""
    return _sessions.get(session_id)


def _generate_opening(student_name: str) -> str:
    """生成开场白。"""
    if llm_service.runtime_mode != "mock":
        try:
            result = llm_service.generate_json("profile_dialog", {
                "action": "opening",
                "student_name": student_name,
                "messages": [],
                "extracted": {},
            })
            return result.get("reply", f"你好 {student_name}！我来帮你构建学习画像。先聊聊，你目前对这门课的掌握情况怎么样？")
        except Exception:
            pass

    # Mock 开场白
    return f"你好 {student_name}！我来帮你构建学习画像，这样后续可以为你提供更个性化的学习内容。先聊聊，你目前对这门课程的掌握情况怎么样？是完全零基础、有一些了解、还是已经比较熟练了？"


def _dialog_turn(session: dict, user_message: str) -> dict[str, Any]:
    """一轮对话：根据用户输入生成回复并抽取维度。"""
    if llm_service.runtime_mode != "mock":
        try:
            result = llm_service.generate_json("profile_dialog", {
                "action": "continue",
                "student_name": session["student_name"],
                "messages": session["messages"][-10:],  # 最近 10 条消息作为上下文
                "extracted": session["extracted"],
                "user_message": user_message,
            })
            return {
                "reply": result.get("reply", "好的，我了解了。"),
                "extracted": result.get("extracted", {}),
                "ready": result.get("ready", False),
            }
        except Exception:
            pass

    # Mock 模式：基于规则的智能抽取
    return _mock_dialog_turn(session, user_message)


def _mock_dialog_turn(session: dict, user_message: str) -> dict[str, Any]:
    """Mock 模式的对话逻辑：基于关键词匹配抽取维度，生成自然回复。"""
    extracted: dict[str, Any] = {}
    existing = session["extracted"]
    msg = user_message.lower()

    # 关键词匹配抽取各维度
    if not existing.get("knowledge_base"):
        level_keywords = {
            "零基础": "零基础", "没有基础": "零基础", "完全不会": "零基础",
            "有一些": "有基础", "了解一点": "有基础", "学过一点": "有基础", "入门": "有基础",
            "比较熟练": "较熟练", "掌握": "较熟练", "熟悉": "较熟练", "还行": "有基础",
        }
        for kw, level in level_keywords.items():
            if kw in msg:
                extracted["knowledge_base"] = level
                break
        # 如果用户提到了具体技术但没明确说水平，推断为有基础
        if not extracted.get("knowledge_base") and any(w in msg for w in ["python", "java", "编程", "代码", "学过", "做过"]):
            extracted["knowledge_base"] = "有基础"

    if not existing.get("emotional_motivation"):
        goal_keywords = {
            "考试": "目标是通过考试，存在阶段性冲刺压力", "期末": "目标是期末冲刺",
            "项目": "希望通过项目实战获得成就感", "做项目": "希望完成项目任务",
            "工作": "学习动机偏职业发展", "就业": "学习动机偏职业发展", "面试": "学习动机偏职业发展",
            "兴趣": "由兴趣驱动学习", "好奇": "由兴趣和好奇心驱动学习",
        }
        for kw, goal in goal_keywords.items():
            if kw in msg:
                extracted["emotional_motivation"] = goal
                break

    if not existing.get("error_prone_points"):
        weak_indicators = ["困难", "不会", "不懂", "薄弱", "难", "搞不懂", "不理解", "搞不清", "头疼", "吃力", "不太熟"]
        if any(w in msg for w in weak_indicators):
            # 尝试提取具体薄弱点
            points = _extract_weak_points(user_message)
            if points:
                extracted["error_prone_points"] = points

    if not existing.get("learning_preference"):
        pref_keywords = {
            "视频": "视频学习", "看视频": "视频学习",
            "动手": "动手实践", "写代码": "动手实践", "实践": "动手实践", "实操": "动手实践",
            "案例": "案例驱动", "例子": "案例驱动", "示例": "案例驱动",
            "文档": "阅读文档", "看书": "阅读文档", "读文档": "阅读文档",
            "理论": "理论优先", "原理": "理论优先",
        }
        for kw, pref in pref_keywords.items():
            if kw in msg:
                extracted["learning_preference"] = pref
                break

    if not existing.get("cognitive_style"):
        style_keywords = {
            "概念": "概念理解型，需要先解释概念边界",
            "图": "图解直观型，适合流程图和变量变化表",
            "步骤": "步骤拆解型，适合逐步推演",
            "例子": "案例迁移型，适合从例题到变式",
            "动手": "实践探索型，适合边写边调试",
            "代码": "代码实操型，适合可运行案例",
        }
        for kw, style in style_keywords.items():
            if kw in msg:
                extracted["cognitive_style"] = style
                break

    if not existing.get("learning_progress"):
        diag_keywords = {
            "刚开始": "刚进入当前章节，需要建立基础框架",
            "学到": "正在推进当前章节学习",
            "作业": "正在围绕课程作业推进",
            "测验": "已进入测验反馈和错因复盘阶段",
            "应用": "需要从理解推进到应用",
            "不会用": "概念到应用迁移不足",
            "时间": "学习节奏受时间安排影响",
            "来不及": "学习进度偏紧，需要短任务推进",
            "拖延": "进度受拖延影响，需要明确阶段目标",
        }
        for kw, diag in diag_keywords.items():
            if kw in msg:
                extracted["learning_progress"] = diag
                break

    if not existing.get("emotional_motivation"):
        strat_keywords = {
            "查资料": "遇到问题会自主查资料，具备主动解决动机",
            "搜索": "遇到问题会主动搜索资料",
            "问同学": "愿意通过同伴求助继续学习",
            "问老师": "愿意向教师求助继续学习",
            "请教": "遇到困难会寻求帮助",
            "跳过": "遇到难题容易回避，需要低门槛任务增强信心",
            "放弃": "遇到困难时信心不足，需要阶段性正反馈",
            "反复练": "愿意通过反复练习巩固",
            "多练": "愿意通过练习提升",
            "刷题": "偏好通过题目训练建立信心",
        }
        for kw, strat in strat_keywords.items():
            if kw in msg:
                extracted["emotional_motivation"] = strat
                break

    # 生成回复
    reply = _generate_mock_reply(session, user_message, extracted)

    # 判断是否所有维度都已抽取
    all_keys = {d["key"] for d in PROFILE_DIMENSIONS}
    filled_keys = set(existing.keys()) | set(extracted.keys())
    ready = all_keys.issubset(filled_keys)

    return {
        "reply": reply,
        "extracted": extracted,
        "ready": ready,
    }


def _extract_weak_points(message: str) -> list[str]:
    """从用户消息中提取薄弱知识点。"""
    import re

    # 尝试提取"XX比较难/困难/不会"模式中的 XX
    patterns = [
        r"(?:但|但是|不过)?([^\s，。、；但]{2,10})(?:比较难|比较困难|不太熟|不太会|不会|不懂|搞不懂)",
        r"(?:比较难|比较困难|不太熟|不太会|不会|不懂|搞不懂)([^\s，。、；]{2,10})",
    ]
    for pat in patterns:
        found = re.findall(pat, message)
        if found:
            # 清理前缀词
            cleaned = [re.sub(r"^(但|但是|不过|就是|是)", "", f).strip() for f in found]
            return [c for c in cleaned if c]

    # 尝试按分隔符拆分
    for sep in ["、", "，", ",", "；", ";"]:
        if sep in message:
            parts = [p.strip() for p in message.split(sep) if p.strip()]
            if len(parts) > 1:
                return parts

    # 提取引号中的内容
    quoted = re.findall(r"[「\"']([^「\"']+)[」\"']", message)
    if quoted:
        return quoted

    # 返回整条消息作为薄弱点描述
    return [message.strip()]


def _generate_mock_reply(session: dict, user_message: str, new_extracted: dict) -> str:
    """Mock 模式生成自然回复。"""
    existing = session["extracted"]
    combined = {**existing, **new_extracted}
    total = len(PROFILE_DIMENSIONS)
    filled = len(combined)

    # 构建确认部分
    confirm_parts = []
    dim_labels = {d["key"]: d["label"] for d in PROFILE_DIMENSIONS}

    for key, value in new_extracted.items():
        label = dim_labels.get(key, key)
        if isinstance(value, list):
            confirm_parts.append(f"{label}：{'、'.join(value)}")
        else:
            confirm_parts.append(f"{label}：{value}")

    # 确定下一个需要了解的维度
    missing_dims = [d for d in PROFILE_DIMENSIONS if d["key"] not in combined]

    if confirm_parts and missing_dims:
        confirm = "、".join(confirm_parts)
        next_dim = missing_dims[0]
        prompts = {
            "knowledge_base": "你目前对这门课程的掌握程度怎么样？",
            "cognitive_style": "你理解新知识时更依赖概念解释、步骤推演、图解还是代码案例？",
            "learning_preference": "你更喜欢哪种学习方式？比如看视频、动手写代码、还是跟着案例做？",
            "error_prone_points": "你觉得哪些知识点比较困难或容易出错？",
            "learning_progress": "你现在学到哪一步了？最近测验、作业或练习进展如何？",
            "emotional_motivation": "你学习这门课的目标、信心或主要压力是什么？",
        }
        return f"了解了，{confirm}。接下来想了解一下——{prompts.get(next_dim['key'], next_dim['label'])}"

    if confirm_parts and not missing_dims:
        confirm = "、".join(confirm_parts)
        return f"好的，{confirm}。我已经对你的学习情况有了全面的了解，可以为你生成学习画像了。点击「完成画像」即可保存。"

    if not confirm_parts and missing_dims:
        next_dim = missing_dims[0]
        prompts = {
            "knowledge_base": "你目前对这门课程的掌握程度怎么样？是完全零基础还是有一些了解？",
            "cognitive_style": "你理解新知识时更依赖概念解释、步骤推演、图解还是代码案例？",
            "learning_preference": "你更喜欢哪种学习方式？",
            "error_prone_points": "你在学习中觉得哪些知识点比较困难？可以具体说说。",
            "learning_progress": "你现在学到哪一步了？最近测验、作业或练习进展如何？",
            "emotional_motivation": "你学习这门课的目标、信心或主要压力是什么？",
        }
        return prompts.get(next_dim["key"], f"能聊聊你的{next_dim['label']}吗？")

    return "好的，我已经对你的学习情况有了全面的了解，可以生成画像了。"


def _build_profile(session: dict) -> dict[str, Any]:
    """根据抽取的维度信息构建完整画像。"""
    extracted = session["extracted"]

    # 如果维度信息不完整，用 LLM/Mock 补全
    if llm_service.runtime_mode != "mock":
        try:
            return llm_service.generate_json("profile", {
                "student_name": session["student_name"],
                **extracted,
            })
        except Exception:
            pass

    # Mock 模式：直接组装，缺失维度用默认值
    extracted = _normalize_extracted(extracted)
    weak_points = extracted.get("error_prone_points", [])
    if isinstance(weak_points, str):
        weak_points = [weak_points]

    return {
        "student_name": session["student_name"],
        "knowledge_base": extracted.get("knowledge_base", "待评估"),
        "cognitive_style": extracted.get("cognitive_style", "步骤拆解型"),
        "learning_preference": extracted.get("learning_preference", "案例驱动"),
        "error_prone_points": weak_points,
        "learning_progress": extracted.get("learning_progress", f"当前主要短板集中在{', '.join(weak_points) if weak_points else '基础概念'}。"),
        "emotional_motivation": extracted.get("emotional_motivation", "希望通过阶段任务获得稳定进步。"),
        "current_level": extracted.get("knowledge_base", "待评估"),
        "learning_goal": extracted.get("emotional_motivation", "掌握课程核心内容"),
        "weak_points": weak_points,
        "diagnosis": extracted.get("learning_progress", f"当前主要短板集中在{', '.join(weak_points) if weak_points else '基础概念'}。"),
        "strategy": "采用短讲义、可运行案例、即时测验和错因反馈的组合。",
        "dimensions": [
            {"key": dim["key"], "label": dim["label"], "description": dim["description"], "value": extracted.get(dim["key"], "")}
            for dim in PROFILE_DIMENSIONS
        ],
        "profile_dimensions": PROFILE_DIMENSIONS,
        "dimension_scores": {
            dim["key"]: 80 if extracted.get(dim["key"]) else 50
            for dim in PROFILE_DIMENSIONS
        },
        "source": "dialog",
    }


def _normalize_extracted(extracted: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for dim in PROFILE_DIMENSIONS:
        key = dim["key"]
        if key in extracted and extracted[key]:
            normalized[key] = extracted[key]
    for legacy_key, new_key in LEGACY_FIELD_MAP.items():
        if new_key not in normalized and extracted.get(legacy_key):
            normalized[new_key] = extracted[legacy_key]
    if "learning_preference" not in normalized and extracted.get("learning_style"):
        normalized["learning_preference"] = extracted["learning_style"]
    return normalized
