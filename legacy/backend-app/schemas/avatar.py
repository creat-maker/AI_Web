from typing import List

from pydantic import BaseModel, Field


class AvatarChatRequest(BaseModel):
    session_id: str = Field(..., max_length=100)
    text: str = Field(..., min_length=1)


class AIGenerateRequest(BaseModel):
    session_id: str = Field("anonymous", max_length=100)
    prompt: str = Field(..., min_length=1)
    generator_type: str = Field("general", max_length=50)


class QuizItem(BaseModel):
    id: int
    question: str
    options: List[str]
    answer: int


class QuizGenerateRequest(BaseModel):
    session_id: str = Field("anonymous", max_length=100)
    topic: str = Field(..., min_length=1)
    count: int = Field(5, ge=1, le=20)
