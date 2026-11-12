from __future__ import annotations

import importlib.util
import json
import struct
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "PythonGUI"))

import numpy as np
from backend.core.integration_control import IntegrationControl
from backend.core.state_manager import StateManager
from backend.device.integration import SHORT_SETTINGS, adjacent_settings, parse_duration, valid_integration
from backend.device.packet_reader import DeviceStreamReader
from backend.device.protocol import FRAME_HEADER_STRUCT, LEGACY_FRAME_HEADER_STRUCT
from backend.models.config import CalibrationConfig, DeviceConfig, UserConfig
from backend.models.frames import BinaryFramePacket
from backend.processing.calibration_manager import CalibrationManager
from backend.processing.spectrum_builder import SpectrumBuilder
from backend.storage.binary_capture import DenseBinaryRecorder, DenseFrameProcessor, require_h5py
from backend.storage.session_archive import export_session_archive


def wire_frame(version=2, us=12500, frame_id=7):
    fields = (b"CCD1", version, 1, 0, frame_id, 4, 0, 4, 1, 8)
    header = FRAME_HEADER_STRUCT.pack(*fields, us) if version == 2 else LEGACY_FRAME_HEADER_STRUCT.pack(*fields)
    return header + struct.pack("<4H", 0, 10, 4095, 1024)


class SettingsTests(unittest.TestCase):
    def test_all_short_settings(self):
        for us in range(1, 8001):
            self.assertEqual(valid_integration(us), us >= 10 and 8000 % us == 0)

    def test_long_settings_and_bounds(self):
        for us in (8001, 10000, 12500, 32000, 32001, 100001, 5_000_000):
            self.assertTrue(valid_integration(us))
        for us in (0, -1, 9, 3000, 5_000_001, Decimal("8000.5")):
            self.assertFalse(valid_integration(us))

    def test_adjacent_and_stepping(self):
        self.assertEqual(adjacent_settings(3000), (2000, 4000))
        self.assertEqual(adjacent_settings(8000), (4000, 8001))
        self.assertEqual(adjacent_settings(8001), (8000, 8002))
        self.assertEqual(adjacent_settings(Decimal("12500.5")), (12500, 12501))
        self.assertEqual(adjacent_settings(10), (None, 16))
        self.assertEqual(adjacent_settings(5_000_000), (4_999_999, None))
        for left, right in zip(SHORT_SETTINGS, SHORT_SETTINGS[1:]):
            self.assertEqual(adjacent_settings(left)[1], right)
            self.assertEqual(adjacent_settings(right)[0], left)

    def test_units_do_not_round(self):
        self.assertEqual(parse_duration("12.5", "ms"), 12500)
        self.assertEqual(parse_duration("0.100001", "s"), 100001)
        for text in ("8.0005", "NaN", "Infinity"):
            with self.assertRaises(ValueError):
                parse_duration(text, "ms")


