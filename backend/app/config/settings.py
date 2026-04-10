"""
Application Settings using Pydantic Settings
"""
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    APP_NAME: str = "Access Vibe Coding"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8765
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "app://"]

    # LLM Configuration
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-4-turbo"
    LLM_REQUEST_TIMEOUT: int = 30
    LLM_MAX_RETRIES: int = 3

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4-turbo"

    # Qwen (Alibaba DashScope)
    QWEN_API_KEY: Optional[str] = None
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"
    QWEN_MODEL: str = "qwen-max"

    # Claude (Anthropic)
    CLAUDE_API_KEY: Optional[str] = None
    CLAUDE_BASE_URL: str = "https://api.anthropic.com"
    CLAUDE_MODEL: str = "claude-3-sonnet-20240229"

    # DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Ollama (local)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen:7b"

    # Automation
    AUTOMATION_DELAY: float = 0.1
    SCREENSHOT_QUALITY: int = 85
    MAX_EXECUTION_TIME: int = 300

    # Storage
    CONFIG_DIR: str = "~/.access-vibe-coding"
    LOG_DIR: str = "~/.access-vibe-coding/logs"
    HISTORY_DIR: str = "~/.access-vibe-coding/history"

    # Encryption key for API keys (base64 encoded 32-byte key)
    ENCRYPTION_KEY: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    return Settings()
