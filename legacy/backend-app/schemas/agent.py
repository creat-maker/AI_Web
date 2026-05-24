from typing import Optional

from pydantic import BaseModel, Field


class LessonGenerateRequest(BaseModel):
    topic: str = Field(
        default="人工智能应用基础",
        min_length=1,
        max_length=200,
        description="教案主题/课题名称",
    )
    difficulty: Optional[str] = Field(
        default="适中",
        description="难度调整：降低难度 / 适中 / 提升难度",
    )
    grade: Optional[str] = Field(
        default=None,
        max_length=50,
        description="授课年级，如 高中二年级",
    )
    subject: Optional[str] = Field(
        default=None,
        max_length=50,
        description="学科，如 物理 / 信息技术",
    )
    additional_requirements: Optional[str] = Field(
        default=None,
        description="额外生成要求，如 添加互动环节、融入思政元素",
    )


class LessonGenerateResponse(BaseModel):
    title: str = Field(description="教案标题")
    markdown_content: str = Field(description="教案正文（Markdown 格式）")
    content_format: str = Field(default="markdown", description="内容格式，固定为 markdown")
