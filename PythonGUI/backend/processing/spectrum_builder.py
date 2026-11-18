from __future__ import annotations

from contextlib import nullcontext
from typing import Sequence

import numpy as np

from backend.core.performance_monitor import PerformanceMonitor
from backend.models.config import DeviceConfig, SATURATION_WARNING_MARGIN, SaturationPlotReference, SaturationReference
from backend.models.frames import BinaryFramePacket, FramePacket, SpectrumFrame
from backend.processing.calibration_manager import CalibrationManager
from backend.processing.adc_converter import counts_to_volts
from backend.processing.dark_subtraction import apply_dark_subtraction, estimate_dark_level
from backend.processing.intensity_correction import apply_intensity_correction
from backend.processing.wavelength_map import indices_to_wavelengths

# DOC-UUID: 552FD33D-F11F-41B7-B520-81E940994448
FRAME_DARK_START_INDEX = 16
FRAME_DARK_END_INDEX = 28
LIVE_DISPLAY_CLIP_MIN = 0.0
NORMALIZED_SIGNAL_MAX = 1.0
MIN_NORMALIZATION_DENOMINATOR = 1e-9
SATURATION_FLOOR_PERCENTILE = 5.0
SPECTROGRAM_ROW_TARGET_WIDTH = 256
SPECTROGRAM_ROW_PEAK_BLEND = 0.15


