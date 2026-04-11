from app.config.settings import settings

LLM_PROVIDERS: dict = {
    "openai": {
        "name": "OpenAI",
        "model": "gpt-4o",
        "base_url": settings.OPENAI_BASE_URL,
        "api_key_env": "OPENAI_API_KEY",
        "api_key": settings.OPENAI_API_KEY,
    },
    "qwen": {
        "name": "通义千问",
        "model": "qwen-max",
        "base_url": settings.QWEN_BASE_URL,
        "api_key_env": "QWEN_API_KEY",
        "api_key": settings.QWEN_API_KEY,
    },
    "claude": {
        "name": "Claude",
        "model": "claude-3-5-sonnet-20241022",
        "base_url": "https://api.anthropic.com",
        "api_key_env": "CLAUDE_API_KEY",
        "api_key": settings.CLAUDE_API_KEY,
    },
    "deepseek": {
        "name": "DeepSeek",
        "model": "deepseek-chat",
        "base_url": settings.DEEPSEEK_BASE_URL,
        "api_key_env": "DEEPSEEK_API_KEY",
        "api_key": settings.DEEPSEEK_API_KEY,
    },
}


def get_provider_config(provider: str) -> dict:
    return LLM_PROVIDERS.get(provider, LLM_PROVIDERS["qwen"])


def get_active_provider_config() -> dict:
    return LLM_PROVIDERS.get(settings.LLM_PROVIDER, LLM_PROVIDERS["qwen"])
