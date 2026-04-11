import io
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.utils.logger import logger

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract/Pillow not available; OcrEngine running in stub mode")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class OcrEngine:
    """
    OCR engine backed by Tesseract with Chinese language support.
    Specialised for extracting danmaku (barrage) text from WeChat Live screenshots.
    """

    # Approximate relative position of the danmaku panel in WeChat Live
    # (right ~30% of the frame, vertically centred)
    DANMAKU_REGION_RATIO = (0.70, 0.10, 1.00, 0.90)  # (left, top, right, bottom) as fractions

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def recognize_image(self, image_bytes: bytes) -> str:
        """Run OCR on raw image bytes and return extracted text."""
        if not TESSERACT_AVAILABLE:
            logger.warning("Tesseract unavailable – returning empty string")
            return ""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(img, lang="chi_sim+eng")
            return text.strip()
        except Exception as exc:
            logger.error("recognize_image error: %s", exc)
            return ""

    def recognize_danmaku(
        self,
        frame_bytes: bytes,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> List[str]:
        """
        Extract danmaku lines from a video frame.
        *region* is (x, y, width, height) in pixels; auto-detected if None.
        Returns a list of non-empty text lines.
        """
        if not TESSERACT_AVAILABLE:
            return []
        try:
            img = Image.open(io.BytesIO(frame_bytes))
            w, h = img.size

            if region:
                x, y, rw, rh = region
                crop = img.crop((x, y, x + rw, y + rh))
            else:
                left = int(w * self.DANMAKU_REGION_RATIO[0])
                top = int(h * self.DANMAKU_REGION_RATIO[1])
                right = int(w * self.DANMAKU_REGION_RATIO[2])
                bottom = int(h * self.DANMAKU_REGION_RATIO[3])
                crop = img.crop((left, top, right, bottom))

            crop = self._preprocess(crop)
            raw = pytesseract.image_to_string(crop, lang="chi_sim+eng", config="--psm 6")
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            return lines
        except Exception as exc:
            logger.error("recognize_danmaku error: %s", exc)
            return []

    def process_video_for_danmaku(
        self,
        video_path: str,
        interval: float = 1.0,
    ) -> List[Dict]:
        """
        Sample frames from *video_path* every *interval* seconds and run OCR.
        Returns [{timestamp, lines: [str]}, ...]
        """
        if not CV2_AVAILABLE:
            logger.warning("OpenCV not available – skipping video danmaku extraction")
            return []
        if not TESSERACT_AVAILABLE:
            logger.warning("Tesseract not available – skipping video danmaku extraction")
            return []

        import cv2 as _cv2

        cap = _cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")

        fps = cap.get(_cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(_cv2.CAP_PROP_FRAME_COUNT))
        step_frames = max(1, int(fps * interval))

        results: List[Dict] = []
        frame_idx = 0

        try:
            while frame_idx < total_frames:
                cap.set(_cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    break

                ok, buf = _cv2.imencode(".jpg", frame)
                if ok:
                    lines = self.recognize_danmaku(buf.tobytes())
                    if lines:
                        results.append({
                            "timestamp": frame_idx / fps,
                            "lines": lines,
                        })

                frame_idx += step_frames
        finally:
            cap.release()

        logger.info("Danmaku extraction complete: %d entries from %s", len(results), video_path)
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _preprocess(img: "Image.Image") -> "Image.Image":
        """Enhance image contrast for better OCR accuracy."""
        try:
            from PIL import ImageEnhance, ImageFilter
            img = img.convert("L")
            img = ImageEnhance.Contrast(img).enhance(2.0)
            img = img.filter(ImageFilter.SHARPEN)
            return img
        except Exception:
            return img
