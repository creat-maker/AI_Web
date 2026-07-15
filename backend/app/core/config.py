from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    sqlite_fallback_path: str = Field(
        default="./backend/storage/eduagent.sqlite3", alias="SQLITE_FALLBACK_PATH"
    )
    deepseek_api_key: str | None = Field(default=None, alias="DEEPSEEK_API_KEY")
    dashscope_api_key: str | None = Field(default=None, alias="DASHSCOPE_API_KEY")
    qwen_api_key: str | None = Field(default=None, alias="QWEN_API_KEY")
    llm_provider: Literal["mock", "deepseek", "qwen", "dashscope"] = Field(
        default="mock", alias="LLM_PROVIDER"
    )
    chroma_persist_dir: str = Field(default="./backend/storage/chroma", alias="CHROMA_PERSIST_DIR")
    upload_dir: str = Field(default="./backend/storage/uploads", alias="UPLOAD_DIR")
    report_dir: str = Field(default="./backend/storage/reports", alias="REPORT_DIR")
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")
    jwt_secret: str = Field(default="edumind-jwt-secret-2026", alias="JWT_SECRET")
    xfyun_app_id: str | None = Field(default=None, alias="XFYUN_APP_ID")
    xfyun_api_key: str | None = Field(default=None, alias="XFYUN_API_KEY")
    xfyun_api_secret: str | None = Field(default=None, alias="XFYUN_API_SECRET")
    xfyun_tts_url: str = Field(default="wss://tts-api.xfyun.cn/v2/tts", alias="XFYUN_TTS_URL")
    xfyun_spark_url: str = Field(default="wss://spark-api.xf-yun.com/v3.5/chat", alias="XFYUN_SPARK_URL")
    xfyun_safety_url: str = Field(default="https://spark-api.xf-yun.com/v1/safety", alias="XFYUN_SAFETY_URL")
    xfyun_enabled: bool = Field(default=False, alias="XFYUN_ENABLED")

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        sqlite_path = Path(self.sqlite_fallback_path)
        if not sqlite_path.is_absolute():
            sqlite_path = ROOT_DIR / sqlite_path
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{sqlite_path}"

    @property
    def is_mock_mode(self) -> bool:
        if self.llm_provider == "deepseek":
            return not bool(self.deepseek_api_key)
        if self.llm_provider in {"qwen", "dashscope"}:
            return not bool(self.qwen_api_key or self.dashscope_api_key)
        return True

    @property
    def xfyun_configured(self) -> bool:
        return bool(self.xfyun_enabled and self.xfyun_app_id and self.xfyun_api_key and self.xfyun_api_secret)

    def path_from_root(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else ROOT_DIR / path

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
