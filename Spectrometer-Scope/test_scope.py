import struct
import sys
from pathlib import Path
import unittest
import zlib

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scope import demo_capture
from scope_protocol import HEADER, HEADER_V2, FIELDS_V2, decode, packet_size, read_capture
from scope_validate import validate
from scope_video import video_features


def fast_fixture():
    old = demo_capture()
    m = dict.fromkeys(FIELDS_V2, 0)
    m.update(old.metadata)
    m.update(adc_count=12000, adc_target_count=12000, adc_clock_hz=24000000,
             adc_sample_cycles=3, adc_resolution_bits=12, tim2_arr=71,
             adc_start_frame_cycles=(-19200+48) % 2**32, mode=3,
             adc_complete_cycles=round((8799.75 + 17/24 + 1/96 + 100 + 2)*96))
    wire = HEADER_V2.pack(b"CSCP", 2, HEADER_V2.size, *(m[k] for k in FIELDS_V2))
    wire += old.logic.tobytes() + np.full(12000, 2000, dtype="<u2").tobytes()
    return decode(wire + struct.pack("<I", zlib.crc32(wire)))


class ProtocolTests(unittest.TestCase):
    def test_v2_preserves_negative_start_and_pixel_period(self):
        capture = fast_fixture()
        self.assertEqual(len(capture.adc), 12000)
        self.assertAlmostEqual(capture.adc_time_us[0], -199.5)
        self.assertAlmostEqual(capture.adc_time_us[1]-capture.adc_time_us[0], 0.75)
        self.assertEqual(capture.pixel_period_us, 2)
        self.assertAlmostEqual(capture.adc_hold_time_us[0]-capture.adc_time_us[0], 5/24+1/96)

    def test_fragmented_serial_reads_support_both_header_versions(self):
        class Port:
            def __init__(self, wire): self.data = bytearray(b"startup\r\n"+wire)
            def reset_input_buffer(self): pass
            def write(self, command): pass
            def flush(self): pass
            def read(self, size):
                data = bytes(self.data[:min(size, 7)])
                del self.data[:len(data)]
                return data
        for capture in (demo_capture(), fast_fixture()):
            self.assertEqual(read_capture(Port(capture.wire)).wire, capture.wire)

    def test_invalid_v2_adc_clock_is_rejected(self):
        wire = bytearray(fast_fixture().wire)
        struct.pack_into("<I", wire, 8 + 33*4, 48000000)
        with self.assertRaisesRegex(ValueError, "configuration bounds"):
            packet_size(wire)

    def test_v2_extended_header_is_crc_protected(self):
        wire = bytearray(fast_fixture().wire)
        wire[8 + 36*4] ^= 1
        with self.assertRaisesRegex(ValueError, "CRC32"):
            decode(wire)

    def test_round_trip_preserves_every_sample_and_gpio_timestamp(self):
        sample = demo_capture()
        result = decode(sample.wire)
        self.assertTrue(np.array_equal(sample.logic, result.logic))
        self.assertTrue(np.array_equal(sample.adc, result.adc))
        self.assertEqual(len(sample.wire), packet_size(sample.wire))

    def test_payload_corruption_is_rejected(self):
        wire = bytearray(demo_capture().wire)
        wire[HEADER.size + 11] ^= 1
        with self.assertRaisesRegex(ValueError, "CRC32"):
            decode(wire)

    def test_header_corruption_is_rejected(self):
        wire = bytearray(demo_capture().wire)
        wire[4] = 17
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            decode(wire)

    def test_oversized_adc_count_is_rejected_before_allocation(self):
        wire = bytearray(demo_capture().wire)
        struct.pack_into("<I", wire, 8 + 3*4, 0xffffffff)
        with self.assertRaisesRegex(ValueError, "bounds"):
            packet_size(wire)

    def test_nonmonotonic_timestamps_are_rejected_even_with_good_crc(self):
        wire = bytearray(demo_capture().wire)
        struct.pack_into("<I", wire, HEADER.size+8, 0)
        struct.pack_into("<I", wire, len(wire)-4, zlib.crc32(wire[:-4]))
        with self.assertRaisesRegex(ValueError, "timestamps"):
            decode(wire)


