"""
Screenshot Service - Capture and process screenshots
"""
import base64
import io
import platform
from typing import Optional, Tuple

from loguru import logger


class ScreenshotService:
    """Handles screenshot capture and processing."""

    def __init__(self):
        self.is_windows = platform.system() == "Windows"

    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[bytes]:
        """
        Take a screenshot and return raw bytes.

        Args:
            region: Optional tuple (x, y, width, height) to capture a specific region

        Returns:
            JPEG image bytes or None if failed
        """
        try:
            from PIL import Image, ImageGrab

            if region:
                x, y, w, h = region
                screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            else:
                screenshot = ImageGrab.grab()

            # Convert to JPEG for smaller size
            output = io.BytesIO()
            screenshot = screenshot.convert("RGB")
            screenshot.save(output, format="JPEG", quality=85, optimize=True)
            return output.getvalue()

        except ImportError:
            logger.warning("PIL not available, using pyautogui fallback")
            return self._take_screenshot_pyautogui(region)
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None

    def _take_screenshot_pyautogui(
        self, region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[bytes]:
        """Fallback screenshot using pyautogui."""
        try:
            import pyautogui
            from PIL import Image

            screenshot = pyautogui.screenshot(region=region)
            output = io.BytesIO()
            screenshot.save(output, format="JPEG", quality=85)
            return output.getvalue()
        except Exception as e:
            logger.error(f"pyautogui screenshot failed: {e}")
            return None

    def take_screenshot_base64(
        self, region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[str]:
        """
        Take a screenshot and return as base64-encoded string.

        Returns:
            Base64-encoded JPEG string or None if failed
        """
        img_bytes = self.take_screenshot(region)
        if img_bytes:
            return base64.b64encode(img_bytes).decode("utf-8")
        return None

    def take_window_screenshot(self, window_title: str) -> Optional[str]:
        """Take a screenshot of a specific window by title."""
        if not self.is_windows:
            return self.take_screenshot_base64()

        try:
            import win32gui
            import win32ui
            import win32con
            from PIL import Image

            def find_window(title):
                result = []
                def callback(hwnd, _):
                    if title.lower() in win32gui.GetWindowText(hwnd).lower():
                        result.append(hwnd)
                win32gui.EnumWindows(callback, None)
                return result[0] if result else None

            hwnd = find_window(window_title)
            if not hwnd:
                return self.take_screenshot_base64()

            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            w = right - left
            h = bottom - top

            return self.take_screenshot_base64(region=(left, top, w, h))

        except Exception as e:
            logger.warning(f"Window screenshot failed, falling back to full screen: {e}")
            return self.take_screenshot_base64()

    def save_screenshot(self, filepath: str, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """Save screenshot to a file."""
        img_bytes = self.take_screenshot(region)
        if img_bytes:
            try:
                with open(filepath, "wb") as f:
                    f.write(img_bytes)
                return True
            except Exception as e:
                logger.error(f"Failed to save screenshot: {e}")
        return False
