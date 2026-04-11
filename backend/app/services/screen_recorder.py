import os
import platform
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

from app.utils.logger import logger


class ScreenRecorder:
    """
    Cross-platform screen recorder using ffmpeg.
    Windows  → gdigrab
    macOS    → avfoundation
    Linux    → x11grab
    """

    def __init__(self) -> None:
        self._process: Optional[subprocess.Popen] = None
        self._output_path: Optional[str] = None
        self._status: str = "idle"  # idle | recording | error
        self._region: Optional[Tuple[int, int, int, int]] = None  # x, y, w, h
        self._fps: int = 15
        self._platform = platform.system()
        self._start_time: Optional[float] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self, output_path: str, region: Optional[Tuple[int, int, int, int]] = None, fps: int = 15) -> None:
        if self._status == "recording":
            raise RuntimeError("Already recording")

        if not shutil.which("ffmpeg"):
            logger.error("ffmpeg not found in PATH")
            self._status = "error"
            raise FileNotFoundError("ffmpeg is not installed or not in PATH")

        safe_output = self._safe_output_path(output_path)
        Path(safe_output).parent.mkdir(parents=True, exist_ok=True)
        self._output_path = safe_output
        self._fps = fps
        if region:
            self._region = region

        cmd = self._build_ffmpeg_cmd(safe_output, fps)
        logger.info("Starting screen recording: %s", " ".join(cmd))

        try:
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            self._status = "recording"
            self._start_time = time.time()
        except Exception as exc:
            self._status = "error"
            logger.error("Failed to start ffmpeg: %s", exc)
            raise

    def stop(self) -> str:
        if self._status != "recording" or self._process is None:
            raise RuntimeError("Not currently recording")

        logger.info("Stopping screen recording")
        try:
            # Send 'q' to gracefully stop ffmpeg
            self._process.stdin.write(b"q\n")
            self._process.stdin.flush()
        except Exception:
            pass

        try:
            self._process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()

        self._status = "idle"
        output = self._output_path or ""
        self._process = None
        self._output_path = None
        self._start_time = None
        logger.info("Screen recording saved: %s", output)
        return output

    def get_status(self) -> Dict:
        elapsed = None
        if self._start_time and self._status == "recording":
            elapsed = time.time() - self._start_time
        return {
            "status": self._status,
            "output_path": self._output_path,
            "fps": self._fps,
            "region": self._region,
            "elapsed": elapsed,
        }

    def set_region(self, x: int, y: int, w: int, h: int) -> None:
        self._region = (x, y, w, h)

    def take_screenshot(self) -> bytes:
        """Capture a single frame and return it as PNG bytes."""
        if not shutil.which("ffmpeg"):
            raise FileNotFoundError("ffmpeg not found")

        from app.config.settings import settings
        out_file = Path(settings.CACHE_PATH) / "screenshot_tmp.png"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        cmd = self._build_screenshot_cmd(str(out_file))
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=10)
            data = out_file.read_bytes()
            return data
        finally:
            if out_file.exists():
                out_file.unlink()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_output_path(path: str) -> str:
        """Resolve and validate that the output path is inside the storage directory."""
        from app.config.settings import settings
        resolved = str(Path(path).resolve())
        storage = str(Path(settings.STORAGE_PATH).resolve())
        if not resolved.startswith(storage):
            raise ValueError(f"Output path '{resolved}' is outside the storage directory")
        return resolved

    def _build_ffmpeg_cmd(self, output_path: str, fps: int) -> list:
        if self._platform == "Windows":
            return self._cmd_windows(output_path, fps)
        elif self._platform == "Darwin":
            return self._cmd_macos(output_path, fps)
        else:
            return self._cmd_linux(output_path, fps)

    def _build_screenshot_cmd(self, output_path: str) -> list:
        if self._platform == "Windows":
            return [
                "ffmpeg", "-y", "-f", "gdigrab", "-i", "desktop",
                "-vframes", "1", output_path,
            ]
        elif self._platform == "Darwin":
            return [
                "ffmpeg", "-y", "-f", "avfoundation", "-i", "1:",
                "-vframes", "1", output_path,
            ]
        else:
            display = os.environ.get("DISPLAY", ":0")
            return [
                "ffmpeg", "-y", "-f", "x11grab", "-i", f"{display}+0,0",
                "-vframes", "1", output_path,
            ]

    def _region_args_windows(self):
        if self._region:
            x, y, w, h = self._region
            return [
                "-offset_x", str(x), "-offset_y", str(y),
                "-video_size", f"{w}x{h}",
            ]
        return []

    def _region_args_linux(self):
        display = os.environ.get("DISPLAY", ":0")
        if self._region:
            x, y, w, h = self._region
            return ["-i", f"{display}+{x},{y}", "-video_size", f"{w}x{h}"]
        return ["-i", f"{display}+0,0"]

    def _cmd_windows(self, output_path: str, fps: int) -> list:
        cmd = [
            "ffmpeg", "-y",
            "-f", "gdigrab",
            "-framerate", str(fps),
        ]
        cmd += self._region_args_windows()
        cmd += ["-i", "desktop"]
        cmd += self._output_encoding(output_path)
        return cmd

    def _cmd_macos(self, output_path: str, fps: int) -> list:
        if self._region:
            x, y, w, h = self._region
            video_size = f"{w}x{h}"
        else:
            video_size = "1920x1080"
        return [
            "ffmpeg", "-y",
            "-f", "avfoundation",
            "-framerate", str(fps),
            "-capture_cursor", "1",
            "-i", "1:",
            "-video_size", video_size,
        ] + self._output_encoding(output_path)

    def _cmd_linux(self, output_path: str, fps: int) -> list:
        display = os.environ.get("DISPLAY", ":0")
        cmd = [
            "ffmpeg", "-y",
            "-f", "x11grab",
            "-framerate", str(fps),
        ]
        if self._region:
            x, y, w, h = self._region
            cmd += ["-video_size", f"{w}x{h}", "-i", f"{display}+{x},{y}"]
        else:
            cmd += ["-i", f"{display}+0,0"]
        cmd += self._output_encoding(output_path)
        return cmd

    @staticmethod
    def _output_encoding(output_path: str) -> list:
        return [
            "-vcodec", "libx264",
            "-preset", "ultrafast",
            "-crf", "28",
            "-pix_fmt", "yuv420p",
            output_path,
        ]
