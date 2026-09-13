from __future__ import annotations

import csv
import json
import queue
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from backend.models.config import CalibrationConfig, DeviceConfig
from backend.models.frames import BinaryFramePacket, FramePacket
from backend.processing.spectrum_builder import (
    FRAME_DARK_END_INDEX,
    FRAME_DARK_START_INDEX,
    LIVE_DISPLAY_CLIP_MIN,
    MIN_NORMALIZATION_DENOMINATOR,
    NORMALIZED_SIGNAL_MAX,
)
from backend.processing.wavelength_map import indices_to_wavelengths

try:
    import h5py
except ImportError:  # pragma: no cover - exercised only on machines missing the dependency.
    h5py = None


FORMAT_VERSION = "dense-hdf5-v1"
DEFAULT_CHUNK_FRAMES = 128
DEFAULT_QUEUE_CHUNKS = 4
CSV_FLOAT_FORMAT = ".8g"
CSV_COLUMNS = [
    "frame_id",
    "timestamp_ns",
    "sample_index",
    "wavelength_nm",
    "raw_adc_count",
    "processed_adc_count",
    "frame_dark_reference_count",
    "automatic_dark_bias_applied",
    "correction_factor_applied",
    "volts",
    "processed_intensity",
]


@dataclass(frozen=True, slots=True)
class StaticRecordingData:
    sample_indices: np.ndarray
    wavelengths_nm: np.ndarray
    qe_correction: np.ndarray
    system_response_correction: np.ndarray
    correction_factor_applied: np.ndarray


@dataclass(frozen=True, slots=True)
class DenseFrameRecord:
    frame_id: int
    timestamp_ns: int
    raw_adc_count: np.ndarray
    processed_adc_count: np.ndarray
    volts: np.ndarray
    processed_intensity: np.ndarray
    frame_dark_reference_count: np.ndarray
    automatic_dark_bias_applied: np.ndarray


def require_h5py() -> Any:
    if h5py is None or not hasattr(h5py, "File"):
        raise RuntimeError("h5py is required for dense binary recording. Install the PythonGUI package dependencies.")
    return h5py


def _config_to_json(config: Any) -> str:
    if hasattr(config, "model_dump"):
        return json.dumps(config.model_dump(mode="json"), sort_keys=True)
    return json.dumps(vars(config), sort_keys=True)


def _coerce_vector(values: Sequence[float], pixel_count: int, *, fill_value: float) -> np.ndarray:
    vector = np.full(pixel_count, fill_value, dtype=np.float64)
    if not values:
        return vector
    source = np.asarray(values, dtype=np.float64)
    limit = min(pixel_count, source.size)
    vector[:limit] = source[:limit]
    return vector


def _build_qe_correction(config: CalibrationConfig, wavelengths_nm: np.ndarray) -> np.ndarray:
    points = config.quantum_efficiency_points
    if not points or not config.apply_quantum_efficiency_correction:
        return np.ones(wavelengths_nm.size, dtype=np.float64)

    sorted_points = sorted(points, key=lambda item: item.wavelength_nm)
    source_wavelengths = np.asarray([point.wavelength_nm for point in sorted_points], dtype=np.float64)
    source_values = np.asarray([point.relative_value for point in sorted_points], dtype=np.float64)
    if source_wavelengths.size == 0:
        return np.ones(wavelengths_nm.size, dtype=np.float64)

    interpolated = np.interp(
        wavelengths_nm,
        source_wavelengths,
        source_values,
        left=float(source_values[0]),
        right=float(source_values[-1]),
    )
    reference_wavelength = config.quantum_efficiency_normalization_wavelength_nm
    if reference_wavelength is None:
        normalization_value = float(np.max(source_values))
    else:
        normalization_value = float(
            np.interp(
                float(reference_wavelength),
                source_wavelengths,
                source_values,
                left=float(source_values[0]),
                right=float(source_values[-1]),
            )
        )
    qe_curve = np.clip(interpolated / max(normalization_value, MIN_NORMALIZATION_DENOMINATOR), MIN_NORMALIZATION_DENOMINATOR, None)
    return 1.0 / qe_curve


