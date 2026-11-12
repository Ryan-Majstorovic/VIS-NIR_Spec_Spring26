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
from backend.models.config import CalibrationConfig, DeviceConfig, SaturationPlotReference, SaturationReference
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
        calibration_manager = CalibrationManager(config)
        builder = SpectrumBuilder(calibration_manager, DeviceConfig())
        bright = packet()
        bright.adc_counts[:] = 1800
        frame = builder.build_from_frame(bright)
        self.assertTrue(frame.reference_shifted)
        self.assertIn('Reference shifted', frame.reference_status)
        self.assertFalse(builder.build_from_frame(packet()).reference_shifted)

        bright.adc_counts[16:29] = 3473
        self.assertFalse(builder.build_from_frame(bright).reference_shifted)
        bright.adc_counts[16:29] = 3472
        self.assertTrue(builder.build_from_frame(bright).reference_shifted)
        bright.timing_profile_id = PROFILE + 1
        self.assertFalse(builder.build_from_frame(bright).reference_shifted)
        calibration_manager.update_config(CalibrationConfig())
        rebuilt = builder.rebuild_live_frame(frame)
        self.assertFalse(rebuilt.reference_shifted)
        self.assertIn('Reference unverified', rebuilt.reference_status)

    def test_calibrated_scale_uses_shared_fifth_percentile_floor_only_in_absolute_mode(self):
        limits = [0.0] * 3694
        limits[32:132] = [1200.0] * 100
        limits[132:412] = [1700.0] * 280
        limits[412:3680] = [2050.0] * 3268
        dark_baseline = [3650.0] * 3694
        dark_baseline[32:412] = [3600.0] * 380
        reference = SaturationReference(
            raw_counts=limits, dark_baseline=dark_baseline, timing_profile_id=PROFILE,
            effective_start_index=32, effective_sample_count=3648, adc_resolution_bits=12, frame_count=8,
        )
        config = CalibrationConfig(
            saturation_reference=reference, bias_counts=[3650] * 3694, bias_timing_profile_id=PROFILE,
            dark_offset_counts=[50] * 3694, dark_integration_us=100, dark_timing_profile_id=PROFILE,
            intensity_correction=[1.5] * 3694,
        )
        calibration_manager = CalibrationManager(config)
        builder = SpectrumBuilder(calibration_manager, DeviceConfig())
        exposure = packet()
        exposure.adc_counts = np.asarray(limits, dtype=np.uint16)
        exposure.adc_counts[[50, 450]] = 2700
        frame = builder.build_from_frame(exposure)
        expected = np.clip((3650.0 - exposure.adc_counts[32:3680]) / (3650.0 - 1700.0), 0.0, 1.0)
        np.testing.assert_allclose(frame.live_display_counts[32:3680], expected)
        self.assertEqual(frame.live_display_counts[50], frame.live_display_counts[450])
        self.assertTrue(frame.near_saturation)
        calibration_manager.update_config(config.model_copy(update={"show_potential_saturation_warning": False}))
        rebuilt = builder.rebuild_live_frame(frame)
        self.assertFalse(rebuilt.near_saturation)
        np.testing.assert_allclose(rebuilt.live_display_counts, frame.live_display_counts)
        calibration_manager.update_config(config.model_copy(update={"use_calibrated_saturation_scale": False}))
        rebuilt = builder.rebuild_live_frame(frame)
        self.assertTrue(rebuilt.near_saturation)
        self.assertLess(max(rebuilt.live_display_counts[32:3680]), 1.0)
        self.assertEqual(rebuilt.spectrogram_row, frame.spectrogram_row)

        auto = config.model_copy(update={"display_normalization_mode": "auto_peak"})
        calibration_manager.update_config(auto)
        ranged = builder.rebuild_live_frame(frame)
        self.assertTrue(ranged.near_saturation)
        calibration_manager.update_config(auto.model_copy(update={"use_calibrated_saturation_scale": False}))
        np.testing.assert_allclose(builder.rebuild_live_frame(frame).live_display_counts, ranged.live_display_counts)

    def test_warning_uses_exact_per_pixel_margin_and_adjacent_active_pixels(self):
        reference = SaturationReference(
            raw_counts=[1600.0] * 3694, dark_baseline=[3600.0] * 3694, timing_profile_id=PROFILE,
            effective_start_index=32, effective_sample_count=3648, adc_resolution_bits=12, frame_count=8,
        )
        config = CalibrationConfig(saturation_reference=reference)
        builder = SpectrumBuilder(CalibrationManager(config), DeviceConfig())
        exposure = packet()
        exposure.adc_counts[30:34] = 1850
        self.assertFalse(builder.build_from_frame(exposure).near_saturation)
        exposure.adc_counts[34] = 1851
        self.assertFalse(builder.build_from_frame(exposure).near_saturation)
        exposure.adc_counts[34] = 1850
        self.assertTrue(builder.build_from_frame(exposure).near_saturation)

        exposure.timing_profile_id = PROFILE + 1
        mismatched = builder.build_from_frame(exposure)
        self.assertFalse(mismatched.near_saturation)
        self.assertLess(max(mismatched.live_display_counts), 1.0)
        exposure.timing_profile_id = PROFILE
        exposure.effective_start += 1
        exposure.effective_count -= 1
        self.assertFalse(builder.build_from_frame(exposure).near_saturation)

    def test_trimmed_plot_reference_is_independent_of_warning_and_spectrogram(self):
        reference = SaturationReference(
            raw_counts=[1500.0] * 3694, dark_baseline=[3650.0] * 3694, timing_profile_id=PROFILE,
            effective_start_index=32, effective_sample_count=3648, adc_resolution_bits=12, frame_count=8,
        )
        plot_reference = SaturationPlotReference(**reference.model_dump(), plateau_adc=1800)
        config = CalibrationConfig(saturation_reference=reference, saturation_plot_reference=plot_reference)
        manager = CalibrationManager(config)
        builder = SpectrumBuilder(manager, DeviceConfig())
        exposure = packet()
        exposure.adc_counts[32:35] = 1800
        frame = builder.build_from_frame(exposure)
        self.assertEqual(frame.live_display_counts[32:35], [1.0] * 3)
        self.assertFalse(frame.near_saturation)
        exposure.adc_counts[32:35] = 1768
        self.assertTrue(builder.build_from_frame(exposure).near_saturation)
        manager.update_config(config.model_copy(update={"use_calibrated_saturation_scale": False}))
        rebuilt = builder.rebuild_live_frame(frame)
        self.assertLess(rebuilt.live_display_counts[32], 1.0)
        self.assertFalse(rebuilt.near_saturation)
        self.assertEqual(rebuilt.spectrogram_row, frame.spectrogram_row)
        manager.update_config(config.model_copy(update={"saturation_reference": None}))
        self.assertFalse(builder.build_from_frame(exposure).near_saturation)
        self.assertEqual(builder.build_from_frame(exposure).live_display_counts[32], 1.0)

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
