"""
Validators utility
"""
import re
from typing import Any, Dict, Optional


def validate_api_key(api_key: str, provider: str) -> tuple[bool, Optional[str]]:
    """Validate an API key format for a given provider."""
    if not api_key or not api_key.strip():
        return False, "API密钥不能为空"

    api_key = api_key.strip()

    patterns = {
        "openai": r"^sk-[A-Za-z0-9\-_]{20,}$",
        "claude": r"^sk-ant-[A-Za-z0-9\-_]{20,}$",
        "deepseek": r"^sk-[A-Za-z0-9\-_]{20,}$",
        "qwen": r"^sk-[A-Za-z0-9\-_]{20,}$",
    }

    if provider in patterns:
        pattern = patterns[provider]
        if not re.match(pattern, api_key):
            return False, f"API密钥格式不正确，请检查"

    return True, None


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """Validate a URL format."""
    if not url or not url.strip():
        return False, "URL不能为空"

    url = url.strip()
    url_pattern = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(url):
        return False, "URL格式不正确"

    return True, None


def validate_instruction(instruction: str) -> tuple[bool, Optional[str]]:
    """Validate a user instruction."""
    if not instruction or not instruction.strip():
        return False, "指令不能为空"

    if len(instruction.strip()) < 5:
        return False, "指令太短，请提供更详细的描述"

    if len(instruction) > 2000:
        return False, "指令太长，请控制在2000字以内"

    return True, None


def sanitize_table_name(name: str) -> str:
    """Sanitize a table name for use in Access."""
    # Remove special characters, keep alphanumeric and underscores
    sanitized = re.sub(r"[^\w\u4e00-\u9fff]", "_", name)
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = "_" + sanitized
    return sanitized[:64]  # Access max name length