class DenseFrameProcessor:
    """Purpose: compute all dense recording arrays with cached calibration vectors. Rationale: the HDF5 path must not depend on UI frame objects."""

    def __init__(self, device_config: DeviceConfig, calibration_config: CalibrationConfig) -> None:
        self.device_config = device_config.model_copy(deep=True)
        self.calibration_config = calibration_config.model_copy(deep=True)
        self.pixel_count = int(self.device_config.sample_count)
        self.sample_indices = np.arange(self.pixel_count, dtype=np.int32)
        self.full_scale_count = float((1 << int(self.device_config.adc_resolution_bits)) - 1)
        self.bias_vector = _coerce_vector(
            self.calibration_config.bias_counts,
            self.pixel_count,
            fill_value=0.0,
        )
        self.dark_offset_vector = (
            _coerce_vector(
                self.calibration_config.dark_offset_counts,
                self.pixel_count,
                fill_value=0.0,
            )
            if self.calibration_config.apply_dark_subtraction
            else np.zeros(self.pixel_count, dtype=np.float64)
        )
        system_response = (
            _coerce_vector(
                self.calibration_config.intensity_correction,
                self.pixel_count,
                fill_value=1.0,
            )
            if self.calibration_config.apply_intensity_correction
            else np.ones(self.pixel_count, dtype=np.float64)
        )
        wavelengths = indices_to_wavelengths(
            self.sample_indices,
            self.calibration_config.wavelength_coefficients,
        ).astype(np.float64, copy=False)
        qe_correction = _build_qe_correction(self.calibration_config, wavelengths)
        correction_factor = system_response * qe_correction
        self.static_data = StaticRecordingData(
            sample_indices=self.sample_indices.copy(),
            wavelengths_nm=wavelengths.astype(np.float32),
            qe_correction=qe_correction.astype(np.float32),
            system_response_correction=system_response.astype(np.float32),
            correction_factor_applied=correction_factor.astype(np.float32),
        )
        self._correction_factor = correction_factor
        self._applied_bias_vector = self.bias_vector + self.dark_offset_vector

    def metadata_attributes(self) -> dict[str, Any]:
        return {
            "format_version": FORMAT_VERSION,
            "sample_count": self.pixel_count,
            "effective_start_index": int(self.device_config.effective_start_index),
            "effective_sample_count": int(self.device_config.effective_sample_count),
            "trailing_dummy_count": int(self.device_config.trailing_dummy_count),
            "adc_resolution_bits": int(self.device_config.adc_resolution_bits),
            "adc_reference_volts": float(self.device_config.adc_reference_volts),
            "device_config_json": _config_to_json(self.device_config),
            "calibration_config_json": _config_to_json(self.calibration_config),
            "apply_dark_subtraction": bool(self.calibration_config.apply_dark_subtraction),
            "apply_intensity_correction": bool(self.calibration_config.apply_intensity_correction),
            "apply_quantum_efficiency_correction": bool(self.calibration_config.apply_quantum_efficiency_correction),
            "display_normalization_mode": self.calibration_config.display_normalization_mode,
            "frame_dark_start_index": FRAME_DARK_START_INDEX,
            "frame_dark_end_index": FRAME_DARK_END_INDEX,
            "precision_policy": "raw uint16 exact; derived arrays stored as float32; CSV derived fields formatted with .8g",
            "correction_factor_storage": "static /correction/correction_factor_applied [P]",
        }

    def build_record(self, frame: FramePacket | BinaryFramePacket) -> DenseFrameRecord:
        if int(frame.sample_count) != self.pixel_count:
            raise ValueError(f"Recording expected {self.pixel_count} samples, got {frame.sample_count}.")

        raw_u16 = np.asarray(frame.adc_counts, dtype=np.uint16)
        raw_counts = raw_u16.astype(np.float64, copy=False)
        bias_corrected_raw = raw_counts - self.bias_vector

        frame_dark_reference = 0.0
        if self.calibration_config.apply_dark_subtraction:
            start = max(0, FRAME_DARK_START_INDEX)
            stop = min(self.pixel_count, FRAME_DARK_END_INDEX + 1)
            if stop > start:
                frame_dark_reference = float(np.median(bias_corrected_raw[start:stop]))

        # The CCD readout is inverted, so larger light means a lower ADC code.
        # With dark subtraction enabled the light estimate is beta_f - (R_p - B_p - D_p).
        # Without it, the same polarity becomes full_scale - (R_p - B_p).
        if self.calibration_config.apply_dark_subtraction:
            dark_corrected_raw = bias_corrected_raw - self.dark_offset_vector
            light_counts = np.maximum(frame_dark_reference - dark_corrected_raw, LIVE_DISPLAY_CLIP_MIN)
            saturated_bias_corrected_raw = -self.bias_vector
            saturated_dark_corrected_raw = saturated_bias_corrected_raw - self.dark_offset_vector
            saturation_light_counts = np.maximum(
                frame_dark_reference - saturated_dark_corrected_raw,
                MIN_NORMALIZATION_DENOMINATOR,
            )
        else:
            light_counts = np.maximum(self.full_scale_count - bias_corrected_raw, LIVE_DISPLAY_CLIP_MIN)
            saturated_bias_corrected_raw = -self.bias_vector
            saturation_light_counts = np.maximum(
                self.full_scale_count - saturated_bias_corrected_raw,
                MIN_NORMALIZATION_DENOMINATOR,
            )

        processed_counts = np.maximum(light_counts * self._correction_factor, LIVE_DISPLAY_CLIP_MIN)
        saturation_reference = np.maximum(
            saturation_light_counts * self._correction_factor,
            MIN_NORMALIZATION_DENOMINATOR,
        )
        volts = light_counts * float(self.device_config.adc_reference_volts) / self.full_scale_count
        if self.calibration_config.display_normalization_mode == "absolute_saturation":
            intensity = processed_counts / saturation_reference
        else:
            intensity = processed_counts / max(float(np.max(processed_counts, initial=0.0)), MIN_NORMALIZATION_DENOMINATOR)
        intensity = np.clip(intensity, LIVE_DISPLAY_CLIP_MIN, NORMALIZED_SIGNAL_MAX)

        timestamp_ns = getattr(frame, "timestamp_ns", None)
        if timestamp_ns is None:
            timestamp_ns = int(frame.timestamp.timestamp() * 1_000_000_000)

        return DenseFrameRecord(
            frame_id=int(frame.frame_counter),
            timestamp_ns=int(timestamp_ns),
            raw_adc_count=raw_u16.copy(),
            processed_adc_count=processed_counts.astype(np.float32),
            volts=volts.astype(np.float32),
            processed_intensity=intensity.astype(np.float32),
            frame_dark_reference_count=np.full(self.pixel_count, frame_dark_reference, dtype=np.float32),
            automatic_dark_bias_applied=self._applied_bias_vector.astype(np.float32),
        )


