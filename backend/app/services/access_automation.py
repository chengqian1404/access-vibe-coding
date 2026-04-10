"""
Access Automation Service - Controls Microsoft Access via pyautogui and pywin32
"""
import asyncio
import platform
import time
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from app.models.operation import ExecutionResult, OperationStep, StepResult, StepType


class AccessAutomation:
    """
    Automates Microsoft Access using pyautogui and (on Windows) pywin32.
    On non-Windows platforms, operations are simulated for development/testing.
    """

    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self._progress_callback: Optional[Callable] = None

        if self.is_windows:
            self._init_windows_modules()
        else:
            logger.warning(
                "Running on non-Windows platform. Automation will be simulated."
            )

    def _init_windows_modules(self):
        """Initialize Windows-specific modules."""
        try:
            import pyautogui
            import win32gui
            import win32con

            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            self.pyautogui = pyautogui
            self.win32gui = win32gui
            self.win32con = win32con
            logger.info("Windows automation modules loaded successfully")
        except ImportError as e:
            logger.warning(f"Failed to import Windows automation modules: {e}")
            self.is_windows = False

    def set_progress_callback(self, callback: Callable):
        """Set a callback function to report progress."""
        self._progress_callback = callback

    def _report_progress(self, step: int, total: int, message: str, screenshot: Optional[str] = None):
        """Report execution progress."""
        if self._progress_callback:
            self._progress_callback({
                "step": step,
                "total": total,
                "message": message,
                "screenshot": screenshot,
            })

    async def execute_steps(
        self, steps: List[OperationStep], dry_run: bool = False
    ) -> ExecutionResult:
        """Execute a list of automation steps."""
        total = len(steps)
        results = []
        start_time = time.time()

        logger.info(f"Starting execution of {total} steps (dry_run={dry_run})")

        for i, step in enumerate(steps):
            step_start = time.time()
            logger.debug(f"Executing step {step.step}/{total}: {step.type} - {step.description}")

            self._report_progress(i + 1, total, f"执行步骤 {i+1}/{total}: {step.description}")

            try:
                if dry_run:
                    result = await self._simulate_step(step)
                else:
                    result = await self._execute_step(step)

                result.duration = time.time() - step_start
                results.append(result)

                if not result.success:
                    logger.warning(f"Step {step.step} failed: {result.error}")
                    return ExecutionResult(
                        success=False,
                        total_steps=total,
                        completed_steps=i,
                        step_results=[r.model_dump() for r in results],
                        error=result.error,
                        execution_time=time.time() - start_time,
                    )

                # Small delay between steps
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Exception in step {step.step}: {e}")
                results.append(StepResult(
                    step=step.step,
                    success=False,
                    message="步骤执行失败",
                    error=str(e),
                    duration=time.time() - step_start,
                ))
                return ExecutionResult(
                    success=False,
                    total_steps=total,
                    completed_steps=i,
                    step_results=[r.model_dump() for r in results],
                    error=str(e),
                    execution_time=time.time() - start_time,
                )

        # Take final screenshot
        final_screenshot = None
        try:
            from app.services.screenshot_service import ScreenshotService
            ss = ScreenshotService()
            final_screenshot = ss.take_screenshot_base64()
        except Exception:
            pass

        return ExecutionResult(
            success=True,
            total_steps=total,
            completed_steps=total,
            step_results=[r.model_dump() for r in results],
            final_screenshot=final_screenshot,
            execution_time=time.time() - start_time,
        )

    async def _execute_step(self, step: OperationStep) -> StepResult:
        """Execute a single automation step."""
        if not self.is_windows:
            return await self._simulate_step(step)

        try:
            if step.type == StepType.CLICK:
                return self._do_click(step)
            elif step.type == StepType.DOUBLE_CLICK:
                return self._do_double_click(step)
            elif step.type == StepType.RIGHT_CLICK:
                return self._do_right_click(step)
            elif step.type == StepType.TYPE:
                return self._do_type(step)
            elif step.type == StepType.KEY_PRESS:
                return self._do_key_press(step)
            elif step.type == StepType.HOTKEY:
                return self._do_hotkey(step)
            elif step.type == StepType.WAIT:
                return await self._do_wait(step)
            elif step.type == StepType.SCREENSHOT:
                return self._do_screenshot(step)
            elif step.type == StepType.SCROLL:
                return self._do_scroll(step)
            elif step.type == StepType.MOVE:
                return self._do_move(step)
            elif step.type == StepType.FIND_WINDOW:
                return self._do_find_window(step)
            elif step.type == StepType.FOCUS_WINDOW:
                return self._do_focus_window(step)
            elif step.type == StepType.COM_CALL:
                return self._do_com_call(step)
            else:
                return StepResult(step=step.step, success=True, message=f"步骤类型 {step.type} 已跳过")

        except Exception as e:
            logger.error(f"Error executing step {step.step}: {e}")
            return StepResult(step=step.step, success=False, error=str(e))

    async def _simulate_step(self, step: OperationStep) -> StepResult:
        """Simulate a step (for non-Windows or dry run)."""
        await asyncio.sleep(0.05)
        return StepResult(
            step=step.step,
            success=True,
            message=f"[模拟] {step.description}",
        )

    def _do_click(self, step: OperationStep) -> StepResult:
        """Perform a mouse click."""
        x = step.params.get("x")
        y = step.params.get("y")
        if x is not None and y is not None:
            self.pyautogui.click(x, y)
        return StepResult(step=step.step, success=True, message=f"点击 ({x}, {y})")

    def _do_double_click(self, step: OperationStep) -> StepResult:
        """Perform a double click."""
        x = step.params.get("x")
        y = step.params.get("y")
        if x is not None and y is not None:
            self.pyautogui.doubleClick(x, y)
        return StepResult(step=step.step, success=True, message=f"双击 ({x}, {y})")

    def _do_right_click(self, step: OperationStep) -> StepResult:
        """Perform a right click."""
        x = step.params.get("x")
        y = step.params.get("y")
        if x is not None and y is not None:
            self.pyautogui.rightClick(x, y)
        return StepResult(step=step.step, success=True, message=f"右键点击 ({x}, {y})")

    def _do_type(self, step: OperationStep) -> StepResult:
        """Type text."""
        text = step.params.get("text", "")
        submit = step.params.get("submit", False)
        interval = step.params.get("interval", 0.05)

        self.pyautogui.write(text, interval=interval)
        if submit:
            self.pyautogui.press("enter")

        return StepResult(step=step.step, success=True, message=f"输入文本: {text}")

    def _do_key_press(self, step: OperationStep) -> StepResult:
        """Press a key."""
        key = step.params.get("key", "")
        presses = step.params.get("presses", 1)
        self.pyautogui.press(key, presses=presses)
        return StepResult(step=step.step, success=True, message=f"按键: {key}")

    def _do_hotkey(self, step: OperationStep) -> StepResult:
        """Press hotkey combination."""
        keys = step.params.get("keys", [])
        if keys:
            self.pyautogui.hotkey(*keys)
        return StepResult(step=step.step, success=True, message=f"快捷键: {'+'.join(keys)}")

    async def _do_wait(self, step: OperationStep) -> StepResult:
        """Wait for specified duration."""
        seconds = step.params.get("seconds", 1.0)
        await asyncio.sleep(seconds)
        return StepResult(step=step.step, success=True, message=f"等待 {seconds} 秒")

    def _do_screenshot(self, step: OperationStep) -> StepResult:
        """Take a screenshot."""
        try:
            from app.services.screenshot_service import ScreenshotService
            ss = ScreenshotService()
            screenshot_b64 = ss.take_screenshot_base64()
            return StepResult(
                step=step.step,
                success=True,
                message="截图已完成",
                screenshot=screenshot_b64,
            )
        except Exception as e:
            return StepResult(step=step.step, success=True, message="截图跳过", error=str(e))

    def _do_scroll(self, step: OperationStep) -> StepResult:
        """Scroll the mouse wheel."""
        clicks = step.params.get("clicks", 3)
        x = step.params.get("x")
        y = step.params.get("y")
        self.pyautogui.scroll(clicks, x=x, y=y)
        return StepResult(step=step.step, success=True, message=f"滚动 {clicks} 格")

    def _do_move(self, step: OperationStep) -> StepResult:
        """Move mouse to position."""
        x = step.params.get("x", 0)
        y = step.params.get("y", 0)
        duration = step.params.get("duration", 0.2)
        self.pyautogui.moveTo(x, y, duration=duration)
        return StepResult(step=step.step, success=True, message=f"移动到 ({x}, {y})")

    def _do_find_window(self, step: OperationStep) -> StepResult:
        """Find a window by title."""
        window_title = step.params.get("window_title", "")
        try:
            hwnd = self.win32gui.FindWindow(None, None)
            # Search for window with matching title
            def enum_windows_callback(hwnd, results):
                title = self.win32gui.GetWindowText(hwnd)
                if window_title.lower() in title.lower():
                    results.append(hwnd)

            windows = []
            self.win32gui.EnumWindows(enum_windows_callback, windows)

            if windows:
                return StepResult(step=step.step, success=True, message=f"找到窗口: {window_title}")
            else:
                return StepResult(
                    step=step.step,
                    success=False,
                    message=f"未找到窗口: {window_title}",
                    error=f"Window not found: {window_title}",
                )
        except Exception as e:
            return StepResult(step=step.step, success=False, error=str(e))

    def _do_focus_window(self, step: OperationStep) -> StepResult:
        """Bring a window to the foreground."""
        window_title = step.params.get("window_title", "")
        try:
            def enum_windows_callback(hwnd, results):
                title = self.win32gui.GetWindowText(hwnd)
                if window_title.lower() in title.lower():
                    results.append(hwnd)

            windows = []
            self.win32gui.EnumWindows(enum_windows_callback, windows)

            if windows:
                hwnd = windows[0]
                self.win32gui.ShowWindow(hwnd, self.win32con.SW_RESTORE)
                self.win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.3)
                return StepResult(step=step.step, success=True, message=f"已激活窗口: {window_title}")
            else:
                return StepResult(
                    step=step.step,
                    success=False,
                    message=f"未找到窗口: {window_title}",
                    error=f"Window not found: {window_title}",
                )
        except Exception as e:
            return StepResult(step=step.step, success=False, error=str(e))

    def _do_com_call(self, step: OperationStep) -> StepResult:
        """Execute a COM object method call (Windows only)."""
        try:
            import win32com.client

            prog_id = step.params.get("prog_id", "Access.Application")
            method = step.params.get("method", "")
            args = step.params.get("args", [])

            app = win32com.client.GetObject(Class=prog_id)
            if method:
                result = getattr(app, method)(*args)
                return StepResult(
                    step=step.step,
                    success=True,
                    message=f"COM调用成功: {method}",
                )
            return StepResult(step=step.step, success=True, message="COM连接成功")

        except Exception as e:
            logger.error(f"COM call failed: {e}")
            return StepResult(step=step.step, success=False, error=str(e))

    def find_access_window(self) -> Optional[int]:
        """Find the Microsoft Access window handle."""
        if not self.is_windows:
            return None

        try:
            windows = []

            def callback(hwnd, results):
                title = self.win32gui.GetWindowText(hwnd)
                if "microsoft access" in title.lower():
                    results.append(hwnd)

            self.win32gui.EnumWindows(callback, windows)
            return windows[0] if windows else None
        except Exception:
            return None

    def is_access_running(self) -> bool:
        """Check if Microsoft Access is currently running."""
        return self.find_access_window() is not None
