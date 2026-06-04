import os
from typing import List, Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "织课 AI (Pacer)"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "织课 AI 后端服务 - 智能教学工坊平台"
    API_V1_STR: str = "/api/v1"

    BACKEND_CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["*"],
        description="CORS 跨域白名单，生产环境应限定具体域名",
    )

    SQLALCHEMY_DATABASE_URI: Optional[str] = Field(
        default=None,
        description="完整数据库连接串。若未设置则从以下分离字段拼接",
    )

    DB_HOST: str = Field(default="localhost", description="数据库主机地址")
    DB_PORT: int = Field(default=3306, description="数据库端口")
    DB_USER: str = Field(default="root", description="数据库用户名")
    DB_PASSWORD: str = Field(default="12345", description="数据库密码")
    DB_NAME: str = Field(default="pacer", description="数据库名称")
    DB_CHARSET: str = Field(default="utf8mb4", description="数据库字符集")

    SQLITE_FALLBACK_PATH: Optional[str] = Field(
        default=None,
        description="MySQL 不可用时回退的 SQLite 路径；留空则在 backend/ 目录下自动生成",
    )

    @computed_field(alias="resolved_database_uri")
    @property
    def RESOLVED_DATABASE_URI(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset={self.DB_CHARSET}"
        )

    def get_sqlite_fallback_uri(self) -> str:
        if self.SQLITE_FALLBACK_PATH:
            path = self.SQLITE_FALLBACK_PATH
        else:
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            path = os.path.join(backend_dir, "pacer.db")
        return f"sqlite:///{path}"

    ENGINE_POOL_PRE_PING: bool = Field(default=True)
    ENGINE_POOL_RECYCLE: int = Field(default=3600, description="连接池回收秒数")

    FRONTEND_DIST_DIR: Optional[str] = Field(
        default=None,
        description="前端构建产物目录，打包部署时由环境变量 PACER_FRONTEND_DIST 覆盖",
    )

    DASHSCOPE_API_KEY: Optional[str] = Field(
        default=None, description="阿里百炼 DashScope API Key"
    )
    QWEN_API_KEY: Optional[str] = Field(
        default=None, description="阿里通义千问 API Key"
    )
    BAIDU_AK: Optional[str] = Field(
        default=None, description="百度数字人 API ID"
    )
    BAIDU_SK: Optional[str] = Field(
        default=None, description="百度数字人 Secret Key"
    )


settings = Settings()
