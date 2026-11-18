"""Coordinate a white-light capture with the device's integration controller."""
from __future__ import annotations

from threading import Lock
from time import perf_counter

import numpy as np

from backend.core.integration_control import IntegrationControl
from backend.core.state_manager import StateManager
from backend.models.config import (
    SATURATION_CAPTURE_INTEGRATION_US,
    SATURATION_MIN_SPAN_FRACTION,
    SaturationPlotReference,
)
from backend.models.frames import BinaryFramePacket
from backend.models.status import CommandResult, ConnectionState


MAX_ACTIVE_SPREAD_FRACTION = 0.05
ACTIVE_PIXEL_TRIM_FRACTION = 0.05


class SaturationCapture:
    """Keep full-rate capture separate from the throttled display buffer."""

    def __init__(self, state: StateManager, integration: IntegrationControl) -> None:
        self._state = state
        self._integration = integration
        self._lock = Lock()
        self.phase = "idle"
        self.message = ""
        self.reference: SaturationPlotReference | None = None
        self.preview_counts: np.ndarray | None = None
        self.preview_summary = ""
        self.frames_collected = 0

    @property
    def active(self) -> bool:
        return self.phase not in ("idle", "done")

    @property
    def active_pixels(self) -> range:
        _, start, count = self._geometry
        return range(start, start + count)

    def start(self, frame_count: int) -> CommandResult:
        with self._lock:
            snapshot = self._state.snapshot(include_spectrum=False)
            device = snapshot.device
            if self.active or snapshot.recording.active or snapshot.recording.exporting:
                return CommandResult(ok=False, message="Finish the active capture, recording, or export first.")
            if frame_count < 1:
                return CommandResult(ok=False, message="Enter a positive number of saturation frames.")
            if (
                device.connection_state != ConnectionState.connected
                or device.integration_state != "Applied"
                or device.integration_us is None
                or device.timing_profile_id is None
            ):
                return CommandResult(ok=False, message="Connect and wait for confirmed exposure and timing metadata.")
            if not 0 <= device.effective_start_index < device.effective_start_index + device.effective_sample_count <= device.sample_count:
                return CommandResult(ok=False, message="The device reported invalid pixel geometry.")

            self._previous_us = device.integration_us
            self._profile = device.timing_profile_id
            self._geometry = (device.sample_count, device.effective_start_index, device.effective_sample_count)
            self._bits = self._state.get_user_config().device.adc_resolution_bits
            self._adc_max = (1 << self._bits) - 1
            config = self._state.get_calibration_config()
            self._covered_baseline = None
            if len(config.bias_counts) == device.sample_count and config.bias_timing_profile_id == self._profile:
                bias = np.asarray(config.bias_counts)
                if np.all(np.isfinite(bias)):
                    self._covered_baseline = bias
            self._frame_count = frame_count
            self.frames_collected = 0
            self._sum = np.zeros(device.sample_count, dtype=float)
            self.reference = None
            self.preview_counts = None
            self.preview_summary = ""
            if self._covered_baseline is None:
                self.phase = "cover_ready"
                self.message = "Block light at the SMA port and select Confirm Covered to measure the dark level."
                return CommandResult(ok=True, message=self.message)
            return self._request_capture_exposure()

    def _request_capture_exposure(self) -> CommandResult:
        result = self._integration.request(SATURATION_CAPTURE_INTEGRATION_US)
        if result.ok:
            self.phase = "setting"
            self.message = "Waiting for the device to confirm 1 second integration."
        return result

    def begin(self) -> None:
        with self._lock:
            if self.phase not in ("cover_ready", "ready"):
                return
            self._last_frame_id = self._state.snapshot(include_spectrum=False).device.frame_counter
            self._started_at = perf_counter()
            self._discard_first = True
            if self.phase == "cover_ready":
                self.phase = "covering"
                self.message = "Keep the SMA port covered while the app measures the dark level."
                self._deadline = self._started_at + max(5.0, 2 * self._previous_us / 1_000_000 + 2.0)
            else:
                self.phase = "verifying"
                self.message = "Hold the light steady. Waiting for a full exposure to check the active pixels."
                self._deadline = self._started_at + 5.0

    def receive_frame(self, frame: BinaryFramePacket, received_at_s: float) -> None:
        preview_phases = ("cover_ready", "covering", "ready", "verifying", "capturing")
        if self.phase not in preview_phases:
            return
        with self._lock:
            covered = self.phase in ("cover_ready", "covering")
            preview_only = self.phase in ("cover_ready", "ready")
            exposure_us = self._previous_us if covered else SATURATION_CAPTURE_INTEGRATION_US
            if (
                self.phase not in preview_phases
                or self.frames_collected >= self._frame_count
                or frame.integration_us != exposure_us
                or len(frame.adc_counts) != frame.sample_count
            ):
                return
            if not preview_only and (
                received_at_s < self._started_at
                or not 0 < ((frame.frame_counter - self._last_frame_id) & 0xFFFFFFFF) < 0x80000000
            ):
                return
            geometry = (frame.sample_count, frame.effective_start, frame.effective_count)
            if frame.timing_profile_id != self._profile or geometry != self._geometry:
                self.message = "Timing profile or pixel geometry changed during saturation capture."
                self.phase = "done" if covered else "restore_pending"
                return
            if preview_only:
                self.preview_counts = frame.adc_counts.copy()
                return
            self._last_frame_id = frame.frame_counter
            if self._discard_first:
                self._discard_first = False
                return
            if received_at_s < self._started_at + exposure_us / 1_000_000:
                return
            if covered:
                self._covered_baseline = frame.adc_counts.copy()
                self.preview_counts = None
                self.phase = "covered"
                self.message = "Dark level measured. Setting 1 second integration."
                return
            self._deadline = perf_counter() + 5.0
            self.preview_counts = frame.adc_counts.copy()
            plateau = self._trimmed_active_counts(self.preview_counts)
            minimum, maximum = int(plateau[0]), int(plateau[-1])
            spread = maximum - minimum
            allowed_spread = int(self._adc_max * MAX_ACTIVE_SPREAD_FRACTION)
            self.preview_summary = (
                f"Trimmed active pixels {minimum:,}–{maximum:,} ADC counts. "
                f"Spread {spread:,} counts, up to {allowed_spread:,} allowed."
            )
            if not self._has_light_span(plateau):
                self._verify_again("Increase or reposition the white light until the active pixels are brighter than the covered reading.")
                return
            if spread > allowed_spread:
                self._verify_again("The active pixels are uneven. Adjust the white light until the waveform is flat.")
                return
            if self.phase == "verifying":
                self.phase = "capturing"
                self.message = f"Flat waveform verified. Hold the light steady for the next {self._frame_count} frames."
                return
            self._sum += frame.adc_counts
            self.frames_collected += 1
            self.message = "Flat waveform verified. Hold the light steady while the app captures frames."

    def cancel(self) -> None:
        with self._lock:
            if self.phase in ("cover_ready", "covering", "covered"):
                self.message = "Saturation calibration cancelled."
                self.phase = "done"
            elif self.phase in ("setting", "ready", "verifying", "capturing"):
                self.message = "Saturation calibration cancelled."
                self.phase = "restore_pending"

    def poll(self) -> None:
        with self._lock:
            if not self.active:
                return
            device = self._state.snapshot(include_spectrum=False).device
            if device.connection_state != ConnectionState.connected:
                covered = self.phase in ("cover_ready", "covering", "covered")
                self.phase = "done"
                self.message = "Device disconnected." if covered else "Device disconnected. The previous exposure could not be restored."
                return
            if self.phase == "covering" and perf_counter() >= self._deadline:
                self.phase = "done"
                self.message = "Timed out waiting for a covered exposure."
                return
            if self.phase == "covered":
                result = self._request_capture_exposure()
                if not result.ok:
                    self._finish_restore(result.message)
                return
            if self.phase == "restoring":
                if device.integration_state in ("Error", "Timeout", "Fault"):
                    self._finish_restore(f"Could not restore the previous exposure. {device.integration_message}")
                elif device.integration_state == "Applied" and device.integration_us == self._previous_us:
                    self._finish_restore(f"Restored {self._previous_us:,} µs integration.")
                return
            if self.phase in ("setting", "ready", "verifying", "capturing") and device.integration_state in ("Error", "Timeout", "Fault"):
                self.phase = "restore_pending"
                self.message = device.integration_message
            elif self.phase == "setting" and device.integration_state == "Applied" and device.integration_us == SATURATION_CAPTURE_INTEGRATION_US:
                self.phase = "ready"
                self.message = (
                    "Shine a steady white light, such as a phone flashlight, into the housing through the SMA port. "
                    "Select Confirm White Light when it is in place."
                )
            elif self.phase in ("verifying", "capturing"):
                if self.frames_collected == self._frame_count:
                    self._complete_capture()
                    self.phase = "restore_pending"
                elif perf_counter() >= self._deadline:
                    self.message = "Timed out waiting for complete 1 second exposures."
                    self.phase = "restore_pending"

            if self.phase == "restore_pending" and device.integration_state != "Pending":
                if self._previous_us == SATURATION_CAPTURE_INTEGRATION_US and device.integration_state == "Applied":
                    self.phase = "done"
                    return
                result = self._integration.request(self._previous_us)
                if result.ok:
                    self.phase = "restoring"
                else:
                    self._finish_restore(f"Could not restore the previous exposure. {result.message}")

    def _verify_again(self, message: str) -> None:
        if self.frames_collected:
            self.frames_collected = 0
            self._sum.fill(0)
            message += " The frame count restarted."
        self.phase = "verifying"
        self.message = message

    def _trimmed_active_counts(self, counts: np.ndarray) -> np.ndarray:
        _, start, count = self._geometry
        ordered = np.sort(counts[start:start + count])
        trim = int(count * ACTIVE_PIXEL_TRIM_FRACTION)
        return ordered[trim:count - trim]

    def _has_light_span(self, plateau: np.ndarray) -> bool:
        _, start, count = self._geometry
        dark_level = np.median(self._covered_baseline[start:start + count])
        return bool(dark_level - plateau[-1] >= self._adc_max * SATURATION_MIN_SPAN_FRACTION)

    def _complete_capture(self) -> None:
        _, start, active = self._geometry
        mean = self._sum / self._frame_count
        plateau = self._trimmed_active_counts(mean)
        if not self._has_light_span(plateau) or plateau[-1] - plateau[0] > int(self._adc_max * MAX_ACTIVE_SPREAD_FRACTION):
            self.message = "The averaged waveform has insufficient white-light coverage or flatness. Repeat with steadier white light."
            return
        self.reference = SaturationPlotReference(
            raw_counts=mean.tolist(),
            dark_baseline=self._covered_baseline.tolist(),
            plateau_adc=float(plateau.mean()),
            timing_profile_id=self._profile,
            effective_start_index=start,
            effective_sample_count=active,
            adc_resolution_bits=self._bits,
            frame_count=self._frame_count,
        )
        self.message = f"Averaged {self._frame_count} frames."

    def _finish_restore(self, message: str) -> None:
        self.phase = "done"
        self.message = f"{self.message} {message}"
