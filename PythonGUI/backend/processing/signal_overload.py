"""Detect persistent distortion in the detector's raw ADC samples."""
from __future__ import annotations

import numpy as np

from backend.models.config import CalibrationConfig
from backend.models.frames import BinaryFramePacket, FramePacket
from backend.processing.spectrum_builder import FRAME_DARK_END_INDEX, FRAME_DARK_START_INDEX


class SignalOverload:
    """Latch the warning through the recovery period, including fading oscillations."""

    def __init__(self) -> None:
        self.active = False
        self._bad_frames = 0
        self._clean_frames = 0
        self._clean_since = 0.0
        self._last_frame_id: int | None = None

    def observe(
        self, frame: FramePacket | BinaryFramePacket, calibration: CalibrationConfig, adc_bits: int, received_at_s: float,
    ) -> bool:
        start = frame.effective_start
        stop = start + frame.effective_count
        consecutive = self._last_frame_id is not None and (
            (frame.frame_counter - self._last_frame_id) & 0xFFFFFFFF
        ) == 1
        self._last_frame_id = frame.frame_counter
        valid = not frame.flags & 2 and 0 <= start < stop <= len(frame.adc_counts) == frame.sample_count
        if not consecutive or not valid:
            self._bad_frames = 0
            self._clean_frames = 0
        if not valid:
            return self.active

        full_scale = (1 << adc_bits) - 1
        raw = np.asarray(frame.adc_counts)
        reference_drop = 0.0
        if (
            start > FRAME_DARK_END_INDEX
            and len(calibration.bias_counts) > FRAME_DARK_END_INDEX
            and frame.timing_profile_id is not None
            and calibration.bias_timing_profile_id == frame.timing_profile_id
        ):
            shielded = slice(FRAME_DARK_START_INDEX, FRAME_DARK_END_INDEX + 1)
            reference_drop = float(np.median(calibration.bias_counts[shielded]) - np.median(raw[shielded]))

        # A broad, alternating ADC pattern survives calibration and normalization changes.
        steps = np.diff(raw[start:stop].astype(np.int32))
        alternating = (steps[:-1] > 0) != (steps[1:] > 0)
        reversal_size = np.minimum(np.abs(steps[:-1]), np.abs(steps[1:]))[alternating]
        reversal_limit = 0.20 * len(alternating)
        if self.active:
            still_distorted = reference_drop >= full_scale * 0.05 or (
                len(alternating) > 0 and np.count_nonzero(reversal_size >= full_scale * 0.01) >= reversal_limit
            )
            if still_distorted:
                self._clean_frames = 0
            else:
                if not self._clean_frames:
                    self._clean_since = received_at_s
                self._clean_frames += 1
                if self._clean_frames >= 3 and received_at_s - self._clean_since >= 0.5:
                    self.active = False
                    self._bad_frames = 0
        else:
            distorted = reference_drop >= full_scale * 0.10 or (
                len(alternating) > 0 and np.count_nonzero(reversal_size >= full_scale * 0.02) >= reversal_limit
            )
            self._bad_frames = self._bad_frames + 1 if distorted else 0
            if self._bad_frames >= 3:
                self.active = True
                self._clean_frames = 0
        return self.active