class DenseBinaryRecorder:
    """Purpose: write dense frame records to appendable HDF5 datasets on a worker thread. Rationale: serial parsing should not block on disk I/O."""

    def __init__(
        self,
        path: Path,
        static_data: StaticRecordingData,
        metadata_attributes: dict[str, Any],
        *,
        chunk_frames: int = DEFAULT_CHUNK_FRAMES,
        queue_chunks: int = DEFAULT_QUEUE_CHUNKS,
    ) -> None:
        self.path = Path(path)
        self.static_data = static_data
        self.metadata_attributes = dict(metadata_attributes)
        self.chunk_frames = max(int(chunk_frames), 1)
        self._queue: queue.Queue[DenseFrameRecord | None] = queue.Queue(maxsize=self.chunk_frames * max(int(queue_chunks), 1))
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._active = False
        self._failed = False
        self._failure_message: str | None = None
        self._frame_count = 0

    def start(self) -> None:
        require_h5py()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            self._active = True
            self._failed = False
            self._failure_message = None
            self._frame_count = 0
        self._thread = threading.Thread(target=self._run, name="dense-binary-writer", daemon=True)
        self._thread.start()

    def append(self, record: DenseFrameRecord) -> bool:
        with self._lock:
            if not self._active or self._failed:
                return False
        try:
            self._queue.put_nowait(record)
        except queue.Full:
            self._mark_failed("Dense binary recording queue filled. Recording failed rather than dropping a frame.")
            return False
        return True

    def stop(self) -> None:
        with self._lock:
            was_active = self._active
        if was_active:
            self._queue.put(None)
        if self._thread is not None:
            self._thread.join()
        with self._lock:
            self._active = False

    def queue_depth(self) -> int:
        return self._queue.qsize()

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "active": self._active,
                "failed": self._failed,
                "failure_message": self._failure_message,
                "frame_count": self._frame_count,
                "queue_depth": self._queue.qsize(),
                "path": str(self.path),
            }

    def fail(self, message: str) -> None:
        self._mark_failed(message)

    def _mark_failed(self, message: str) -> None:
        with self._lock:
            self._failed = True
            self._failure_message = message

    def _run(self) -> None:
        batch: list[DenseFrameRecord] = []
        try:
            h5 = require_h5py()
            with h5.File(self.path, "w") as handle:
                for key, value in self.metadata_attributes.items():
                    handle.attrs[key] = value
                datasets = self._create_datasets(handle)
                while True:
                    record = self._queue.get()
                    if record is None:
                        if batch:
                            self._flush_records(datasets, batch)
                        break
                    batch.append(record)
                    if len(batch) >= self.chunk_frames:
                        self._flush_records(datasets, batch)
                        batch = []
        except Exception as exc:  # pragma: no cover - depends on filesystem/HDF5 failures.
            self._mark_failed(str(exc))
        finally:
            with self._lock:
                self._active = False

    def _create_datasets(self, handle: Any) -> dict[str, Any]:
        pixel_count = int(self.static_data.sample_indices.size)
        frame_group = handle.require_group("frame")
        pixel_group = handle.require_group("pixel")
        raw_group = handle.require_group("raw")
        processed_group = handle.require_group("processed")
        dark_group = handle.require_group("dark")
        correction_group = handle.require_group("correction")

        pixel_group.create_dataset("sample_index", data=self.static_data.sample_indices, dtype=np.int32)
        pixel_group.create_dataset("wavelength_nm", data=self.static_data.wavelengths_nm, dtype=np.float32)
        correction_group.create_dataset("qe_correction", data=self.static_data.qe_correction, dtype=np.float32)
        correction_group.create_dataset("system_response_correction", data=self.static_data.system_response_correction, dtype=np.float32)
        correction_group.create_dataset("correction_factor_applied", data=self.static_data.correction_factor_applied, dtype=np.float32)

        frame_chunks = (self.chunk_frames,)
        dense_chunks = (self.chunk_frames, pixel_count)
        return {
            "frame_id": frame_group.create_dataset("frame_id", shape=(0,), maxshape=(None,), chunks=frame_chunks, dtype=np.uint64),
            "timestamp_ns": frame_group.create_dataset("timestamp_ns", shape=(0,), maxshape=(None,), chunks=frame_chunks, dtype=np.int64),
            "raw_adc_count": raw_group.create_dataset("adc_count", shape=(0, pixel_count), maxshape=(None, pixel_count), chunks=dense_chunks, dtype=np.uint16),
            "processed_adc_count": processed_group.create_dataset("adc_count", shape=(0, pixel_count), maxshape=(None, pixel_count), chunks=dense_chunks, dtype=np.float32),
            "volts": processed_group.create_dataset("volts", shape=(0, pixel_count), maxshape=(None, pixel_count), chunks=dense_chunks, dtype=np.float32),
            "processed_intensity": processed_group.create_dataset("intensity", shape=(0, pixel_count), maxshape=(None, pixel_count), chunks=dense_chunks, dtype=np.float32),
            "frame_dark_reference_count": dark_group.create_dataset("frame_dark_reference_count", shape=(0, pixel_count), maxshape=(None, pixel_count), chunks=dense_chunks, dtype=np.float32),
            "automatic_dark_bias_applied": dark_group.create_dataset("automatic_dark_bias_applied", shape=(0, pixel_count), maxshape=(None, pixel_count), chunks=dense_chunks, dtype=np.float32),
        }

    def _flush_records(self, datasets: dict[str, Any], records: Sequence[DenseFrameRecord]) -> None:
        count = len(records)
        if count <= 0:
            return
        with self._lock:
            start = self._frame_count
            stop = start + count
            self._frame_count = stop

        for dataset in datasets.values():
            if dataset.ndim == 1:
                dataset.resize((stop,))
            else:
                dataset.resize((stop, dataset.shape[1]))

        datasets["frame_id"][start:stop] = np.asarray([record.frame_id for record in records], dtype=np.uint64)
        datasets["timestamp_ns"][start:stop] = np.asarray([record.timestamp_ns for record in records], dtype=np.int64)
        datasets["raw_adc_count"][start:stop, :] = np.stack([record.raw_adc_count for record in records])
        datasets["processed_adc_count"][start:stop, :] = np.stack([record.processed_adc_count for record in records])
        datasets["volts"][start:stop, :] = np.stack([record.volts for record in records])
        datasets["processed_intensity"][start:stop, :] = np.stack([record.processed_intensity for record in records])
        datasets["frame_dark_reference_count"][start:stop, :] = np.stack([record.frame_dark_reference_count for record in records])
        datasets["automatic_dark_bias_applied"][start:stop, :] = np.stack([record.automatic_dark_bias_applied for record in records])


