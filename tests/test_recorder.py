"""Unit tests for ScreenRecorder and AudioRecorder services."""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.screen_recorder import ScreenRecorder
from app.services.audio_recorder import AudioRecorder
from app.config.settings import settings

# Use valid paths inside the storage directory for all tests
VALID_VIDEO_PATH = os.path.join(settings.RECORDINGS_PATH, "test_video.mp4")
VALID_AUDIO_PATH = os.path.join(settings.RECORDINGS_PATH, "test_audio.wav")


# ── ScreenRecorder Tests ──────────────────────────────────────────────────────

class TestScreenRecorderInit(unittest.TestCase):
    """Test ScreenRecorder initialization."""

    def test_initial_status_is_idle(self):
        recorder = ScreenRecorder()
        self.assertEqual(recorder._status, "idle")

    def test_initial_process_is_none(self):
        recorder = ScreenRecorder()
        self.assertIsNone(recorder._process)

    def test_initial_output_path_is_none(self):
        recorder = ScreenRecorder()
        self.assertIsNone(recorder._output_path)


class TestScreenRecorderStatusTransitions(unittest.TestCase):
    """Test ScreenRecorder state transitions."""

    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    @patch("subprocess.Popen")
    def test_start_sets_recording_status(self, mock_popen, mock_which):
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc

        recorder = ScreenRecorder()
        recorder.start(VALID_VIDEO_PATH)
        self.assertEqual(recorder._status, "recording")

    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    @patch("subprocess.Popen")
    def test_stop_sets_idle_status(self, mock_popen, mock_which):
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_proc.wait.return_value = 0
        mock_proc.stdin = MagicMock()
        mock_popen.return_value = mock_proc

        recorder = ScreenRecorder()
        recorder.start(VALID_VIDEO_PATH)
        recorder.stop()
        self.assertEqual(recorder._status, "idle")

    @patch("shutil.which", return_value=None)
    def test_start_fails_if_ffmpeg_missing(self, mock_which):
        recorder = ScreenRecorder()
        with self.assertRaises(FileNotFoundError):
            recorder.start(VALID_VIDEO_PATH)
        self.assertEqual(recorder._status, "error")

    def test_double_start_raises(self):
        recorder = ScreenRecorder()
        recorder._status = "recording"
        with self.assertRaises(RuntimeError):
            recorder.start(VALID_VIDEO_PATH)

    def test_get_status_returns_dict(self):
        recorder = ScreenRecorder()
        status = recorder.get_status()
        self.assertIn("status", status)
        self.assertIn("output_path", status)

    def test_stop_when_idle_raises(self):
        recorder = ScreenRecorder()
        with self.assertRaises(RuntimeError):
            recorder.stop()

    def test_invalid_path_raises_value_error(self):
        recorder = ScreenRecorder()
        with self.assertRaises(ValueError):
            recorder._safe_output_path("/some/random/path/video.mp4")

    def test_valid_storage_path_accepted(self):
        recorder = ScreenRecorder()
        result = recorder._safe_output_path(VALID_VIDEO_PATH)
        self.assertIn("storage", result)


# ── AudioRecorder Tests ───────────────────────────────────────────────────────

class TestAudioRecorderInit(unittest.TestCase):
    """Test AudioRecorder initialization."""

    def test_initial_status_is_idle(self):
        ar = AudioRecorder()
        self.assertEqual(ar._status, "idle")

    def test_initial_thread_is_none(self):
        ar = AudioRecorder()
        self.assertIsNone(ar._thread)


class TestAudioRecorderDeviceListing(unittest.TestCase):
    """Test device listing."""

    def test_list_devices_without_pyaudio_returns_stub(self):
        import app.services.audio_recorder as ar_module
        original = ar_module.PYAUDIO_AVAILABLE
        ar_module.PYAUDIO_AVAILABLE = False
        try:
            ar = AudioRecorder()
            devices = ar.list_devices()
            # Stub mode returns at least one default device
            self.assertIsInstance(devices, list)
            self.assertGreaterEqual(len(devices), 1)
            self.assertEqual(devices[0]["name"], "Default (stub)")
        finally:
            ar_module.PYAUDIO_AVAILABLE = original

    def test_list_devices_returns_list(self):
        ar = AudioRecorder()
        devices = ar.list_devices()
        self.assertIsInstance(devices, list)


class TestAudioRecorderStatusTransitions(unittest.TestCase):
    """Test AudioRecorder recording lifecycle."""

    def test_start_sets_recording_status(self):
        ar = AudioRecorder()
        # Start uses a background thread; we can verify the status immediately after
        ar.start(VALID_AUDIO_PATH)
        self.assertEqual(ar._status, "recording")
        # Clean up
        ar.stop()

    def test_stop_sets_idle_status(self):
        ar = AudioRecorder()
        ar.start(VALID_AUDIO_PATH)
        ar.stop()
        self.assertEqual(ar._status, "idle")

    def test_invalid_path_raises_value_error(self):
        ar = AudioRecorder()
        with self.assertRaises(ValueError):
            ar.start("/invalid/path/audio.wav")

    def test_stop_when_idle_raises(self):
        ar = AudioRecorder()
        with self.assertRaises(RuntimeError):
            ar.stop()


if __name__ == "__main__":
    unittest.main()