class SpectrumBuilder:
    """Purpose: build app-level spectrum frames and export columns. Rationale: frame conversion should stay separate from transport parsing."""
    def __init__(
        self,
        calibration_manager: CalibrationManager,
        device_config: DeviceConfig,
        *,
        performance_monitor: PerformanceMonitor | None = None,
    ) -> None:
        """Purpose: store processing dependencies and caches. Rationale: repeated export calculations should reuse device settings and wavelength maps."""
        self._calibration_manager = calibration_manager
        self._device_config = device_config
        self._cached_wavelengths: dict[tuple[int, tuple[float, ...]], np.ndarray] = {}
        self._performance_monitor = performance_monitor

    def update_device_config(self, device_config: DeviceConfig) -> None:
        """Purpose: store updated device settings. Rationale: export calculations should follow the latest ADC and geometry configuration."""
        self._device_config = device_config

    def build_from_frame(self, frame: FramePacket | BinaryFramePacket) -> SpectrumFrame:
        """Purpose: wrap one parsed device frame as a spectrum frame. Rationale: the rest of the app should work with one stable frame type."""
        monitor = self._performance_monitor
        with (
            monitor.measure("backend.build_from_frame")
            if monitor is not None
            else nullcontext()
        ):
            plot_reference, warning_reference = self._saturation_references(
                frame.timing_profile_id, frame.sample_count, frame.effective_start, frame.effective_count, frame.adc_counts,
            )
            (
                processed_counts,
                display_counts,
                _wavelengths,
                _volts,
                dark_reference,
                saturation_reference_counts,
            ) = self._build_processed_columns(
                frame.adc_counts, integration_us=frame.integration_us, timing_profile_id=frame.timing_profile_id,
                saturation_reference=plot_reference,
            )
            raw_adc_counts = (
                frame.adc_counts.tolist()
                if hasattr(frame.adc_counts, "tolist")
                else list(frame.adc_counts)
            )
            spectrogram_values = self._normalize_spectrogram_signal(
                processed_counts,
                saturation_reference_counts=saturation_reference_counts,
            )
            spectrogram_row = self._build_spectrogram_row(
                spectrogram_values,
                expected_sample_count=frame.sample_count,
                effective_start_index=frame.effective_start,
                effective_sample_count=frame.effective_count,
            )
            reference_status, reference_shifted = self._assess_reference(frame.adc_counts, frame.timing_profile_id)
            return SpectrumFrame(
                frame_id=frame.frame_counter,
                timestamp=frame.timestamp,
                source="usb_binary_frame",
                expected_sample_count=frame.sample_count,
                effective_start_index=frame.effective_start,
                effective_sample_count=frame.effective_count,
                frame_flags=frame.flags,
                integration_us=frame.integration_us,
                timing_profile_id=frame.timing_profile_id,
                reference_status=reference_status,
                reference_shifted=reference_shifted,
                near_saturation=self._near_saturation(frame.adc_counts, warning_reference),
                dark_calibration_applied=self._dark_matches(frame.integration_us, frame.timing_profile_id),
                adc_counts=[int(value) for value in raw_adc_counts],
                live_display_counts=display_counts.tolist(),
                spectrogram_row=spectrogram_row,
                dark_reference_count=dark_reference,
                notes=(
                    "Captured from TIM4-synchronized USB CDC binary frames. Frame start is "
                    "referenced to ICG rising; the 32/3648/14 pixel map remains nominal. "
                    "Sensor-pin phase and exact dummy origin require external verification."
                ),
            )

    def rebuild_live_frame(self, frame: SpectrumFrame) -> SpectrumFrame:
        """Purpose: rebuild one stored frame using the current calibration settings. Rationale: UI calibration toggles should update the latest display immediately."""
        monitor = self._performance_monitor
        with (
            monitor.measure("backend.rebuild_live_frame")
            if monitor is not None
            else nullcontext()
        ):
            plot_reference, warning_reference = self._saturation_references(
                frame.timing_profile_id, frame.expected_sample_count, frame.effective_start_index,
                frame.effective_sample_count, frame.adc_counts,
            )
            (
                processed_counts,
                display_counts,
                _wavelengths,
                _volts,
                dark_reference,
                saturation_reference_counts,
            ) = self._build_processed_columns(
                frame.adc_counts, integration_us=frame.integration_us, timing_profile_id=frame.timing_profile_id,
                saturation_reference=plot_reference,
            )
            spectrogram_values = self._normalize_spectrogram_signal(
                processed_counts,
                saturation_reference_counts=saturation_reference_counts,
            )
            updated = frame.model_copy(deep=True)
            updated.live_display_counts = display_counts.tolist()
            updated.spectrogram_row = self._build_spectrogram_row(
                spectrogram_values,
                expected_sample_count=frame.expected_sample_count,
                effective_start_index=frame.effective_start_index,
                effective_sample_count=frame.effective_sample_count,
            )
            updated.reference_status, updated.reference_shifted = self._assess_reference(
                frame.adc_counts, frame.timing_profile_id,
            )
            updated.near_saturation = self._near_saturation(frame.adc_counts, warning_reference)
            updated.dark_reference_count = dark_reference
            updated.dark_calibration_applied = self._dark_matches(frame.integration_us, frame.timing_profile_id)
            return updated

    def _build_processed_counts(
        self,
        adc_counts: Sequence[int],
    ) -> tuple[np.ndarray, np.ndarray, float]:
        """Purpose: build corrected count series and a final normalized display signal. Rationale: document-style calibration needs additive terms removed before multiplicative corrections and only then normalized."""
        (
            corrected_counts,
            normalized_counts,
            _wavelengths,
            _volts,
            frame_dark_level,
            _saturation_reference_counts,
        ) = self._build_processed_columns(adc_counts)
        return corrected_counts, normalized_counts, frame_dark_level

    def _build_live_display_counts(
        self,
        adc_counts: Sequence[int],
    ) -> tuple[np.ndarray, float]:
        """Purpose: build the live plot series from raw ADC counts. Rationale: the UI should display normalized processed data without mutating the captured raw frame."""
        _processed_counts, normalized_counts, frame_dark_level = self._build_processed_counts(adc_counts)
        return normalized_counts, frame_dark_level

    def reference_status(self, adc_counts, timing_profile_id) -> str:
        return self._assess_reference(adc_counts, timing_profile_id)[0]

    def _assess_reference(
        self, adc_counts: Sequence[int] | np.ndarray, timing_profile_id: int | None,
    ) -> tuple[str, bool]:
        raw = np.asarray(adc_counts, dtype=float)
        if raw.size < 32:
            return "Reference unavailable: incomplete leading region", False
        reference = float(np.median(raw[16:29]))
        active = float(np.median(raw[32:3680])) if raw.size > 32 else reference
        message = f"Raw reference {reference:.1f} ADC; reference-active {reference-active:.1f} ADC"
        config = self._calibration_manager.config
        if config.bias_counts and config.bias_timing_profile_id != timing_profile_id:
            return message + " | Stored bias bypassed: timing profile mismatch", False
        if config.dark_offset_counts and config.dark_timing_profile_id != timing_profile_id:
            message += " | Stored dark bypassed: timing profile mismatch"
        if len(config.bias_counts) < 29:
            return message + " | Reference unverified: capture a covered baseline", False
        baseline = float(np.median(config.bias_counts[16:29]))
        # Screening threshold, not a calibrated sensor saturation specification.
        shifted = abs(reference - baseline) > max(50.0, abs(baseline) * 0.05)
        if shifted:
            message += " | Reference shifted >5%/50 ADC: check illumination and analog levels"
        return message, shifted

    def _saturation_references(
        self, profile: int | None, count: int, start: int, active: int, adc_counts: Sequence[int],
    ) -> tuple[SaturationReference | None, SaturationReference | None]:
        if count != len(adc_counts):
            return None, None
        config = self._calibration_manager.config
        geometry = (profile, count, start, active, self._device_config.adc_resolution_bits)
        warning = config.saturation_reference
        if warning is not None and not warning.matches(*geometry):
            warning = None
        plot = config.saturation_plot_reference
        if plot is not None and plot.matches(*geometry):
            return plot, warning
        return warning, warning

    def _near_saturation(self, adc_counts: Sequence[int], reference: SaturationReference | None) -> bool:
        if reference is None or not self._calibration_manager.config.show_potential_saturation_warning:
            return False

        start = reference.effective_start_index
        active = slice(start, start + reference.effective_sample_count)
        limit = np.asarray(reference.raw_counts[active])
        dark = np.asarray(reference.dark_baseline[active])
        threshold = limit + (dark - limit) * SATURATION_WARNING_MARGIN
        near = np.asarray(adc_counts[active]) <= threshold
        return bool(np.any(near[:-2] & near[1:-1] & near[2:]))

    def _dark_matches(self, integration_us: int | None, timing_profile_id: int | None = None) -> bool:
        config = self._calibration_manager.config
        return bool(config.apply_dark_subtraction and config.dark_offset_counts and
                    integration_us is not None and config.dark_integration_us == integration_us and
                    config.dark_timing_profile_id == timing_profile_id)

    def _build_processed_columns(
        self,
        adc_counts: Sequence[int],
        *, integration_us: int | None = None, timing_profile_id: int | None = None,
        saturation_reference: SaturationReference | None = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, np.ndarray]:
        """Purpose: run the calibration pipeline through corrected counts, wavelength assignment, and final normalization. Rationale: both the live plot and CSV export should use the same ordered processing steps."""
        monitor = self._performance_monitor
        with (
            monitor.measure("backend.build_processed_columns")
            if monitor is not None
            else nullcontext()
        ):
            raw_counts = np.asarray(adc_counts, dtype=float)
            full_scale_count = float((1 << self._device_config.adc_resolution_bits) - 1)
            calibration_config = self._calibration_manager.config
            bias_corrected_raw = raw_counts.copy()
            if calibration_config.bias_counts and calibration_config.bias_timing_profile_id == timing_profile_id:
                bias_corrected_raw = apply_dark_subtraction(
                    bias_corrected_raw,
                    calibration_config.bias_counts,
                )
            saturated_bias_corrected_raw = np.zeros_like(raw_counts, dtype=float)
            if calibration_config.bias_counts and calibration_config.bias_timing_profile_id == timing_profile_id:
                saturated_bias_corrected_raw = apply_dark_subtraction(
                    saturated_bias_corrected_raw,
                    calibration_config.bias_counts,
                )

            frame_dark_level = 0.0
            if calibration_config.apply_dark_subtraction:
                # The document defines beta_f from the dark pixels after removing the
                # stored master bias B_p, so the frame-wise offset here is measured
                # on the bias-corrected raw frame. Because this CCD is inverted in
                # our readout, the light-tracking signal is then the distance from
                # that dark baseline down to the current sample.
                frame_dark_level = estimate_dark_level(
                    bias_corrected_raw,
                    start_index=FRAME_DARK_START_INDEX,
                    end_index=FRAME_DARK_END_INDEX,
                )
            light_counts = self._light_counts_from_bias_corrected_raw(
                bias_corrected_raw,
                frame_dark_level=frame_dark_level,
                full_scale_count=full_scale_count,
                apply_dark_subtraction_enabled=calibration_config.apply_dark_subtraction,
                dark_offset_counts=calibration_config.dark_offset_counts if self._dark_matches(integration_us, timing_profile_id) else [],
            )
            saturation_light_counts = self._light_counts_from_bias_corrected_raw(
                saturated_bias_corrected_raw,
                frame_dark_level=frame_dark_level,
                full_scale_count=full_scale_count,
                apply_dark_subtraction_enabled=calibration_config.apply_dark_subtraction,
                dark_offset_counts=calibration_config.dark_offset_counts if self._dark_matches(integration_us, timing_profile_id) else [],
            )

            wavelengths = self._wavelengths_for_sample_count(len(raw_counts))
            corrected_counts, saturation_reference_counts = self._apply_multiplicative_corrections(
                light_counts,
                saturation_light_counts,
                wavelengths=wavelengths,
            )

            corrected_counts = np.maximum(corrected_counts, LIVE_DISPLAY_CLIP_MIN)
            volts = counts_to_volts(
                light_counts,
                reference_volts=self._device_config.adc_reference_volts,
                resolution_bits=self._device_config.adc_resolution_bits,
            )
            normalized_counts = self._normalize_processed_signal(
                corrected_counts,
                saturation_reference_counts=saturation_reference_counts,
            )
            if (
                saturation_reference is not None
                and calibration_config.use_calibrated_saturation_scale
                and calibration_config.display_normalization_mode == "absolute_saturation"
            ):
                start = saturation_reference.effective_start_index
                active = slice(start, start + saturation_reference.effective_sample_count)
                # The inverted ADC signal increases in brightness as the raw code falls.
                if isinstance(saturation_reference, SaturationPlotReference):
                    saturation_floor = saturation_reference.plateau_adc
                else:
                    saturation_floor = np.percentile(
                        saturation_reference.raw_counts[active], SATURATION_FLOOR_PERCENTILE,
                    )
                dark_level = np.median(saturation_reference.dark_baseline[active])
                span = dark_level - saturation_floor
                if span > MIN_NORMALIZATION_DENOMINATOR:
                    normalized_counts[active] = np.clip(
                        (dark_level - raw_counts[active]) / span,
                        LIVE_DISPLAY_CLIP_MIN, NORMALIZED_SIGNAL_MAX,
                    )
            return corrected_counts, normalized_counts, wavelengths, volts, frame_dark_level, saturation_reference_counts

    def _build_spectrogram_row(
        self,
        normalized_spectrogram_values: Sequence[float] | np.ndarray,
        *,
        expected_sample_count: int,
        effective_start_index: int,
        effective_sample_count: int,
    ) -> list[float]:
        """Purpose: prepare one compact spectrogram row alongside live-frame processing. Rationale: the spectrogram should use a stable value scale even when the line plot is using per-frame auto-ranging."""
        monitor = self._performance_monitor
        with (
            monitor.measure("backend.build_spectrogram_row")
            if monitor is not None
            else nullcontext()
        ):
            values = np.asarray(normalized_spectrogram_values, dtype=float)
            total_samples = len(values)
            if total_samples <= 0:
                return []

            if total_samples >= expected_sample_count:
                start = max(int(effective_start_index), 0)
                end = min(start + max(int(effective_sample_count), 0), total_samples)
                active_values = values[start:end]
            else:
                active_values = values

            if active_values.size <= 0:
                return []
            return self._compress_spectrogram_row(active_values, target_width=SPECTROGRAM_ROW_TARGET_WIDTH)

    @staticmethod
    def _compress_spectrogram_row(values: np.ndarray, *, target_width: int) -> list[float]:
        """Purpose: reduce one normalized frame row to a fixed spectrogram width. Rationale: the heatmap should grade by overall segment level instead of letting one hot sample dominate the whole bucket."""
        if values.size <= 0:
            return []

        safe_target_width = max(int(target_width), 1)
        clipped_values = np.clip(np.asarray(values, dtype=float), LIVE_DISPLAY_CLIP_MIN, NORMALIZED_SIGNAL_MAX)
        source_width = int(clipped_values.size)

        if source_width <= safe_target_width:
            padded = clipped_values.tolist()
            if len(padded) < safe_target_width:
                padded.extend([padded[-1]] * (safe_target_width - len(padded)))
            return padded

        boundaries = np.linspace(0, source_width, safe_target_width + 1, dtype=int)
        compressed: list[float] = []
        for column_index in range(safe_target_width):
            start = int(boundaries[column_index])
            end = max(int(boundaries[column_index + 1]), start + 1)
            segment = clipped_values[start:end]
            segment_peak = float(np.max(segment))
            segment_rms = float(np.sqrt(np.mean(segment * segment)))
            blended_value = (
                (segment_rms * (1.0 - SPECTROGRAM_ROW_PEAK_BLEND))
                + (segment_peak * SPECTROGRAM_ROW_PEAK_BLEND)
            )
            compressed.append(min(max(blended_value, LIVE_DISPLAY_CLIP_MIN), NORMALIZED_SIGNAL_MAX))
        return compressed

    def _light_counts_from_bias_corrected_raw(
        self,
        bias_corrected_raw: Sequence[float],
        *,
        frame_dark_level: float,
        full_scale_count: float,
        apply_dark_subtraction_enabled: bool,
        dark_offset_counts: Sequence[float],
    ) -> np.ndarray:
        """Purpose: convert bias-corrected raw CCD codes into light-tracking counts. Rationale: the same additive logic should be reused for the live frame and the absolute-saturation reference frame."""
        raw = np.asarray(bias_corrected_raw, dtype=float)
        if apply_dark_subtraction_enabled:
            dark_corrected_raw = apply_dark_subtraction(
                raw,
                dark_offset_counts,
            )
            return np.maximum(
                frame_dark_level - dark_corrected_raw,
                LIVE_DISPLAY_CLIP_MIN,
            )
        return np.maximum(
            full_scale_count - raw,
            LIVE_DISPLAY_CLIP_MIN,
        )

    def _apply_multiplicative_corrections(
        self,
        light_counts: Sequence[float],
        saturation_light_counts: Sequence[float],
        *,
        wavelengths: Sequence[float],
    ) -> tuple[np.ndarray, np.ndarray]:
        """Purpose: apply flat-field and QE-style multiplicative corrections to both the live signal and its saturation reference. Rationale: absolute saturation mode only works if the denominator sees the same multiplicative processing as the numerator."""
        calibration_config = self._calibration_manager.config
        corrected_counts = np.asarray(light_counts, dtype=float)
        saturation_reference_counts = np.asarray(saturation_light_counts, dtype=float)

        if calibration_config.apply_intensity_correction:
            corrected_counts = apply_intensity_correction(
                corrected_counts,
                calibration_config.intensity_correction,
            )
            saturation_reference_counts = apply_intensity_correction(
                saturation_reference_counts,
                calibration_config.intensity_correction,
            )

        if calibration_config.apply_quantum_efficiency_correction:
            qe_curve = self._calibration_manager.build_quantum_efficiency_curve(wavelengths)
            corrected_counts = corrected_counts / qe_curve
            saturation_reference_counts = saturation_reference_counts / qe_curve

        corrected_counts = np.maximum(corrected_counts, LIVE_DISPLAY_CLIP_MIN)
        saturation_reference_counts = np.maximum(saturation_reference_counts, MIN_NORMALIZATION_DENOMINATOR)
        return corrected_counts, saturation_reference_counts

    def _wavelengths_for_sample_count(self, sample_count: int) -> np.ndarray:
        """Purpose: reuse wavelength arrays for a given sample count and coefficient set. Rationale: live export calculations should not keep rebuilding the same polynomial map."""
        calibration_config = self._calibration_manager.config
        coefficient_key = tuple(calibration_config.effective_wavelength_coefficients)
        cache_key = (sample_count, coefficient_key)
        wavelengths = self._cached_wavelengths.get(cache_key)
        if wavelengths is None:
            wavelengths = indices_to_wavelengths(
                range(sample_count),
                coefficient_key,
            )
            self._cached_wavelengths = {cache_key: wavelengths}
        return wavelengths

    def _normalize_processed_signal(
        self,
        processed_counts: Sequence[float],
        *,
        saturation_reference_counts: Sequence[float],
    ) -> np.ndarray:
        """Purpose: normalize the fully corrected signal into the 0-to-1 display range. Rationale: the UI needs both auto-ranging and absolute saturation-referenced views of the same processed signal."""
        processed = np.asarray(processed_counts, dtype=float)
        normalization_mode = self._calibration_manager.config.display_normalization_mode
        if normalization_mode == "absolute_saturation":
            denominator = np.maximum(
                np.asarray(saturation_reference_counts, dtype=float),
                MIN_NORMALIZATION_DENOMINATOR,
            )
        else:
            denominator = max(float(np.max(processed, initial=0.0)), MIN_NORMALIZATION_DENOMINATOR)
        normalized = processed / denominator
        return np.clip(normalized, LIVE_DISPLAY_CLIP_MIN, NORMALIZED_SIGNAL_MAX)

    def _normalize_spectrogram_signal(
        self,
        processed_counts: Sequence[float],
        *,
        saturation_reference_counts: Sequence[float],
    ) -> np.ndarray:
        """Purpose: build a stable spectrogram value scale from processed counts. Rationale: rolling heatmap colors should stay comparable from frame to frame even when the line plot uses auto-peak normalization."""
        processed = np.asarray(processed_counts, dtype=float)
        denominator = np.maximum(
            np.asarray(saturation_reference_counts, dtype=float),
            MIN_NORMALIZATION_DENOMINATOR,
        )
        normalized = processed / denominator
        return np.clip(normalized, LIVE_DISPLAY_CLIP_MIN, NORMALIZED_SIGNAL_MAX)
