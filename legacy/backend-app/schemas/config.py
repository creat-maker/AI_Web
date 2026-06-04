from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ConfigCreate(BaseModel):
    config_key: str = Field(..., max_length=100)
    config_value: Optional[str] = None
    description: Optional[str] = Field(None, max_length=255)


class ConfigUpdate(BaseModel):
    config_value: Optional[str] = None
    description: Optional[str] = Field(None, max_length=255)


class ConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    config_key: str
    config_value: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ChatHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    role: str
    content: str
    created_at: datetime
