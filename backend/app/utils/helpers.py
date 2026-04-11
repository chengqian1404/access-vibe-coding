import os
import re
import time
from pathlib import Path


def format_duration(seconds: float) -> str:
    """Convert seconds to human-readable HH:MM:SS string."""
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_file_size(num_bytes: int) -> str:
    """Convert bytes to human-readable size string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def safe_filename(name: str) -> str:
    """Sanitize a string to be safe as a filename."""
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = re.sub(r"\s+", "_", name.strip())
    name = re.sub(r"_+", "_", name)
    return name[:200]


def ensure_dir(path: str) -> str:
    """Create directory (and parents) if it doesn't exist. Returns the path."""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def get_timestamp_str() -> str:
    """Return a filesystem-safe timestamp string: YYYYMMDD_HHMMSS."""
    return time.strftime("%Y%m%d_%H%M%S")
