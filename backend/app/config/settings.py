import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8765
    DEBUG: bool = True

    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/storage/app.db"
    STORAGE_PATH: str = str(BASE_DIR / "storage")
    RECORDINGS_PATH: str = str(BASE_DIR / "storage" / "recordings")
    ANALYSES_PATH: str = str(BASE_DIR / "storage" / "analyses")
    CACHE_PATH: str = str(BASE_DIR / "storage" / "cache")

    LLM_PROVIDER: str = "qwen"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    CLAUDE_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"

    WHISPER_API_KEY: str = Field(default="", alias="WHISPER_API_KEY")

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"
        populate_by_name = True


settings = Settings()
