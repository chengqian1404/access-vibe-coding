import math
import os
from pathlib import Path
from typing import Dict, List, Optional

from app.utils.logger import logger

MAX_WHISPER_BYTES = 24 * 1024 * 1024  # 24 MB (Whisper limit is 25 MB)


class AudioProcessor:
    """Transcribes audio files using the OpenAI Whisper API."""

    def __init__(self) -> None:
        self._status: str = "idle"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def transcribe(self, audio_path: str) -> List[Dict]:
        """
        Transcribe audio file and return a list of segment dicts:
        [{start, end, text, confidence}, ...]
        Automatically chunks files larger than Whisper's 25 MB limit.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        self._status = "transcribing"
        try:
            file_size = os.path.getsize(audio_path)
            if file_size > MAX_WHISPER_BYTES:
                logger.info("Audio file %d bytes – splitting into chunks", file_size)
                return self._transcribe_chunked(audio_path)
            else:
                return self._transcribe_single(audio_path)
        finally:
            self._status = "idle"

    def get_status(self) -> Dict:
        return {"status": self._status}

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_client(self):
        from app.services.config_manager import config_manager
        from app.config.settings import settings
        from openai import OpenAI

        whisper_key = config_manager.get("whisper_api_key") or settings.WHISPER_API_KEY
        if not whisper_key:
            # Fall back to the general OpenAI key
            whisper_key = config_manager.get("openai_api_key") or settings.OPENAI_API_KEY
        if not whisper_key:
            raise ValueError("WHISPER_API_KEY / OPENAI_API_KEY is not configured")
        return OpenAI(api_key=whisper_key)

    def _transcribe_single(self, audio_path: str, offset_seconds: float = 0.0) -> List[Dict]:
        client = self._get_client()
        logger.info("Transcribing %s (offset=%.1fs)", audio_path, offset_seconds)
        with open(audio_path, "rb") as f:
            raw = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="zh",
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        segments = []
        if hasattr(raw, "segments") and raw.segments:
            for seg in raw.segments:
                seg_dict = seg if isinstance(seg, dict) else vars(seg) if hasattr(seg, "__dict__") else {}
                start = float(seg_dict.get("start") or getattr(seg, "start", 0.0))
                end = float(seg_dict.get("end") or getattr(seg, "end", 0.0))
                text = (seg_dict.get("text") or getattr(seg, "text", "")).strip()
                logprob = float(seg_dict.get("avg_logprob") or getattr(seg, "avg_logprob", -0.3))
                segments.append({
                    "start": start + offset_seconds,
                    "end": end + offset_seconds,
                    "text": text,
                    "confidence": logprob,
                })
        else:
            text = getattr(raw, "text", "") or ""
            if text:
                segments.append({
                    "start": offset_seconds,
                    "end": offset_seconds,
                    "text": text.strip(),
                    "confidence": 0.8,
                })
        return segments

    def _transcribe_chunked(self, audio_path: str) -> List[Dict]:
        """Split audio into ~20 MB WAV chunks and transcribe each."""
        try:
            import wave
            import struct
        except ImportError:
            raise ImportError("wave module required for chunked transcription")

        chunk_dir = Path(audio_path).parent / "_chunks"
        chunk_dir.mkdir(parents=True, exist_ok=True)

        all_segments: List[Dict] = []

        try:
            with wave.open(audio_path, "rb") as wf:
                n_channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                framerate = wf.getframerate()
                n_frames = wf.getnframes()

                bytes_per_frame = n_channels * sampwidth
                max_frames = MAX_WHISPER_BYTES // bytes_per_frame
                chunk_idx = 0
                offset_frames = 0

                while offset_frames < n_frames:
                    frames_to_read = min(max_frames, n_frames - offset_frames)
                    wf.setpos(offset_frames)
                    data = wf.readframes(frames_to_read)

                    chunk_path = str(chunk_dir / f"chunk_{chunk_idx:04d}.wav")
                    with wave.open(chunk_path, "wb") as cw:
                        cw.setnchannels(n_channels)
                        cw.setsampwidth(sampwidth)
                        cw.setframerate(framerate)
                        cw.writeframes(data)

                    offset_seconds = offset_frames / framerate
                    segments = self._transcribe_single(chunk_path, offset_seconds)
                    all_segments.extend(segments)

                    offset_frames += frames_to_read
                    chunk_idx += 1
                    logger.info("Chunk %d transcribed (%d segments)", chunk_idx, len(segments))
        finally:
            # Clean up chunk files
            for f in chunk_dir.glob("chunk_*.wav"):
                try:
                    f.unlink()
                except Exception:
                    pass
            try:
                chunk_dir.rmdir()
            except Exception:
                pass

        return all_segments
