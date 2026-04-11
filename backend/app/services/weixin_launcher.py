import platform
import subprocess
import sys
import time
from typing import Optional

from app.utils.logger import logger


class WeixinLauncher:
    """Utilities to detect, launch, and interact with WeChat desktop client."""

    WEIXIN_PROCESS_NAMES = {
        "Windows": ["WeChat.exe", "Weixin.exe"],
        "Darwin": ["WeChat", "微信"],
        "Linux": ["wechat", "WeChat"],
    }

    def __init__(self) -> None:
        self._platform = platform.system()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_weixin_running(self) -> bool:
        """Return True if a WeChat process is currently running."""
        try:
            import psutil
            names = self.WEIXIN_PROCESS_NAMES.get(self._platform, [])
            for proc in psutil.process_iter(["name"]):
                try:
                    pname = proc.info.get("name", "") or ""
                    if any(n.lower() in pname.lower() for n in names):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            logger.warning("psutil not available; falling back to subprocess check")
            return self._fallback_check()
        return False

    def open_weixin(self) -> bool:
        """Attempt to open the WeChat desktop client."""
        if self.is_weixin_running():
            logger.info("WeChat is already running")
            return self.find_weixin_window()

        logger.info("Attempting to launch WeChat on %s", self._platform)
        try:
            if self._platform == "Windows":
                return self._open_windows()
            elif self._platform == "Darwin":
                return self._open_macos()
            else:
                return self._open_linux()
        except Exception as exc:
            logger.error("Failed to open WeChat: %s", exc)
            return False

    def find_weixin_window(self) -> bool:
        """Try to bring WeChat window to the foreground. Returns True on success."""
        try:
            if self._platform == "Windows":
                return self._focus_windows()
            elif self._platform == "Darwin":
                return self._focus_macos()
            else:
                return self._focus_linux()
        except Exception as exc:
            logger.warning("find_weixin_window error: %s", exc)
            return False

    def open_live_stream(self, weixin_id: str) -> bool:
        """
        Attempt to navigate WeChat to a specific live stream.
        WeChat does not expose a public deep-link URL scheme for live streams,
        so we provide instructional guidance and try best-effort automation.
        """
        logger.info("Attempting to open live stream for id: %s", weixin_id)
        if not self.is_weixin_running():
            if not self.open_weixin():
                logger.error("Cannot open WeChat")
                return False
            time.sleep(3)

        self.find_weixin_window()

        # WeChat mini-program / channel URL scheme (best-effort)
        wechat_url = f"weixin://dl/channels?id={weixin_id}"
        try:
            if self._platform == "Windows":
                subprocess.Popen(["cmd", "/c", "start", wechat_url], shell=False)
            elif self._platform == "Darwin":
                subprocess.Popen(["open", wechat_url])
            else:
                subprocess.Popen(["xdg-open", wechat_url])
            logger.info("Sent URL scheme: %s", wechat_url)
            return True
        except Exception as exc:
            logger.warning("URL scheme launch failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Platform helpers
    # ------------------------------------------------------------------

    def _open_windows(self) -> bool:
        common_paths = [
            r"C:\Program Files\Tencent\WeChat\WeChat.exe",
            r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
        ]
        for path in common_paths:
            try:
                subprocess.Popen([path])
                logger.info("Launched WeChat from %s", path)
                return True
            except FileNotFoundError:
                continue
        # Try via Start Menu
        try:
            subprocess.Popen(["start", "WeChat"], shell=True)
            return True
        except Exception:
            return False

    def _open_macos(self) -> bool:
        for app_name in ("WeChat", "微信"):
            try:
                result = subprocess.run(
                    ["open", "-a", app_name], capture_output=True, timeout=5
                )
                if result.returncode == 0:
                    logger.info("Launched %s on macOS", app_name)
                    return True
            except Exception:
                continue
        return False

    def _open_linux(self) -> bool:
        for cmd in ("wechat", "wechat-uos", "flatpak run com.tencent.WeChat"):
            try:
                subprocess.Popen(cmd.split())
                return True
            except FileNotFoundError:
                continue
        return False

    def _focus_windows(self) -> bool:
        try:
            import ctypes
            import ctypes.wintypes

            HWND = ctypes.wintypes.HWND

            def callback(hwnd, lParam):
                title = ctypes.create_unicode_buffer(256)
                ctypes.windll.user32.GetWindowTextW(hwnd, title, 256)
                if "微信" in title.value or "WeChat" in title.value:
                    ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                    return False
                return True

            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
            ctypes.windll.user32.EnumWindows(WNDENUMPROC(callback), 0)
            return True
        except Exception as exc:
            logger.warning("_focus_windows error: %s", exc)
            return False

    def _focus_macos(self) -> bool:
        script = 'tell application "WeChat" to activate'
        try:
            subprocess.run(["osascript", "-e", script], timeout=5, check=True)
            return True
        except Exception:
            return False

    def _focus_linux(self) -> bool:
        try:
            subprocess.run(["wmctrl", "-a", "WeChat"], timeout=5)
            return True
        except Exception:
            return False

    def _fallback_check(self) -> bool:
        try:
            if self._platform == "Windows":
                out = subprocess.check_output(["tasklist"], text=True)
                return "WeChat" in out or "Weixin" in out
            elif self._platform == "Darwin":
                out = subprocess.check_output(["pgrep", "-i", "wechat"], text=True)
                return bool(out.strip())
            else:
                out = subprocess.check_output(["pgrep", "-i", "wechat"], text=True)
                return bool(out.strip())
        except Exception:
            return False
