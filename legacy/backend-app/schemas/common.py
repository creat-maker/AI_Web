from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(default=200, description="业务状态码，200 表示成功")
    msg: str = Field(default="success", description="提示信息")
    data: Optional[T] = Field(default=None, description="响应数据体")
