"""
Logger utility configuration
"""
import os
import sys
from pathlib import Path

from loguru import logger


def setup_logger(log_level: str = "INFO", log_file: bool = True):
    """Configure the application logger."""
    logger.remove()

    # Console handler
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # File handler
    if log_file:
        log_dir = Path(os.path.expanduser("~/.access-vibe-coding/logs"))
        log_dir.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_dir / "access-vibe-coding.log",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
        )

    return logger