def export_hdf5_to_csv(hdf5_path: Path, csv_path: Path | None = None, *, chunk_frames: int = DEFAULT_CHUNK_FRAMES) -> Path:
    h5 = require_h5py()
    source_path = Path(hdf5_path)
    output_path = Path(csv_path) if csv_path is not None else source_path.with_suffix(".csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with h5.File(source_path, "r") as handle, output_path.open("w", newline="", encoding="utf-8") as csv_handle:
        writer = csv.writer(csv_handle)
        writer.writerow(CSV_COLUMNS)

        frame_ids = handle["frame/frame_id"]
        timestamp_ns = handle["frame/timestamp_ns"]
        sample_indices = handle["pixel/sample_index"][:]
        wavelengths_nm = handle["pixel/wavelength_nm"][:]
        raw_adc = handle["raw/adc_count"]
        processed_adc = handle["processed/adc_count"]
        volts = handle["processed/volts"]
        intensity = handle["processed/intensity"]
        frame_dark = handle["dark/frame_dark_reference_count"]
        automatic_bias = handle["dark/automatic_dark_bias_applied"]
        correction_dataset = handle["correction/correction_factor_applied"]
        correction_static = correction_dataset[:] if correction_dataset.ndim == 1 else None

        total_frames = int(frame_ids.shape[0])
        pixel_count = int(sample_indices.shape[0])
        for start in range(0, total_frames, max(int(chunk_frames), 1)):
            stop = min(start + max(int(chunk_frames), 1), total_frames)
            frame_id_chunk = frame_ids[start:stop]
            timestamp_chunk = timestamp_ns[start:stop]
            raw_chunk = raw_adc[start:stop, :]
            processed_chunk = processed_adc[start:stop, :]
            volts_chunk = volts[start:stop, :]
            intensity_chunk = intensity[start:stop, :]
            frame_dark_chunk = frame_dark[start:stop, :]
            automatic_bias_chunk = automatic_bias[start:stop, :]
            correction_chunk = correction_dataset[start:stop, :] if correction_static is None else None

            for frame_offset in range(stop - start):
                correction_row = correction_static if correction_static is not None else correction_chunk[frame_offset]
                for pixel_index in range(pixel_count):
                    writer.writerow(
                        [
                            int(frame_id_chunk[frame_offset]),
                            int(timestamp_chunk[frame_offset]),
                            int(sample_indices[pixel_index]),
                            format(float(wavelengths_nm[pixel_index]), CSV_FLOAT_FORMAT),
                            int(raw_chunk[frame_offset, pixel_index]),
                            format(float(processed_chunk[frame_offset, pixel_index]), CSV_FLOAT_FORMAT),
                            format(float(frame_dark_chunk[frame_offset, pixel_index]), CSV_FLOAT_FORMAT),
                            format(float(automatic_bias_chunk[frame_offset, pixel_index]), CSV_FLOAT_FORMAT),
                            format(float(correction_row[pixel_index]), CSV_FLOAT_FORMAT),
                            format(float(volts_chunk[frame_offset, pixel_index]), CSV_FLOAT_FORMAT),
                            format(float(intensity_chunk[frame_offset, pixel_index]), CSV_FLOAT_FORMAT),
                        ]
                    )

    return output_path


def inspect_hdf5(path: Path) -> dict[str, Any]:
    h5 = require_h5py()
    result: dict[str, Any] = {
        "path": str(path),
        "attributes": {},
        "datasets": {},
        "frame_count": 0,
        "frame_id_gaps": 0,
        "missing_frame_ids": 0,
    }
    with h5.File(path, "r") as handle:
        result["attributes"] = {key: handle.attrs[key] for key in handle.attrs}

        def visit(name: str, item: Any) -> None:
            if hasattr(item, "shape") and hasattr(item, "dtype"):
                result["datasets"][f"/{name}"] = {
                    "shape": tuple(int(value) for value in item.shape),
                    "dtype": str(item.dtype),
                }

        handle.visititems(visit)
        frame_ids = handle["frame/frame_id"][:]
        result["frame_count"] = int(frame_ids.shape[0])
        if frame_ids.shape[0] >= 2:
            deltas = np.diff(frame_ids.astype(np.int64))
            gaps = deltas[deltas > 1] - 1
            result["frame_id_gaps"] = int(gaps.shape[0])
            result["missing_frame_ids"] = int(np.sum(gaps, initial=0))
    return result
