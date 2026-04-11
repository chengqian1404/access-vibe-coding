"""Unit tests for MonitorService."""

import sys
import os
import time
import threading
import unittest
from unittest.mock import MagicMock, patch, call

# Ensure backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.monitor_service import MonitorService


class TestMonitorServiceInit(unittest.TestCase):
    """Test MonitorService initialization."""

    def test_default_state(self):
        svc = MonitorService()
        self.assertFalse(svc._monitoring)
        self.assertFalse(svc._is_live)
        self.assertIsNone(svc._weixin_id)
        self.assertIsNone(svc._thread)
        self.assertIsNone(svc._on_live_detected)

    def test_default_interval(self):
        svc = MonitorService()
        self.assertEqual(svc._interval, 30)


class TestMonitorServiceStartStop(unittest.TestCase):
    """Test start_monitoring / stop_monitoring lifecycle."""

    def setUp(self):
        self.svc = MonitorService()

    def tearDown(self):
        if self.svc._monitoring:
            self.svc.stop_monitoring()

    def test_start_sets_monitoring_flag(self):
        with patch.object(self.svc, "check_live_status", return_value=False):
            self.svc.start_monitoring("test_id", interval=5)
            self.assertTrue(self.svc._monitoring)
            self.assertEqual(self.svc._weixin_id, "test_id")

    def test_stop_clears_monitoring_flag(self):
        with patch.object(self.svc, "check_live_status", return_value=False):
            self.svc.start_monitoring("test_id", interval=5)
            self.svc.stop_monitoring()
            # Give the thread a moment to exit
            time.sleep(0.2)
            self.assertFalse(self.svc._monitoring)

    def test_double_start_is_idempotent(self):
        with patch.object(self.svc, "check_live_status", return_value=False):
            self.svc.start_monitoring("id1", interval=5)
            thread_before = self.svc._thread
            self.svc.start_monitoring("id2", interval=5)
            # Second call should not replace the thread
            self.assertIs(self.svc._thread, thread_before)

    def test_interval_minimum_is_five(self):
        with patch.object(self.svc, "check_live_status", return_value=False):
            self.svc.start_monitoring("id", interval=1)
            self.assertEqual(self.svc._interval, 5)


class TestMonitorServiceStatus(unittest.TestCase):
    """Test get_status reporting."""

    def test_status_when_idle(self):
        svc = MonitorService()
        status = svc.get_status()
        self.assertFalse(status["monitoring"])
        self.assertFalse(status["is_live"])
        self.assertIsNone(status["weixin_id"])

    def test_status_when_monitoring(self):
        svc = MonitorService()
        with patch.object(svc, "check_live_status", return_value=False):
            svc.start_monitoring("abc", interval=5)
            status = svc.get_status()
            self.assertTrue(status["monitoring"])
            self.assertEqual(status["weixin_id"], "abc")
            svc.stop_monitoring()


class TestMonitorServiceCallback(unittest.TestCase):
    """Test live-detected callback invocation."""

    def test_callback_fired_when_live_detected(self):
        svc = MonitorService()
        callback = MagicMock()
        svc.set_live_callback(callback)

        fired = threading.Event()

        def fake_check(weixin_id):
            fired.set()
            return True

        with patch.object(svc, "check_live_status", side_effect=fake_check):
            svc.start_monitoring("test", interval=5)
            fired.wait(timeout=2.0)
            time.sleep(0.1)
            svc.stop_monitoring()

        callback.assert_called()


if __name__ == "__main__":
    unittest.main()
