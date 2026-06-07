from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

PYTHON_GUI_ROOT = Path(__file__).resolve().parents[1]
if str(PYTHON_GUI_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_GUI_ROOT))

from backend.models.config import CalibrationConfig, DeviceConfig
from backend.models.frames import BinaryFramePacket
from backend.storage.binary_capture import (
    CSV_COLUMNS,
    DenseBinaryRecorder,
    DenseFrameProcessor,
    export_hdf5_to_csv,
    inspect_hdf5,
    require_h5py,
)

try:
    require_h5py()
    H5PY_AVAILABLE = True
except RuntimeError:
    H5PY_AVAILABLE = False


def _significant_digit_count(text: str) -> int:
    mantissa = text.lower().split("e", 1)[0]
    digits = "".join(character for character in mantissa if character.isdigit()).lstrip("0")
    return len(digits)


@unittest.skipIf(not H5PY_AVAILABLE, "h5py is not available")
class BinaryCaptureCsvTests(unittest.TestCase):
    def test_csv_export_reads_hdf5_arrays_and_preserves_raw_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            hdf5_path = Path(temp_dir) / "capture.h5"
            device_config = DeviceConfig(
                sample_count=4,
                effective_start_index=0,
                effective_sample_count=4,
                trailing_dummy_count=0,
            )
            calibration_config = CalibrationConfig(
                apply_dark_subtraction=False,
                apply_intensity_correction=True,
                intensity_correction=[1.0, 1.125, 1.25, 1.375],
            )
            processor = DenseFrameProcessor(device_config, calibration_config)
            recorder = DenseBinaryRecorder(
                hdf5_path,
                processor.static_data,
                processor.metadata_attributes(),
                chunk_frames=2,
            )
            recorder.start()
            raw_frames = [
                np.asarray([0, 1024, 2048, 4095], dtype=np.uint16),
                np.asarray([5, 1000, 2000, 3000], dtype=np.uint16),
            ]
            for frame_id, adc_counts in enumerate(raw_frames, start=10):
                packet = BinaryFramePacket(
                    frame_counter=frame_id,
                    sample_count=4,
                    effective_start=0,
                    effective_count=4,
                    flags=1,
                    adc_counts=adc_counts,
                    timestamp_ns=1_700_000_000_000_000_000 + frame_id,
                    timestamp=datetime.now(timezone.utc),
                )
                self.assertTrue(recorder.append(processor.build_record(packet)))
            recorder.stop()
            self.assertFalse(recorder.status()["failed"])

            report = inspect_hdf5(hdf5_path)
            self.assertEqual(report["frame_count"], 2)
            self.assertEqual(report["datasets"]["/raw/adc_count"]["shape"], (2, 4))
            self.assertEqual(report["datasets"]["/raw/adc_count"]["dtype"], "uint16")

            csv_path = export_hdf5_to_csv(hdf5_path)
            with csv_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(list(rows[0].keys()), CSV_COLUMNS)
            self.assertEqual(len(rows), 8)
            self.assertEqual([int(row["raw_adc_count"]) for row in rows[:4]], raw_frames[0].tolist())
            self.assertEqual([int(row["raw_adc_count"]) for row in rows[4:]], raw_frames[1].tolist())

            derived_columns = [
                "wavelength_nm",
                "processed_adc_count",
                "frame_dark_reference_count",
                "automatic_dark_bias_applied",
                "correction_factor_applied",
                "volts",
                "processed_intensity",
            ]
            for row in rows:
                for column in derived_columns:
                    self.assertLessEqual(_significant_digit_count(row[column]), 8)


if __name__ == "__main__":
    unittest.main()
