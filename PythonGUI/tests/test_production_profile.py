import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zlib
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from backend.device.packet_reader import DeviceStreamReader
from backend.device.protocol import FRAME_V3_HEADER_STRUCT
from backend.models.config import CalibrationConfig, DeviceConfig
from backend.models.frames import BinaryFramePacket
from backend.processing.calibration_manager import CalibrationManager
from backend.processing.spectrum_builder import SpectrumBuilder
from backend.storage.binary_capture import DenseFrameProcessor, DenseBinaryRecorder, require_h5py
from backend.storage.session_archive import export_session_archive

PROFILE = 65537

def wire(frame_id=1, code=3500):
    header = FRAME_V3_HEADER_STRUCT.pack(b'CCD1', 3, 1, 0, frame_id, 3694, 32, 3648, 1, 7388, 100, PROFILE)
    body = header + struct.pack('<3694H', *([code]*3694))
    return body + struct.pack('<I', zlib.crc32(body))

def packet(profile=PROFILE):
    return BinaryFramePacket(1, 3694, 32, 3648, 1, np.asarray([3650]*32+[3500]*3648+[3650]*14, dtype=np.uint16),
                             1000000000, integration_us=100, timing_profile_id=profile)

class ProductionProfileTests(unittest.TestCase):
    def test_fragmentation_crc_rejection_and_recovery(self):
        corrupted = bytearray(wire(2)); corrupted[102] ^= 16
        stream = wire() + corrupted + wire(3)
        reader = DeviceStreamReader(); frames = []
        for start in range(0, len(stream), 127):
            frames.extend(p for p in reader.feed(stream[start:start+127]) if isinstance(p, BinaryFramePacket))
        self.assertEqual([p.frame_counter for p in frames], [1, 3])
        self.assertEqual([p.timing_profile_id for p in frames], [PROFILE]*2)
        self.assertTrue(all(len(p.adc_counts) == 3694 for p in frames))

    def test_valid_crc_does_not_accept_out_of_range_adc(self):
        frames = DeviceStreamReader().feed(wire(code=4096))
        self.assertFalse(any(isinstance(p, BinaryFramePacket) for p in frames))

    def test_legacy_calibration_bypassed_consistently_in_live_and_recorded_data(self):
        config = CalibrationConfig(bias_counts=[100]*3694, dark_offset_counts=[20]*3694, dark_integration_us=100)
        builder = SpectrumBuilder(CalibrationManager(config), DeviceConfig())
        live = builder.build_from_frame(packet())
        record = DenseFrameProcessor(DeviceConfig(), config).build_record(packet())
        self.assertFalse(live.dark_calibration_applied)
        self.assertFalse(record.dark_calibration_applied)
        self.assertTrue(np.all(record.automatic_dark_bias_applied == 0))
        self.assertIn('timing profile mismatch', live.reference_status)
        np.testing.assert_allclose(live.live_display_counts, record.processed_intensity, atol=1e-7)
        self.assertEqual(live.adc_counts, packet().adc_counts.tolist())
        config.bias_timing_profile_id = config.dark_timing_profile_id = PROFILE
        builder = SpectrumBuilder(CalibrationManager(config), DeviceConfig())
        self.assertTrue(builder.build_from_frame(packet()).dark_calibration_applied)
        self.assertFalse(builder.build_from_frame(packet(PROFILE+1)).dark_calibration_applied)
        changed = packet(); changed.integration_us = 200
        self.assertFalse(builder.build_from_frame(changed).dark_calibration_applied)

    def test_flat_light_response_does_not_become_verified_dark(self):
        config = CalibrationConfig(bias_counts=[3655]*3694, bias_timing_profile_id=PROFILE)
        builder = SpectrumBuilder(CalibrationManager(config), DeviceConfig())
        self.assertIn('Reference shifted', builder.reference_status([1800]*3694, PROFILE))
        self.assertNotIn('Reference shifted', builder.reference_status([3655]*3694, PROFILE))

    def test_profile_preserved_in_hdf5_and_archive(self):
        processor = DenseFrameProcessor(DeviceConfig(), CalibrationConfig())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'profile.h5'
            recorder = DenseBinaryRecorder(path, processor.static_data, processor.metadata_attributes())
            recorder.start(); recorder.append(processor.build_record(packet())); recorder.stop()
            with require_h5py().File(path) as handle:
                self.assertEqual(handle['frame/timing_profile_id'][0], PROFILE)
            with ZipFile(export_session_archive(path)) as archive:
                manifest = json.loads(archive.read("calibration.json"))
            self.assertEqual(manifest["timing_ranges"][0]["timing_profile_id"], PROFILE)

if __name__ == '__main__':
    unittest.main()
