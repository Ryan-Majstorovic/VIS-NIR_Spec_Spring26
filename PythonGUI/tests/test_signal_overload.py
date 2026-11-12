import unittest

import numpy as np

from backend.core.state_manager import StateManager
from backend.models.config import CalibrationConfig, UserConfig
from backend.models.frames import BinaryFramePacket
from backend.models.status import ConnectionState


class SignalOverloadTests(unittest.TestCase):
    def setUp(self):
        config = CalibrationConfig(bias_counts=[3640] * 3694, bias_timing_profile_id=65537)
        self.state = StateManager(UserConfig(), config)
        self.state.set_connection_state(ConnectionState.connected)
        self.frame_id = 0

    def feed(self, timestamp, *, shielded=3640, active=2650, profile=65537, skip=0):
        raw = np.full(3694, shielded, dtype=np.uint16)
        raw[32:3680] = active
        self.frame_id += 1 + skip
        packet = BinaryFramePacket(
            self.frame_id, 3694, 32, 3648, 1, raw, 0,
            integration_us=100, timing_profile_id=profile,
        )
        self.state.update_from_frame(packet, received_at_s=timestamp)
        return self.state.signal_overload_active()

    def test_shielded_reference_drop_warns_on_flat_raw_signal(self):
        for timestamp in (0.00, 0.01, 0.02):
            self.assertFalse(self.feed(timestamp, shielded=1700, active=1650, profile=65538))
        self.assertFalse(self.feed(0.03, shielded=1700, active=1650))
        self.assertFalse(self.feed(0.04, shielded=1700, active=1650))
        self.assertTrue(self.feed(0.05, shielded=1700, active=1650))
        self.assertTrue(self.state.snapshot(include_spectrum=False).device.signal_overload)
        self.state.set_connection_state(ConnectionState.disconnected)
        self.assertFalse(self.state.signal_overload_active())
        self.assertFalse(self.state.snapshot(include_spectrum=False).device.signal_overload)

    def test_alternation_warns_and_fading_oscillations_delay_clearance(self):
        choppy = np.tile([1720, 3830], 1824)
        self.assertFalse(self.feed(0.00, active=choppy))
        self.assertFalse(self.feed(0.01, active=choppy))
        self.assertTrue(self.feed(0.02, active=choppy))
        self.assertTrue(self.feed(0.10, active=np.tile([3600, 3660], 1824)))
        self.assertTrue(self.feed(0.70, active=np.tile([3600, 3660], 1824)))
        self.assertTrue(self.feed(0.80))
        self.assertTrue(self.feed(0.95))
        self.assertTrue(self.feed(1.20))
        self.assertTrue(self.feed(1.25, skip=1))
        self.assertTrue(self.feed(1.40))
        self.assertFalse(self.feed(1.76))

    def test_isolated_jump_and_smooth_ramp_do_not_warn(self):
        ramp = np.linspace(1700, 3800, 3648, dtype=np.uint16)
        ramp[500] = 3800
        for timestamp in (0.0, 0.01, 0.02, 0.03):
            self.assertFalse(self.feed(timestamp, active=ramp))
