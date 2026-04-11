import logging
import logging.handlers
import os
import sys
from pathlib import Path

from app.config.settings import settings


_ws_manager = None


def set_ws_manager(manager) -> None:
    global _ws_manager
    _ws_manager = manager


class WebSocketLogHandler(logging.Handler):
    """Broadcasts log records to connected WebSocket clients."""

    def emit(self, record: logging.LogRecord) -> None:
        if _ws_manager is None:
            return
        try:
            import asyncio
            msg = self.format(record)
            data = {
                "level": record.levelname,
                "message": msg,
                "module": record.module,
            }
            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                pass
            if loop and loop.is_running():
                asyncio.ensure_future(_ws_manager.broadcast({"type": "log_message", "data": data}))
        except Exception:
            pass


def setup_logger(name: str = "access_vibe") -> logging.Logger:
    log_dir = Path(settings.STORAGE_PATH)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_handler.setFormatter(fmt)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    ws_handler = WebSocketLogHandler()
    ws_handler.setLevel(logging.INFO)
    ws_handler.setFormatter(fmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(ws_handler)

    return logger


logger = setup_logger()
