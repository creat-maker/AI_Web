import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import ChatHistory, SystemConfig
from app.schemas import AIGenerateRequest, AvatarChatRequest, QuizGenerateRequest, QuizItem, ResponseModel
from app.services import call_qwen, get_config_value, mock_baidu_token

router = APIRouter(prefix="/avatar", tags=["Avatar 对话与生成"])


@router.post("/chat", response_model=ResponseModel[dict])
async def avatar_chat(payload: AvatarChatRequest, db: Session = Depends(get_db)):
    history = ChatHistory(session_id=payload.session_id, role="user", content=payload.text)
    db.add(history)
    db.commit()

    system_prompt = (
        "你是一个教学助手，名字叫「小织」，用活泼、亲切的口吻与老师对话。"
        "每次回复不超过 100 字，禁止输出任何格式化符号（如 ```、**、- 等）。"
    )

    recent = db.query(ChatHistory).filter(
        ChatHistory.session_id == payload.session_id
    ).order_by(ChatHistory.created_at.desc()).limit(10).all()

    messages = [{"role": "system", "content": system_prompt}]
    for msg in reversed(recent):
        messages.append({"role": msg.role, "content": msg.content})

    api_key = get_config_value(db, "QWEN_API_KEY")
    reply_text = call_qwen(api_key, messages, temperature=0.9)

    assistant_msg = ChatHistory(session_id=payload.session_id, role="assistant", content=reply_text)
    db.add(assistant_msg)
    db.commit()

    return ResponseModel(data={"reply": reply_text})


@router.post("/generate", response_model=ResponseModel[str])
async def generate_avatar(
    payload: AIGenerateRequest,
    db: Session = Depends(get_db),
):
    api_key = get_config_value(db, "QWEN_API_KEY")

    user_prompt = (
        f"请根据以下需求，生成一段 Avatar 数字人的播报脚本：\n\n"
        f"【需求】{payload.prompt}\n\n"
        "要求：\n"
        "1. 播报时长控制在 30-60 秒内（约 150-300 字）\n"
        "2. 语言口语化、适合 TTS 语音合成\n"
        "3. 分 2-3 个自然段，不要使用 Markdown 格式\n"
        "4. 以『亲爱的同学们，大家好...』开头"
    )

    messages = [
        {"role": "system", "content": "你是一个顶级教学设计专家，擅长写 Avatar 数字人播报脚本。"},
        {"role": "user", "content": user_prompt},
    ]

    script = call_qwen(api_key, messages, temperature=0.7)
    return ResponseModel(data=script)


@router.post("/quiz/generate", response_model=ResponseModel[dict])
async def generate_quiz(
    payload: QuizGenerateRequest,
    db: Session = Depends(get_db),
):
    api_key = get_config_value(db, "QWEN_API_KEY")

    quiz_instruction = (
        f"请为「{payload.topic}」这个教学主题生成 {payload.count} 道选择题。"
        "必须严格返回 JSON 数组格式，每道题包含 id、question（题干）、"
        "options（4 个选项的数组）、answer（正确答案索引，0-3）。"
        "题目要有区分度，难度适中。不要输出任何 Markdown 格式。"
    )

    messages = [
        {"role": "system", "content": "你是一个专业的出题专家，只输出合法的 JSON 数组。"},
        {"role": "user", "content": quiz_instruction},
    ]

    raw = call_qwen(api_key, messages, temperature=0.5)
    cleaned = raw.strip().strip("```json").strip("```").strip()

    try:
        items = json.loads(cleaned)
        quizzes = [QuizItem(**item) for item in items[:payload.count]]
    except (json.JSONDecodeError, Exception):
        quizzes = [
            QuizItem(
                id=i + 1,
                question=f"关于「{payload.topic}」的第 {i + 1} 题",
                options=["选项 A", "选项 B", "选项 C", "选项 D"],
                answer=0,
            )
            for i in range(payload.count)
        ]

    session_id = payload.session_id or str(uuid.uuid4())
    for quiz in quizzes:
        history_entry = ChatHistory(
            session_id=session_id,
            role="assistant",
            content=json.dumps(quiz.model_dump(), ensure_ascii=False),
        )
        db.add(history_entry)
    db.commit()

    return ResponseModel(data={"session_id": session_id, "quizzes": [q.model_dump() for q in quizzes]})


@router.get("/chat-history/{session_id}", response_model=ResponseModel[list[dict]])
def get_chat_history(session_id: str, limit: int = 50, db: Session = Depends(get_db)):
    records = db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id
    ).order_by(ChatHistory.created_at.desc()).limit(limit).all()

    return ResponseModel(data=[
        {"role": r.role, "content": r.content, "created_at": r.created_at.isoformat()}
        for r in reversed(records)
    ])
