from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from backend.core.integration_control import IntegrationControl
from backend.core.saturation_capture import SaturationCapture
from backend.core.state_manager import StateManager
from backend.models.config import (
    CalibrationConfig, DEFAULT_SATURATION_CAPTURE_FRAME_COUNT, SATURATION_CAPTURE_INTEGRATION_US, UserConfig,
)
from backend.models.frames import BinaryFramePacket
from backend.models.status import ConnectionState
from backend.storage.calibration_store import CalibrationStore


class SaturationCaptureTests(unittest.TestCase):
    def setUp(self):
        self.state = StateManager(UserConfig(), CalibrationConfig(bias_counts=[3600] * 3694, bias_timing_profile_id=65537))
        self.state.set_connection_state(ConnectionState.connected)
        self.sent = []
        transport = SimpleNamespace(is_connected=lambda: True, write=self.sent.append)
        self.integration = IntegrationControl(transport, self.state)
        self.addCleanup(self.integration.reset)
        self.capture = SaturationCapture(self.state, self.integration)
        self.now = 0.0
        clock = patch("backend.core.saturation_capture.perf_counter", side_effect=lambda: self.now)
        clock.start()
        self.addCleanup(clock.stop)
        self.feed(20, 100, 3500)

    def feed(self, frame_id, integration_us, code, *, received_at=None, profile=65537,
             first_pixel=None, last_pixel=None, edge_count=1, non_active_code=3600):
        counts = np.full(3694, non_active_code, dtype=np.uint16)
        counts[32:3680] = code
        if first_pixel is not None:
            counts[32:32 + edge_count] = first_pixel
        if last_pixel is not None:
            counts[3680 - edge_count:3680] = last_pixel
        packet = BinaryFramePacket(
            frame_id, 3694, 32, 3648, 1, counts, 1,
            integration_us=integration_us, timing_profile_id=profile,
        )
        self.integration.receive_frame(packet)
        self.state.update_from_frame(packet)
        self.capture.receive_frame(packet, self.now if received_at is None else received_at)

    def confirm_capture_exposure(self):
        self.integration.receive_text(f"OK INTEG {SATURATION_CAPTURE_INTEGRATION_US} 21")
        self.feed(21, SATURATION_CAPTURE_INTEGRATION_US, 3500)
        self.capture.poll()

    def confirm_restore(self):
        self.integration.receive_text("OK INTEG 100 40")
        self.feed(40, 100, 3500)
        self.capture.poll()

    def test_confirm_capture_average_and_restore(self):
        self.assertTrue(self.capture.start(2).ok)
        self.assertEqual(self.sent, [b"INTEG 1000000\n"])
        self.capture.poll()
        self.assertEqual(self.capture.phase, "setting")
        self.confirm_capture_exposure()
        self.assertEqual(self.capture.phase, "ready")
        self.assertIn("SMA port", self.capture.message)
        self.feed(22, SATURATION_CAPTURE_INTEGRATION_US, 3600)
        self.assertEqual(self.capture.preview_counts[32], 3600)
        self.assertEqual(self.capture.active_pixels, range(32, 3680))
        self.assertEqual(self.capture.frames_collected, 0)
        self.now = 10.0
        self.capture.begin()
        self.feed(23, SATURATION_CAPTURE_INTEGRATION_US, 3600, received_at=9.9)
        self.feed(24, SATURATION_CAPTURE_INTEGRATION_US, 3600)
        self.now = 11.1
        self.feed(25, SATURATION_CAPTURE_INTEGRATION_US, 1900)
        self.assertEqual(self.capture.phase, "capturing")
        self.assertEqual(self.capture.frames_collected, 0)
        self.now = 12.1
        self.feed(26, SATURATION_CAPTURE_INTEGRATION_US, 1800)
        self.feed(26, SATURATION_CAPTURE_INTEGRATION_US, 1600)
        self.assertEqual(self.capture.frames_collected, 1)
        self.assertEqual(self.capture.preview_counts[32], 1800)
        self.now = 13.1
        self.feed(27, SATURATION_CAPTURE_INTEGRATION_US, 2200)
        self.capture.poll()
        reference = self.capture.reference
        self.assertIsNotNone(reference)
        self.assertEqual(reference.raw_counts[32:3680], [2000.0] * 3648)
        self.assertEqual(reference.dark_baseline[32], 3600)
        self.assertEqual(self.sent, [b"INTEG 1000000\n", b"INTEG 100\n"])
        self.assertEqual(self.capture.phase, "restoring")
        self.confirm_restore()
        self.assertFalse(self.capture.active)
        self.assertIn("Restored 100", self.capture.message)

        with TemporaryDirectory() as directory:
            path = Path(directory) / "calibration.json"
            path.write_text("{}", encoding="utf-8")
            store = CalibrationStore(path, path)
            self.assertIsNone(store.load().saturation_reference)
            config = CalibrationConfig(saturation_plot_reference=reference, use_calibrated_saturation_scale=False)
            store.save(config)
            self.assertEqual(store.load(), config)

    def test_reject_partial_coverage_and_use_matching_covered_bias(self):
        config = CalibrationConfig(bias_counts=[3550] * 3694, bias_timing_profile_id=65537)
        self.state.set_calibration_config(config)
        self.capture.start(2)
        self.confirm_capture_exposure()
        self.capture.begin()
        self.feed(22, SATURATION_CAPTURE_INTEGRATION_US, 2000)
        self.now = 1.1
        self.feed(23, SATURATION_CAPTURE_INTEGRATION_US, 2000, first_pixel=3500, edge_count=200)
        self.capture.poll()
        self.assertIsNone(self.capture.reference)
        self.assertEqual(self.capture.phase, "verifying")
        self.assertIn("covered reading", self.capture.message)
        self.now = 2.2
        self.feed(24, SATURATION_CAPTURE_INTEGRATION_US, 2000, first_pixel=2205, edge_count=200)
        self.assertEqual(self.capture.phase, "verifying")
        self.assertIn("uneven", self.capture.message)
        self.assertIn("205 counts", self.capture.preview_summary)
        self.now = 3.2
        self.feed(25, SATURATION_CAPTURE_INTEGRATION_US, 2000, first_pixel=2204)
        self.assertEqual(self.capture.phase, "capturing")
        self.now = 4.2
        self.feed(26, SATURATION_CAPTURE_INTEGRATION_US, 1600)
        self.assertEqual(self.capture.frames_collected, 1)
        self.now = 5.2
        self.feed(27, SATURATION_CAPTURE_INTEGRATION_US, 2000, first_pixel=2205, edge_count=200)
        self.assertEqual(self.capture.phase, "verifying")
        self.assertEqual(self.capture.frames_collected, 0)
        self.assertIn("restarted", self.capture.message)
        self.now = 6.2
        self.feed(28, SATURATION_CAPTURE_INTEGRATION_US, 2000)
        self.now = 7.2
        self.feed(29, SATURATION_CAPTURE_INTEGRATION_US, 2000)
        self.now = 8.2
        self.feed(30, SATURATION_CAPTURE_INTEGRATION_US, 2200)
        self.capture.poll()
        self.assertEqual(self.capture.reference.dark_baseline[32], 3550)
        self.assertEqual(self.capture.reference.raw_counts[32], 2100)

    def test_plot_reference_trims_eight_frames_after_measuring_covered_level(self):
        self.state.set_calibration_config(CalibrationConfig(bias_counts=[1000] * 3694, bias_timing_profile_id=65536))
        self.assertTrue(self.capture.start(DEFAULT_SATURATION_CAPTURE_FRAME_COUNT).ok)
        self.assertEqual(self.capture.phase, "cover_ready")
        self.assertFalse(self.sent)
        self.capture.begin()
        self.feed(21, 100, 1800)
        self.now = 0.5
        self.feed(22, 100, 3600)
        self.capture.poll()
        self.assertEqual(self.sent, [b"INTEG 1000000\n"])
        self.integration.receive_text("OK INTEG 1000000 23")
        self.feed(23, 1000000, 1800, non_active_code=1800)
        self.capture.poll()
        self.capture.begin()
        self.feed(24, 1000000, 1800)
        self.now = 1.6
        self.feed(25, 1000000, 1800, first_pixel=3500, edge_count=100, non_active_code=1800)
        for index in range(8):
            self.now += 1.0
            self.feed(26 + index, 1000000, 1760 + index * 10, first_pixel=3500, last_pixel=1000,
                      edge_count=100, non_active_code=1800)
            self.assertEqual(self.capture.frames_collected, index + 1)
        self.capture.poll()
        self.confirm_restore()
        reference = self.capture.reference
        self.assertEqual(reference.frame_count, 8)
        self.assertEqual(reference.plateau_adc, 1795)
        self.assertEqual(reference.raw_counts[32], 3500)
        self.assertEqual(reference.raw_counts[3679], 1000)
        self.assertEqual(reference.dark_baseline[32], 3600)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "calibration.json"
            store = CalibrationStore(path, path)
            config = CalibrationConfig(saturation_plot_reference=reference)
            store.save(config)
            self.assertEqual(store.load(), config)

    def test_cancel_pending_change_then_restore(self):
        self.capture.start(8)
        self.capture.cancel()
        self.capture.poll()
        self.assertEqual(len(self.sent), 1)
        self.confirm_capture_exposure()
        self.assertEqual(self.sent[-1], b"INTEG 100\n")
        self.confirm_restore()
        self.assertIsNone(self.capture.reference)
        self.assertIn("cancelled", self.capture.message)

    def test_disconnect_during_capture_reports_missing_restore(self):
        self.capture.start(8)
        self.confirm_capture_exposure()
        self.capture.begin()
        self.state.set_connection_state(ConnectionState.disconnected)
        self.capture.poll()
        self.assertFalse(self.capture.active)
        self.assertIsNone(self.capture.reference)
        self.assertIn("could not be restored", self.capture.message)
        self.assertEqual(len(self.sent), 1)

    def test_capture_timeout_restores_previous_exposure(self):
        self.capture.start(8)
        self.confirm_capture_exposure()
        self.capture.begin()
        self.now = 5.1
        self.capture.poll()
        self.assertEqual(self.sent[-1], b"INTEG 100\n")
        self.confirm_restore()
        self.assertIsNone(self.capture.reference)
        self.assertIn("Timed out", self.capture.message)

    def test_profile_change_during_capture_restores_previous_exposure(self):
        self.capture.start(8)
        self.confirm_capture_exposure()
        self.capture.begin()
        self.feed(22, SATURATION_CAPTURE_INTEGRATION_US, 2000, profile=65538)
        self.capture.poll()
        self.assertEqual(self.sent[-1], b"INTEG 100\n")
        self.confirm_restore()
        self.assertIsNone(self.capture.reference)
        self.assertIn("profile or pixel geometry changed", self.capture.message)
