import base64
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.utils.logger import logger

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("opencv-python not available; VideoProcessor running in stub mode")


class VideoProcessor:
    """Extracts keyframes and scene boundaries from video files using OpenCV."""

    HISTOGRAM_THRESHOLD = 0.6  # cosine similarity threshold for scene cut

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_keyframes(self, video_path: str, output_dir: str) -> List[str]:
        """
        Detect scene changes and save one frame per scene.
        Returns list of saved image file paths.
        """
        if not CV2_AVAILABLE:
            logger.warning("OpenCV unavailable – returning empty keyframes list")
            return []

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")

        saved_paths: List[str] = []
        prev_hist = None
        frame_idx = 0
        scene_idx = 0
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                hist = self._frame_histogram(frame)
                is_new_scene = prev_hist is None or self._hist_diff(prev_hist, hist) > self.HISTOGRAM_THRESHOLD

                if is_new_scene:
                    out_path = os.path.join(output_dir, f"keyframe_{scene_idx:04d}.jpg")
                    cv2.imwrite(out_path, frame)
                    saved_paths.append(out_path)
                    scene_idx += 1
                    prev_hist = hist

                frame_idx += 1
        finally:
            cap.release()

        logger.info("Extracted %d keyframes from %s", len(saved_paths), video_path)
        return saved_paths

    def detect_scenes(self, video_path: str) -> List[Dict]:
        """
        Detect scene boundaries.
        Returns list of {scene_idx, start_frame, start_time, end_frame, end_time}.
        """
        if not CV2_AVAILABLE:
            return []

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")

        scenes: List[Dict] = []
        prev_hist = None
        frame_idx = 0
        scene_start = 0
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    # Close last scene
                    if scenes or frame_idx > 0:
                        scenes.append({
                            "scene_idx": len(scenes),
                            "start_frame": scene_start,
                            "start_time": scene_start / fps,
                            "end_frame": frame_idx,
                            "end_time": frame_idx / fps,
                        })
                    break

                hist = self._frame_histogram(frame)
                if prev_hist is not None and self._hist_diff(prev_hist, hist) > self.HISTOGRAM_THRESHOLD:
                    scenes.append({
                        "scene_idx": len(scenes),
                        "start_frame": scene_start,
                        "start_time": scene_start / fps,
                        "end_frame": frame_idx,
                        "end_time": frame_idx / fps,
                    })
                    scene_start = frame_idx

                prev_hist = hist
                frame_idx += 1
        finally:
            cap.release()

        return scenes

    def extract_frame_at(self, video_path: str, timestamp: float) -> bytes:
        """Extract a single frame at *timestamp* seconds and return as JPEG bytes."""
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV is required for extract_frame_at")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")
        try:
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            target_frame = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ret, frame = cap.read()
            if not ret:
                raise ValueError(f"Cannot read frame at timestamp {timestamp}s")
            ok, buf = cv2.imencode(".jpg", frame)
            if not ok:
                raise RuntimeError("Failed to encode frame as JPEG")
            return buf.tobytes()
        finally:
            cap.release()

    def merge_av(self, video_path: str, audio_path: str, output_path: str) -> str:
        """Merge separate video and audio files into one MP4 using ffmpeg."""
        import shutil
        import subprocess

        if not shutil.which("ffmpeg"):
            raise FileNotFoundError("ffmpeg not found in PATH")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "experimental",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg merge failed: {result.stderr[-500:]}")
        logger.info("Merged AV → %s", output_path)
        return output_path

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _frame_histogram(frame) -> "np.ndarray":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        cv2.normalize(hist, hist)
        return hist.flatten()

    @staticmethod
    def _hist_diff(h1, h2) -> float:
        """Return 1 - correlation (0 = identical, 1 = completely different)."""
        corr = cv2.compareHist(h1.reshape(-1, 1), h2.reshape(-1, 1), cv2.HISTCMP_CORREL)
        return 1.0 - float(corr)
