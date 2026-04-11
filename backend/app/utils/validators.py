import os
import re
from pathlib import Path


def validate_weixin_id(weixin_id: str) -> bool:
    """Validate a WeChat ID: 6-20 alphanumeric/underscore characters."""
    if not weixin_id or not isinstance(weixin_id, str):
        return False
    pattern = r"^[a-zA-Z0-9_\u4e00-\u9fa5]{2,64}$"
    return bool(re.match(pattern, weixin_id.strip()))


def validate_api_key(key: str) -> bool:
    """Validate that an API key is a non-empty string of reasonable length."""
    if not key or not isinstance(key, str):
        return False
    key = key.strip()
    return 8 <= len(key) <= 256


def validate_file_path(path: str) -> bool:
    """Validate that a file path exists and is a regular file."""
    if not path or not isinstance(path, str):
        return False
    p = Path(path)
    return p.exists() and p.is_file()
