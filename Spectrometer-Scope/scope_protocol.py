"""Bounded, CRC-protected diagnostic capture wire protocol (CSCP v1/v2)."""
from dataclasses import dataclass
import struct
import time
import zlib

import numpy as np

MAGIC = b"CSCP"
HEADER = struct.Struct("<4sHH32I")
FIELDS = (
    "capture_id cpu_hz logic_count adc_count logic_stride adc_first_delay_cycles "
    "origin_cycles logic_stride_cycles frame_period_cycles integration_us pin_mapping "
    "board_inversion_mask flags adc_dma_remaining adc_errors tim1_psc tim1_arr tim1_ccr "
    "tim2_psc tim2_arr tim3_psc tim3_arr tim3_ccr tim4_psc tim4_arr tim4_ccr "
    "logic_start_phase_ticks mode tim2_smcr tim3_ccer tim4_ccer build_family"
).split()
HEADER_V2 = struct.Struct("<4sHH48I")
FIELDS_V2 = FIELDS + (
    "adc_target_count adc_clock_hz adc_sample_cycles adc_resolution_bits adc_start_frame_cycles "
    "adc_cr1 adc_cr2 adc_smpr2 tim4_cr2 tim4_ccr2 adc_complete_cycles adc_complete_phase_ticks "
    "adc_sr dma_errors adc_initial_counter reserved"
).split()
MODES = ("production", "productionoverview", "fast", "fastoverview", "slow", "corrected", "correctedoverview", "exposed", "exposedoverview", "zoom", "overview")


def header_layout(data):
    if len(data) < 8:
        raise ValueError("Incomplete scope header")
    magic, version, size = struct.unpack_from("<4sHH", data)
    layout, fields = (HEADER, FIELDS) if version == 1 else (HEADER_V2, FIELDS_V2)
    if magic != MAGIC or version not in (1, 2) or size != layout.size:
        raise ValueError("Unsupported diagnostic packet header")
    return layout, fields


@dataclass
class Capture:
    metadata: dict
    logic: np.ndarray
    adc: np.ndarray
    wire: bytes

    @property
    def time_us(self):
        return self.logic[:, 0].astype(float) / self.metadata["cpu_hz"] * 1e6

    @property
    def frame_time_us(self):
        m = self.metadata
        # Use the actual observed GPIO edge as time zero whenever available.
        # MCU PB6 rises at the configured frame wrap (detector fall after U1).
        icg = self.signals(inferred_detector=True)["ICG"]
        falling = np.flatnonzero(np.diff(icg) == -1) + 1
        if len(falling):
            return self.time_us - self.time_us[falling[0]]
        return self.time_us + m["logic_start_phase_ticks"] * (m["tim4_psc"] + 1) / m["cpu_hz"] * 1e6 - m["frame_period_cycles"] / m["cpu_hz"] * 1e6

    @property
    def adc_time_us(self):
        m = self.metadata
        # Projection from captured register values, not a measured ADC aperture.
        first = m["tim4_ccr"] * (m["tim4_psc"] + 1) + m["adc_first_delay_cycles"]
        if "adc_start_frame_cycles" in m:
            first = m["adc_start_frame_cycles"]
            if first >= 2**31:
                first -= 2**32
        period = (m["tim2_psc"] + 1) * (m["tim2_arr"] + 1)
        return (first + np.arange(len(self.adc)) * period) / m["cpu_hz"] * 1e6

    @property
    def pixel_period_us(self):
        m = self.metadata
        return 4 * (m["tim1_psc"] + 1) * (m["tim1_arr"] + 1) / m["cpu_hz"] * 1e6

    @property
    def adc_hold_time_us(self):
        """Estimated end of aperture, including ST's trigger latency; not measured."""
        m = self.metadata
        return self.adc_time_us + (m.get("adc_sample_cycles", 15) + 2) / m.get("adc_clock_hz", 24_000_000)*1e6 + 1e6/m["cpu_hz"]

    def signals(self, inferred_detector=False):
        ports = self.logic[:, 1]
        signals = {name: ((ports >> bit) & 1).astype(np.int8) for name, bit in (("phiM", 8), ("SH", 6), ("ICG", 22), ("ADC clock", 5))}
        if inferred_detector:
            for bit, name in enumerate(("phiM", "SH", "ICG")):
                if self.metadata["board_inversion_mask"] & (1 << bit):
                    signals[name] = 1 - signals[name]
        return signals


def packet_size(header: bytes) -> int:
    layout, names = header_layout(header)
    if len(header) < layout.size:
        raise ValueError("Incomplete scope header")
    _, version, _, *fields = layout.unpack_from(header)
    m = dict(zip(names, fields))
    if m["logic_stride"] != 8 or not 2 <= m["logic_count"] <= 8192 or not 0 <= m["adc_count"] <= (4000 if version == 1 else 12000):
        raise ValueError("Invalid diagnostic payload bounds")
    if m["cpu_hz"] != 96_000_000 or m["pin_mapping"] != 1:
        raise ValueError("Unsupported clock or pin mapping")
    if version == 2 and (not 1 <= m["adc_target_count"] <= 12000 or m["adc_count"] > m["adc_target_count"] or m["adc_clock_hz"] != 24_000_000 or m["adc_sample_cycles"] not in (3, 15) or m["adc_resolution_bits"] != 12):
        raise ValueError("Invalid ADC configuration bounds")
    return layout.size + m["logic_count"] * 8 + m["adc_count"] * 2 + 4


def decode(wire: bytes) -> Capture:
    expected = packet_size(wire)
    if len(wire) != expected:
        raise ValueError(f"Capture length {len(wire)} differs from expected {expected}")
    if zlib.crc32(wire[:-4]) != struct.unpack_from("<I", wire, len(wire)-4)[0]:
        raise ValueError("Scope CRC32 mismatch: capture rejected")
    layout, names = header_layout(wire)
    m = dict(zip(names, layout.unpack_from(wire)[3:]))
    m["protocol_version"] = struct.unpack_from("<H", wire, 4)[0]
    logic_end = layout.size + m["logic_count"] * 8
    logic = np.frombuffer(wire, dtype="<u4", count=m["logic_count"]*2, offset=layout.size).reshape(-1, 2).copy()
    adc = np.frombuffer(wire, dtype="<u2", count=m["adc_count"], offset=logic_end).copy()
    if np.any(np.diff(logic[:, 0].astype(np.int64)) <= 0):
        raise ValueError("Logic timestamps are not strictly increasing")
    return Capture(m, logic, adc, wire)


def read_capture(port, mode="fast", timeout=12):
    if mode not in MODES:
        raise ValueError("Unsupported acquisition mode")
    port.reset_input_buffer()
    port.write(f"SCOPE {mode.upper()}\n".encode("ascii"))
    port.flush()
    data = bytearray()
    deadline = time.monotonic() + timeout
    total = None
    while time.monotonic() < deadline:
        part = port.read(min(16384, max(1, (total or HEADER_V2.size) - len(data))))
        if part:
            data.extend(part)
        if total is None:
            offset = data.find(MAGIC)
            if offset < 0:
                if len(data) > 256:
                    if b"CCD1" in data and not mode.startswith("production"):
                        raise RuntimeError("Production CCD1 firmware is running. Flash the scope image first.")
                    del data[:-3]
                continue
            if offset:
                del data[:offset]
            if len(data) >= 8 and len(data) >= header_layout(data)[0].size:
                total = packet_size(data)
        if total is not None and len(data) >= total:
            return decode(bytes(data[:total]))
    raise TimeoutError("No complete scope response. Check COM port, scope firmware and USB connection.")
