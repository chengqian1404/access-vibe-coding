import threading
import time
import wave
from pathlib import Path
from typing import Dict, List, Optional

from app.utils.logger import logger

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("pyaudio not available; AudioRecorder will use stub mode")


CHUNK = 1024
FORMAT_BITS = 16
CHANNELS = 2
RATE = 44100
PYAUDIO_FORMAT = 8  # pyaudio.paInt16


class AudioRecorder:
    """Records system/microphone audio to WAV using pyaudio."""

    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._status: str = "idle"
        self._output_path: Optional[str] = None
        self._audio_level: float = 0.0
        self._device_index: Optional[int] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_devices(self) -> List[Dict]:
        if not PYAUDIO_AVAILABLE:
            return [{"index": 0, "name": "Default (stub)", "channels": 2, "rate": 44100}]
        pa = pyaudio.PyAudio()
        devices = []
        try:
            for i in range(pa.get_device_count()):
                try:
                    info = pa.get_device_info_by_index(i)
                    if info.get("maxInputChannels", 0) > 0:
                        devices.append({
                            "index": i,
                            "name": info.get("name", f"Device {i}"),
                            "channels": int(info.get("maxInputChannels", 1)),
                            "rate": int(info.get("defaultSampleRate", RATE)),
                        })
                except Exception:
                    continue
        finally:
            pa.terminate()
        return devices

    def start(self, output_path: str, device_index: Optional[int] = None) -> None:
        if self._status == "recording":
            raise RuntimeError("Already recording")

        safe_output = self._safe_output_path(output_path)
        Path(safe_output).parent.mkdir(parents=True, exist_ok=True)
        self._output_path = safe_output
        self._device_index = device_index
        self._stop_event.clear()
        self._status = "recording"

        self._thread = threading.Thread(
            target=self._record_thread,
            name="audio-recorder",
            daemon=True,
        )
        self._thread.start()
        logger.info("AudioRecorder started → %s", output_path)

    def stop(self) -> str:
        if self._status != "recording":
            raise RuntimeError("Not currently recording")
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=10)
            self._thread = None
        self._status = "idle"
        path = self._output_path or ""
        logger.info("AudioRecorder stopped. Saved → %s", path)
        return path

    def get_status(self) -> Dict:
        return {
            "status": self._status,
            "output_path": self._output_path,
            "audio_level": self._audio_level,
            "device_index": self._device_index,
        }

    def get_audio_level(self) -> float:
        return self._audio_level

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_output_path(path: str) -> str:
        from app.config.settings import settings
        resolved = str(Path(path).resolve())
        storage = str(Path(settings.STORAGE_PATH).resolve())
        if not resolved.startswith(storage):
            raise ValueError(f"Output path '{resolved}' is outside the storage directory")
        return resolved

    def _record_thread(self) -> None:
        if not PYAUDIO_AVAILABLE:
            self._stub_record()
            return

        pa = pyaudio.PyAudio()
        stream = None
        wf = None
        try:
            open_kwargs = {
                "format": PYAUDIO_FORMAT,
                "channels": CHANNELS,
                "rate": RATE,
                "input": True,
                "frames_per_buffer": CHUNK,
            }
            if self._device_index is not None:
                open_kwargs["input_device_index"] = self._device_index

            stream = pa.open(**open_kwargs)

            wf = wave.open(self._output_path, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pa.get_sample_size(PYAUDIO_FORMAT))
            wf.setframerate(RATE)

            while not self._stop_event.is_set():
                data = stream.read(CHUNK, exception_on_overflow=False)
                wf.writeframes(data)
                self._audio_level = self._compute_level(data)
        except Exception as exc:
            logger.error("AudioRecorder thread error: %s", exc)
            self._status = "error"
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception:
                    pass
            if wf:
                try:
                    wf.close()
                except Exception:
                    pass
            pa.terminate()
            self._audio_level = 0.0

    def _stub_record(self) -> None:
        """Write a minimal silent WAV when pyaudio is unavailable."""
        try:
            with wave.open(self._output_path, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(RATE)
                while not self._stop_event.is_set():
                    wf.writeframes(b"\x00" * CHUNK * 2 * CHANNELS)
                    time.sleep(CHUNK / RATE)
        except Exception as exc:
            logger.error("Stub record error: %s", exc)

    @staticmethod
    def _compute_level(data: bytes) -> float:
        """Return RMS amplitude normalised to 0-1."""
        try:
            import array as arr
            import math
            samples = arr.array("h", data)
            if not samples:
                return 0.0
            rms = math.sqrt(sum(s * s for s in samples) / len(samples))
            return min(1.0, rms / 32768.0)
        except Exception:
            return 0.0