class ProtocolTests(unittest.TestCase):
    def test_fragmented_mixed_versions_and_responses(self):
        data = b"PENDING INTEG 12500\r\n" + wire_frame(1) + wire_frame() + b"OK INTEG 12500 7\r\n"
        reader = DeviceStreamReader()
        packets = []
        for byte in data:
            packets.extend(reader.feed(bytes([byte])))
        frames = [p for p in packets if isinstance(p, BinaryFramePacket)]
        self.assertEqual([f.integration_us for f in frames], [None, 12500])
        self.assertEqual(frames[1].adc_counts.tolist(), [0, 10, 4095, 1024])
        self.assertEqual(len(packets), 4)

    def test_invalid_duration_resynchronizes(self):
        packets = DeviceStreamReader().feed(wire_frame(us=3000) + wire_frame())
        self.assertEqual(len([p for p in packets if isinstance(p, BinaryFramePacket)]), 1)

    def test_inspector_accepts_both_versions(self):
        spec = importlib.util.spec_from_file_location("ccd_inspector", ROOT / "Spectrometer-COM-Inspector/spectrometer_com_inspector.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        counter = module.Ccd1FrameCounter()
        counter.feed(wire_frame(1) + wire_frame(frame_id=8))
        self.assertEqual(counter.stats.frames_seen, 2)
        self.assertEqual(counter.stats.last_integration_us, 12500)


class IntegrationControlTests(unittest.TestCase):
    def setUp(self):
        self.state = StateManager(UserConfig(), CalibrationConfig())
        self.sent = []
        self.transport = SimpleNamespace(is_connected=lambda: True, write=self.sent.append)
        self.control = IntegrationControl(self.transport, self.state)

    def tearDown(self):
        self.control.reset()

    def test_confirmation_requires_ack_and_matching_frame(self):
        self.assertTrue(self.control.request(12500).ok)
        self.control.receive_text("OK INTEG 12500 7")
        self.assertEqual(self.state.snapshot().device.integration_state, "Pending")
        self.control.receive_frame(SimpleNamespace(integration_us=10, frame_counter=6, flags=1))
        self.assertEqual(self.state.snapshot().device.integration_state, "Pending")
        self.control.receive_frame(SimpleNamespace(integration_us=12500, frame_counter=7, flags=1))
        self.assertEqual(self.state.snapshot().device.integration_state, "Applied")
        self.assertIsNone(self.control.pending_us)

    def test_frame_before_ack_and_busy(self):
        self.control.request(8001)
        self.assertFalse(self.control.request(16000).ok)
        self.assertEqual(self.sent, [b"INTEG 8001\n"])
        self.control.receive_frame(SimpleNamespace(integration_us=8001, frame_counter=9, flags=1))
        self.control.receive_text("OK INTEG 8001 9")
        self.assertEqual(self.state.snapshot().device.integration_state, "Applied")

    def test_only_confirmed_request_calls_applied_callback(self):
        confirmed = []
        self.control.request(12500, on_applied=confirmed.append)
        self.control.receive_text("OK INTEG 12500 7")
        self.assertEqual(confirmed, [])
        frame = SimpleNamespace(integration_us=12500, frame_counter=7, flags=1)
        self.control.receive_frame(frame)
        self.control.receive_frame(frame)
        self.assertEqual(confirmed, [12500])

        self.control.request(25000, on_applied=confirmed.append)
        self.control.receive_text("ERR INTEG INVALID")
        self.control.request(1000000)
        self.control.receive_text("OK INTEG 1000000 8")
        self.control.receive_frame(SimpleNamespace(integration_us=1000000, frame_counter=8, flags=1))
        self.assertEqual(confirmed, [12500])

    def test_timeout_and_fault_do_not_apply_requested_metadata(self):
        self.control.request(5_000_000)
        self.assertAlmostEqual(self.control.timer.interval, 11.008)
        self.control._timeout()
        self.assertEqual(self.state.snapshot().device.integration_state, "Timeout")
        self.assertIsNone(self.state.snapshot().device.integration_us)
        self.control.request(10)
        self.control.receive_text("ERR INTEG TIMING")
        self.assertEqual(self.state.snapshot().device.integration_state, "Fault")

    def test_canceled_timeout_cannot_cancel_later_request(self):
        self.control.request(10000)
        old_generation = self.control.generation
        self.control.reset()
        self.control.request(12500)
        self.control._timeout(old_generation)
        self.assertEqual(self.control.pending_us, 12500)
        self.assertEqual(self.state.snapshot().device.integration_state, "Pending")

    def test_change_from_long_exposure_uses_old_frame_interval(self):
        packet = DeviceStreamReader().feed(wire_frame(us=5_000_000))[0]
        self.state.update_from_frame(packet)
        self.control.request(10)
        self.assertAlmostEqual(self.control.timer.interval, 6.016)

    def test_rejection_and_disconnect(self):
        self.assertFalse(self.control.request(3000).ok)
        self.assertEqual(self.sent, [])
        self.control.request(10000)
        self.control.receive_text("ERR INTEG INVALID")
        self.assertEqual(self.state.snapshot().device.integration_state, "Error")
        self.control.request(10000)
        self.control.reset()
        self.assertIsNone(self.control.pending_us)


class MetadataTests(unittest.TestCase):
    def test_dark_reference_requires_exact_integration(self):
        config = CalibrationConfig(dark_offset_counts=[50.0] * 4, dark_integration_us=12500)
        device = DeviceConfig(sample_count=4, effective_start_index=0, effective_sample_count=4)
        processor = DenseFrameProcessor(device, config)
        builder = SpectrumBuilder(CalibrationManager(config), device)
        for us, expected in ((None, False), (10, False), (12500, True)):
            packet = BinaryFramePacket(frame_counter=1, sample_count=4, effective_start=0,
                                       effective_count=4, flags=1, adc_counts=np.ones(4, dtype=np.uint16),
                                       timestamp_ns=1, integration_us=us)
            record = processor.build_record(packet)
            self.assertEqual(record.integration_us, us)
            self.assertEqual(record.dark_calibration_applied, expected)
            self.assertEqual(builder.build_from_frame(packet).dark_calibration_applied, expected)
            self.assertEqual(record.automatic_dark_bias_applied.tolist(), [50.0 if expected else 0.0] * 4)

    def test_recording_archive_and_legacy_unknown_duration(self):
        h5py = require_h5py()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "timing.h5"
            processor = DenseFrameProcessor(DeviceConfig(sample_count=4), CalibrationConfig())
            recorder = DenseBinaryRecorder(path, processor.static_data, processor.metadata_attributes(), chunk_frames=1)
            recorder.start()
            for packet in DeviceStreamReader().feed(wire_frame(1) + wire_frame()):
                self.assertTrue(recorder.append(processor.build_record(packet)))
            recorder.stop()
            self.assertFalse(recorder.status()["failed"])
            with h5py.File(path, "r") as handle:
                self.assertEqual(handle["frame/integration_us"][:].tolist(), [0, 12500])
            with ZipFile(export_session_archive(path)) as archive:
                timing = json.loads(archive.read("calibration.json"))["timing_ranges"]
            self.assertEqual([entry["integration_us"] for entry in timing], [None, 12500])

            with h5py.File(path, "a") as handle:
                revision = handle["calibration/revisions/0"]
                handle.attrs["calibration_config_json"] = revision["config_json"].asstr()[()]
                handle.create_group("correction")
                for name in ("qe_correction", "system_response_correction", "correction_factor_applied"):
                    handle.move(revision[name].name, f"correction/{name}")
                handle.move(revision["wavelength_nm"].name, "pixel/wavelength_nm")
                del handle["calibration"]
                del handle["frame/calibration_revision"]
                del handle["frame/timing_profile_id"]
            for version in ("dense-hdf5-v3", "dense-hdf5-v2", "dense-hdf5-v1"):
                with self.subTest(version=version):
                    with h5py.File(path, "a") as handle:
                        handle.attrs["format_version"] = version
                        if version == "dense-hdf5-v1":
                            del handle["frame/integration_us"]
                            del handle["frame/dark_calibration_applied"]
                    with ZipFile(export_session_archive(path)) as archive:
                        manifest = json.loads(archive.read("calibration.json"))
                    self.assertEqual(len(manifest["calibrations"]), 1)
                    expected = [None] if version == "dense-hdf5-v1" else [None, 12500]
                    self.assertEqual([entry["integration_us"] for entry in manifest["timing_ranges"]], expected)
                    self.assertTrue(all(entry["timing_profile_id"] is None for entry in manifest["timing_ranges"]))


if __name__ == "__main__":
    unittest.main()
