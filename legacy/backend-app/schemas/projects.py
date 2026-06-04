import json
from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    filename: str
    original_name: str
    file_path: str
    file_size: int
    content_type: Optional[str] = None
    created_at: datetime


class StagedAttachmentOut(BaseModel):
    temp_id: str
    original_name: str
    file_size: int
    content_type: Optional[str] = None


class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    grade: Optional[str] = Field(None, max_length=50)
    subject: Optional[str] = Field(None, max_length=50)
    attachment_ids: List[str] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    grade: Optional[str] = Field(None, max_length=50)
    subject: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=20)


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    grade: Optional[str] = None
    subject: Optional[str] = None
    status: Optional[str] = None
    contents: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator("contents", mode="before")
    @classmethod
    def _parse_contents(cls, value: Any) -> dict[str, Any]:
        if value in (None, "", b""):
            return {}
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return {}
            return parsed if isinstance(parsed, dict) else {}
        return {}


class ProjectDetail(ProjectOut):
    attachments: List[AttachmentOut] = []


class GeneratedContentEntry(BaseModel):
    format: str
    data: Any
    raw_content: str
    attachment_ids: List[int] = Field(default_factory=list)
    source_files: List[str] = Field(default_factory=list)
    user_requirement: Optional[str] = None
    updated_at: str


class GeneratedContentOut(BaseModel):
    project_id: int
    generator_type: str
    content: GeneratedContentEntry
    animation_html: Optional[str] = None
