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
    upload_dir: str = "./backend/storage/uploads"
    report_dir: str = "./backend/storage/reports"

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

    def path_from_root(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else ROOT_DIR / path


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
