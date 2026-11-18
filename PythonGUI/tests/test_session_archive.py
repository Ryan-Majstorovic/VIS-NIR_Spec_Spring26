from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from threading import Event, Thread
from typing import Callable
from unittest.mock import patch
from zipfile import ZipFile

import numpy as np

from backend.core.command_service import CommandService
from backend.core.session_manager import SessionManager
from backend.core.state_manager import StateManager
from backend.device.serial_transport import SerialTransport
from backend.models.config import CalibrationConfig, DeviceConfig, UserConfig
from backend.models.frames import BinaryFramePacket
from backend.processing.calibration_manager import CalibrationManager
from backend.processing.spectrum_builder import SpectrumBuilder
from backend.storage.binary_capture import CSV_COLUMNS, require_h5py
from backend.storage.session_archive import export_session_archive


class SessionArchiveTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.capture = Path(directory.name) / "capture.h5"
        device = DeviceConfig(sample_count=4, effective_start_index=0, effective_sample_count=4, trailing_dummy_count=0)
        self.initial = CalibrationConfig(apply_dark_subtraction=False)
        calibration = CalibrationManager(self.initial)
        self.state = StateManager(UserConfig(device=device), self.initial)
        self.service = CommandService(
            state_manager=self.state,
            session_manager=SessionManager(),
            transport=SerialTransport(),
            calibration_manager=calibration,
            spectrum_builder=SpectrumBuilder(calibration, device),
            binary_export_dir=self.capture.parent,
        )
        self.addCleanup(self.service.stop_binary_recording)

    def _frame(self, frame_id: int, integration_us: int = 100) -> None:
        self.service._process_packet(BinaryFramePacket(
            frame_counter=frame_id,
            sample_count=4,
            effective_start=0,
            effective_count=4,
            flags=1,
            adc_counts=np.array([10, 20, 30, 40], dtype=np.uint16),
            timestamp_ns=1_000_000_000 + frame_id,
            integration_us=integration_us,
            timing_profile_id=65537,
        ))

    def test_saved_calibration_and_timing_ranges_join_to_frame_data(self) -> None:
        preview = self.initial.model_copy(update={"intensity_correction": [3.0] * 4})
        self.service.apply_calibration_config(preview)
        self.assertTrue(self.service.start_binary_recording(self.capture).ok)
        self._frame(0xFFFFFFFF)
        self.service.apply_calibration_config(preview)
        self._frame(0)
        saved = CalibrationConfig(
            intensity_correction=[2.0] * 4,
            dark_offset_counts=[200.0] * 4,
            dark_integration_us=100,
            dark_timing_profile_id=65537,
        )
        self.service.apply_calibration_config(saved, saved=True)
        self._frame(2)
        self._frame(3, 200)
        self.service.apply_calibration_config(preview, saved=True)
        self.assertTrue(self.service.stop_binary_recording().ok)
        self.assertTrue(self.service.export_session().ok)

        with ZipFile(self.capture.with_suffix(".zip")) as archive:
            self.assertEqual(archive.namelist(), ["frames.csv", "calibration.json"])
            manifest = json.loads(archive.read("calibration.json"))
            rows = list(csv.DictReader(io.StringIO(archive.read("frames.csv").decode())))
        self.assertEqual(list(rows[0]), CSV_COLUMNS)
        self.assertEqual([int(row["frame_id"]) for row in rows[::4]], [0xFFFFFFFF, 0, 2, 3])
        self.assertEqual([int(row["frame_index"]) for row in rows[::4]], [0, 1, 2, 3])
        self.assertEqual([int(row["raw_adc_count"]) for row in rows], [10, 20, 30, 40] * 4)
        self.assertEqual([float(row["processed_adc_count"]) for row in rows[::4]], [4085, 4085, 380, 0])
        self.assertEqual(manifest["recording_format_version"], "dense-hdf5-v4")
        self.assertEqual(manifest["device_config"]["sample_count"], 4)
        self.assertEqual([item["correction_factor_applied"] for item in manifest["calibrations"]], [[1.0] * 4, [2.0] * 4])
        self.assertEqual(manifest["calibrations"][1]["config"]["dark_offset_counts"], [200.0] * 4)
        self.assertEqual(manifest["calibration_ranges"], [
            {"start_frame_index": 0, "end_frame_index": 2, "calibration_revision": 0, "dark_calibration_applied": False},
            {"start_frame_index": 2, "end_frame_index": 3, "calibration_revision": 1, "dark_calibration_applied": True},
            {"start_frame_index": 3, "end_frame_index": 4, "calibration_revision": 1, "dark_calibration_applied": False},
        ])
        self.assertEqual(manifest["timing_ranges"], [
            {"start_frame_index": 0, "end_frame_index": 3, "integration_us": 100, "timing_profile_id": 65537},
            {"start_frame_index": 3, "end_frame_index": 4, "integration_us": 200, "timing_profile_id": 65537},
        ])
        with require_h5py().File(self.capture, "r") as handle:
            self.assertEqual(handle["frame/calibration_revision"][:].tolist(), [0, 0, 1, 1])
            for column, dataset in (
                ("processed_adc_count", "processed/adc_count"),
                ("volts", "processed/volts"),
                ("processed_intensity", "processed/intensity"),
            ):
                np.testing.assert_allclose(
                    [float(row[column]) for row in rows], handle[dataset][:].ravel(),
                )

    def test_recording_keeps_starting_spectrum_scaling_across_calibration_saves(self) -> None:
        self.service.apply_calibration_config(self.initial.model_copy(update={"display_normalization_mode": "auto_peak"}))
        self.assertTrue(self.service.start_binary_recording(self.capture).ok)
        self._frame(1)
        self.service.apply_calibration_config(self.initial)
        self._frame(2)
        self.service.apply_calibration_config(self.initial.model_copy(update={"intensity_correction": [2.0] * 4}), saved=True)
        self._frame(3)
        self.assertTrue(self.service.stop_binary_recording().ok)

        with require_h5py().File(self.capture, "r") as handle:
            self.assertEqual(handle["frame/calibration_revision"][:].tolist(), [0, 0, 1])
            for revision in (0, 1):
                config = json.loads(handle[f"calibration/revisions/{revision}/config_json"][()])
                self.assertEqual(config["display_normalization_mode"], "auto_peak")
            np.testing.assert_allclose(handle["processed/intensity"][:, 0], [1.0, 1.0, 1.0])

        next_capture = self.capture.with_name("next.h5")
        self.assertTrue(self.service.start_binary_recording(next_capture).ok)
        self._frame(4)
        self.assertTrue(self.service.stop_binary_recording().ok)
        with require_h5py().File(next_capture, "r") as handle:
            config = json.loads(handle["calibration/revisions/0/config_json"][()])
            self.assertEqual(config["display_normalization_mode"], "absolute_saturation")

    def test_export_requires_a_stopped_recording_with_frames(self) -> None:
        self.assertFalse(self.service.export_session().ok)
        self.assertTrue(self.service.start_binary_recording(self.capture).ok)
        self.assertFalse(self.service.export_session().ok)
        self.assertTrue(self.service.stop_binary_recording().ok)
        self.assertFalse(self.service.export_session().ok)
        with self.assertRaisesRegex(ValueError, "contains no frames"):
            export_session_archive(self.capture)
        self.assertFalse(self.capture.with_suffix(".zip").exists())

    def test_failed_export_keeps_existing_archive_and_removes_temporary_file(self) -> None:
        self.assertTrue(self.service.start_binary_recording(self.capture).ok)
        self._frame(1)
        self.assertTrue(self.service.stop_binary_recording().ok)
        destination = self.capture.parent / "Selected Folder"
        destination.mkdir()
        output = destination / "Saved Session.zip"
        self.assertTrue(self.service.export_session(output).ok)
        self.assertEqual(self.state.snapshot().recording.last_zip_path, str(output))
        self.assertFalse(self.capture.with_suffix(".zip").exists())
        original = output.read_bytes()
        source = self.capture.read_bytes()
        with patch("backend.storage.session_archive.write_frame_csv", side_effect=OSError("disk full")):
            result = self.service.export_session(output)
        self.assertFalse(result.ok)
        self.assertIn("disk full", result.message)
        self.assertIsNone(self.state.snapshot().recording.export_percent)
        self.assertEqual(output.read_bytes(), original)
        self.assertEqual(self.capture.read_bytes(), source)
        self.assertEqual(set(destination.iterdir()), {output})
        self.assertTrue(self.service.export_session(output).ok)

    def test_duplicate_export_is_rejected_while_first_export_runs(self) -> None:
        self.assertTrue(self.service.start_binary_recording(self.capture).ok)
        self._frame(1)
        self.assertTrue(self.service.stop_binary_recording().ok)
        started, finish = Event(), Event()
        results = []

        def export(path: Path, output_path: Path | None, *, on_progress: Callable[[int], None]) -> Path:
            on_progress(50)
            started.set()
            if not finish.wait(5):
                raise TimeoutError("Test did not release the export.")
            return export_session_archive(path, output_path)

        with patch("backend.core.command_service.export_session_archive", side_effect=export):
            worker = Thread(target=lambda: results.append(self.service.export_session()))
            worker.start()
            try:
                self.assertTrue(started.wait(5))
                self.assertTrue(self.state.snapshot().recording.exporting)
                self.assertEqual(self.state.snapshot().recording.export_percent, 50)
                self.assertFalse(self.service.export_session().ok)
            finally:
                finish.set()
                worker.join(5)
        self.assertTrue(results[0].ok)
        self.assertFalse(self.state.snapshot().recording.exporting)
        self.assertIsNone(self.state.snapshot().recording.export_percent)

    def test_export_reports_frames_written_and_reserves_completion_until_publish(self) -> None:
        self.assertTrue(self.service.start_binary_recording(self.capture).ok)
        self._frame(1)
        self._frame(2)
        self.assertTrue(self.service.stop_binary_recording().ok)
        destination = self.capture.with_suffix(".zip")
        progress = []

        def report(percent: int) -> None:
            progress.append((percent, destination.exists()))

        export_session_archive(self.capture, destination, on_progress=report)
        self.assertEqual(progress, [(50, False), (99, False), (100, True)])
