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

# 6 个画像维度及其标签（用于展示和 LLM 提示）
PROFILE_DIMENSIONS = [
    {"key": "current_level", "label": "当前水平"},
    {"key": "learning_goal", "label": "学习目标"},
    {"key": "weak_points", "label": "薄弱知识点"},
    {"key": "learning_preference", "label": "学习偏好"},
    {"key": "diagnosis", "label": "学习诊断"},
    {"key": "strategy", "label": "学习策略"},
]

DIMENSION_MAP = {d["key"]: d["label"] for d in PROFILE_DIMENSIONS}

SYSTEM_PROMPT = """你是 EduMind 的学习画像构建助手。你的任务是通过自然对话了解学生的学习情况，从中抽取 6 个维度的画像信息。

画像维度：
- current_level（当前水平）：学生对课程的掌握程度
- learning_goal（学习目标）：学生学这门课的目的
- weak_points（薄弱知识点）：学生觉得困难的知识点
- learning_preference（学习偏好）：学生喜欢的学习方式
- diagnosis（学习诊断）：学生学习中的主要障碍
- strategy（学习策略）：学生遇到问题的处理方式

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
    if not existing.get("current_level"):
        level_keywords = {
            "零基础": "零基础", "没有基础": "零基础", "完全不会": "零基础",
            "有一些": "有基础", "了解一点": "有基础", "学过一点": "有基础", "入门": "有基础",
            "比较熟练": "较熟练", "掌握": "较熟练", "熟悉": "较熟练", "还行": "有基础",
        }
        for kw, level in level_keywords.items():
            if kw in msg:
                extracted["current_level"] = level
                break
        # 如果用户提到了具体技术但没明确说水平，推断为有基础
        if not extracted.get("current_level") and any(w in msg for w in ["python", "java", "编程", "代码", "学过", "做过"]):
            extracted["current_level"] = "有基础"

    if not existing.get("learning_goal"):
        goal_keywords = {
            "考试": "通过考试", "期末": "通过考试", "过考": "通过考试",
            "项目": "完成项目", "做项目": "完成项目", "实战": "完成项目",
            "工作": "职业发展", "就业": "职业发展", "面试": "职业发展",
            "兴趣": "兴趣学习", "好奇": "兴趣学习",
        }
        for kw, goal in goal_keywords.items():
            if kw in msg:
                extracted["learning_goal"] = goal
                break

    if not existing.get("weak_points"):
        weak_indicators = ["困难", "不会", "不懂", "薄弱", "难", "搞不懂", "不理解", "搞不清", "头疼", "吃力", "不太熟"]
        if any(w in msg for w in weak_indicators):
            # 尝试提取具体薄弱点
            points = _extract_weak_points(user_message)
            if points:
                extracted["weak_points"] = points

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

    if not existing.get("diagnosis"):
        diag_keywords = {
            "概念": "概念理解困难", "理解": "概念理解困难",
            "应用": "实践应用不足", "不会用": "实践应用不足",
            "时间": "时间安排问题", "来不及": "时间安排问题", "拖延": "时间安排问题",
            "基础": "基础薄弱", "底子": "基础薄弱",
        }
        for kw, diag in diag_keywords.items():
            if kw in msg:
                extracted["diagnosis"] = diag
                break

    if not existing.get("strategy"):
        strat_keywords = {
            "查资料": "自主查资料", "搜索": "自主查资料", "百度": "自主查资料", "google": "自主查资料",
            "问同学": "请教他人", "问老师": "请教他人", "请教": "请教他人",
            "跳过": "回避问题", "放弃": "回避问题",
            "反复练": "反复练习", "多练": "反复练习", "刷题": "反复练习",
        }
        for kw, strat in strat_keywords.items():
            if kw in msg:
                extracted["strategy"] = strat
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
            "current_level": "你目前对这门课程的掌握程度怎么样？",
            "learning_goal": "你学习这门课的目标是什么呢？",
            "weak_points": "你觉得哪些知识点比较困难？",
            "learning_preference": "你更喜欢哪种学习方式？比如看视频、动手写代码、还是跟着案例做？",
            "diagnosis": "你觉得学习中最主要的障碍是什么？",
            "strategy": "遇到不会的问题你一般怎么处理？",
        }
        return f"了解了，{confirm}。接下来想了解一下——{prompts.get(next_dim['key'], next_dim['label'])}"

    if confirm_parts and not missing_dims:
        confirm = "、".join(confirm_parts)
        return f"好的，{confirm}。我已经对你的学习情况有了全面的了解，可以为你生成学习画像了。点击「完成画像」即可保存。"

    if not confirm_parts and missing_dims:
        next_dim = missing_dims[0]
        prompts = {
            "current_level": "你目前对这门课程的掌握程度怎么样？是完全零基础还是有一些了解？",
            "learning_goal": "你学习这门课的目标是什么？是为了考试、做项目还是其他？",
            "weak_points": "你在学习中觉得哪些知识点比较困难？可以具体说说。",
            "learning_preference": "你更喜欢哪种学习方式？",
            "diagnosis": "你觉得目前学习中最大的障碍是什么？",
            "strategy": "遇到不会的问题你会怎么处理？",
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
    weak_points = extracted.get("weak_points", [])
    if isinstance(weak_points, str):
        weak_points = [weak_points]

    return {
        "student_name": session["student_name"],
        "current_level": extracted.get("current_level", "待评估"),
        "learning_goal": extracted.get("learning_goal", "掌握课程核心内容"),
        "weak_points": weak_points,
        "learning_preference": extracted.get("learning_preference", "案例驱动"),
        "diagnosis": extracted.get("diagnosis", f"当前主要短板集中在{', '.join(weak_points) if weak_points else '基础概念'}。"),
        "strategy": extracted.get("strategy", "采用短讲义、可运行案例、即时测验和错因反馈的组合。"),
        "source": "dialog",
    }
