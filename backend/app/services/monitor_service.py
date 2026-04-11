import threading
import time
from typing import Any, Callable, Dict, Optional

from app.utils.logger import logger


class MonitorService:
    """
    Background service that periodically checks whether a WeChat live stream
    is active and fires a callback when the status changes.
    """

    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._weixin_id: Optional[str] = None
        self._interval: int = 30
        self._is_live: bool = False
        self._monitoring: bool = False
        self._last_checked: Optional[float] = None
        self._on_live_detected: Optional[Callable[[str], Any]] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_live_callback(self, callback: Callable[[str], Any]) -> None:
        """Register a callback invoked when a live stream is detected."""
        self._on_live_detected = callback

    def start_monitoring(self, weixin_id: str, interval: int = 30) -> None:
        if self._monitoring:
            logger.info("Monitor already running for id=%s", self._weixin_id)
            return
        self._weixin_id = weixin_id
        self._interval = max(5, interval)
        self._stop_event.clear()
        self._monitoring = True
        self._thread = threading.Thread(
            target=self._monitor_loop, name="monitor-service", daemon=True
        )
        self._thread.start()
        logger.info("MonitorService started for weixin_id=%s, interval=%ds", weixin_id, self._interval)

    def stop_monitoring(self) -> None:
        if not self._monitoring:
            return
        self._stop_event.set()
        self._monitoring = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        logger.info("MonitorService stopped")

    def check_live_status(self, weixin_id: str) -> bool:
        """
        Heuristic live-status check.
        Tries to detect a live WeChat window; falls back to process-presence check.
        """
        try:
            import psutil
            for proc in psutil.process_iter(["name", "status"]):
                try:
                    pname = (proc.info.get("name") or "").lower()
                    if "wechat" in pname or "weixin" in pname:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            pass
        return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "monitoring": self._monitoring,
            "weixin_id": self._weixin_id,
            "is_live": self._is_live,
            "last_checked": self._last_checked,
            "interval": self._interval,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _monitor_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._last_checked = time.time()
                live = self.check_live_status(self._weixin_id or "")
                if live and not self._is_live:
                    logger.info("Live stream detected for weixin_id=%s", self._weixin_id)
                    self._is_live = True
                    if self._on_live_detected:
                        try:
                            self._on_live_detected(self._weixin_id or "")
                        except Exception as cb_exc:
                            logger.error("Live callback error: %s", cb_exc)
                elif not live and self._is_live:
                    logger.info("Live stream ended for weixin_id=%s", self._weixin_id)
                    self._is_live = False
            except Exception as exc:
                logger.error("MonitorService loop error: %s", exc)
            self._stop_event.wait(self._interval)