class AnalyzerTests(unittest.TestCase):
    def test_raw_overrun_status_rejects_capture_even_without_hal_error(self):
        capture = fast_fixture()
        capture.metadata['adc_sr'] = 32
        checks = {c['name']: c for c in validate(capture)['checks']}
        self.assertEqual(checks['ADC DMA']['status'], 'FAIL')

    def test_flat_trace_does_not_identify_optical_pixel_boundary(self):
        result = video_features(fast_fixture())
        self.assertIsNone(result['leading_half_drop_us'])
        self.assertIsNone(result['trailing_half_return_us'])
        self.assertEqual(result['pixel_alignment'], 'UNVERIFIED')

    def test_local_feature_search_ignores_larger_preframe_step(self):
        capture = fast_fixture()
        t = capture.adc_hold_time_us
        capture.adc[:] = np.where(t < 0, 1000, np.where(t < 676, 3600, 3400))
        result = video_features(capture)
        self.assertAlmostEqual(result['leading_half_drop_us'], 676, delta=.75)
        self.assertEqual(result['pixel_alignment'], 'UNVERIFIED')

    def test_fast_capture_does_not_shrink_ccd_pixel_timing(self):
        capture = fast_fixture()
        # Prevent a synthetic old 0.5 MHz PA5 trace being mistaken for real fast data.
        capture.logic = capture.logic[::12]
        checks = {c['name']: c for c in validate(capture)['checks']}
        self.assertEqual(checks['ADC DMA']['status'], 'PASS')
        self.assertEqual(checks['ADC conversion budget']['status'], 'PASS')
        self.assertIn('2.667 ADC samples/CCD pixel', checks['ADC sampling']['value'])

    def test_insufficient_conversion_time_fails(self):
        capture = fast_fixture()
        capture.metadata['adc_sample_cycles'] = 15
        checks = {c['name']: c for c in validate(capture)['checks']}
        self.assertEqual(checks['ADC conversion budget']['status'], 'FAIL')

    def test_missing_triggers_detected_by_capture_duration(self):
        capture = fast_fixture()
        capture.metadata['adc_complete_cycles'] += 96*1000
        checks = {c['name']: c for c in validate(capture)['checks']}
        self.assertEqual(checks['ADC capture duration']['status'], 'FAIL')

    def test_sensor_timing_is_never_certified_from_mcu_pads(self):
        report = validate(demo_capture())
        self.assertEqual(report["sensor_validation"], "UNVERIFIED")
        checks = {c["name"]: c for c in report["checks"]}
        self.assertEqual(checks["Detector electrical timing"]["status"], "UNVERIFIED")
        self.assertEqual(checks["t4 master phase at ICG rise"]["status"], "UNVERIFIED")

    def test_shifted_raw_video_is_flagged_without_calling_it_a_pixel_boundary(self):
        report = validate(demo_capture())
        self.assertAlmostEqual(report["transition_candidate"]["sample"], 315, delta=8)
        self.assertIn("not proof", report["transition_candidate"]["evidence"])

    def test_sh_high_at_icg_rise_is_a_failure(self):
        checks = {c["name"]: c for c in validate(demo_capture())["checks"]}
        self.assertEqual(checks["t1 ICG rise after SH fall"]["status"], "FAIL")

    def test_aliased_clock_is_unverified(self):
        capture = demo_capture()
        capture.logic = capture.logic[::12]
        checks = {c["name"]: c for c in validate(capture)["checks"]}
        self.assertEqual(checks["Master clock target"]["status"], "UNVERIFIED")

    def test_master_fit_excludes_a_gap_instead_of_counting_missing_edges(self):
        capture = demo_capture()
        capture.logic[4096:, 0] += 9600
        checks = {c['name']: c for c in validate(capture)['checks']}
        self.assertEqual(checks['Master clock target']['status'], 'PASS')
        self.assertIn('without unresolved gaps', checks['Master clock target']['value'])

    def test_short_resolved_fragment_does_not_certify_master_frequency(self):
        capture = demo_capture()
        capture.logic = capture.logic[:40]
        checks = {c['name']: c for c in validate(capture)['checks']}
        self.assertEqual(checks['Master clock target']['status'], 'UNVERIFIED')

    def test_adc_hardware_error_cannot_pass(self):
        capture = demo_capture()
        capture.metadata["adc_errors"] = 2
        checks = {c["name"]: c for c in validate(capture)["checks"]}
        self.assertEqual(checks["ADC DMA"]["status"], "FAIL")

    def test_quantized_clock_period_does_not_create_false_frequency_failure(self):
        capture = demo_capture()
        cycles = np.arange(8192, dtype=np.uint32) * 19 + 19
        us = cycles / 96 + 7900
        ports = capture.logic[:, 1] & np.uint32(~(1 << 8) & 0xffffffff)
        phi = (np.remainder(us + 0.125, 0.5) < 0.25).astype(np.uint32)
        capture.logic[:, 0] = cycles
        capture.logic[:, 1] = ports | ((1-phi) << 8)
        checks = {c["name"]: c for c in validate(capture)["checks"]}
        self.assertEqual(checks["Master clock target"]["status"], "PASS")

    def test_coincident_sampled_edges_do_not_become_next_cycle_t2_failure(self):
        capture = demo_capture()
        capture.logic = capture.logic[::10]
        checks = {c["name"]: c for c in validate(capture)["checks"]}
        self.assertNotEqual(checks["t2 ICG fall to SH rise"]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
