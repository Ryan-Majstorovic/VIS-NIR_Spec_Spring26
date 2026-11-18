from __future__ import annotations

import struct
import time
import zlib
from datetime import datetime, timezone

import numpy as np

from backend.device.integration import valid_integration
from backend.models.frames import BannerPacket, BinaryFramePacket, DevicePacket, TextLinePacket

# DOC-UUID: 2BD0CC64-CA9B-4886-BE5C-970D86E21283
PACKET_MAGIC = b"CCD1"
PACKET_VERSION = 3
PACKET_TYPE_FRAME = 1
MAX_BINARY_SAMPLE_COUNT = 8192
LEGACY_FRAME_HEADER_STRUCT = struct.Struct("<4sBBHIHHHHI")
FRAME_HEADER_STRUCT = struct.Struct("<4sBBHIHHHHII")
FRAME_V3_HEADER_STRUCT = struct.Struct("<4sBBHIHHHHIII")


def parse_device_line(line: str) -> DevicePacket | None:
    """Purpose: classify one decoded text line. Rationale: firmware banners and diagnostics share the same CDC text channel."""
    cleaned = line.strip()
    if not cleaned:
        return None

    if (
        cleaned.startswith("USB CDC")
        or "TIM2_TRGO" in cleaned
        or "ICG-synchronous" in cleaned
        or "TIM4 update=" in cleaned
    ):
        return BannerPacket(text=cleaned)

    return TextLinePacket(text=cleaned)


def try_parse_binary_frame(buffer: bytes) -> tuple[BinaryFramePacket | None, int]:
    """Purpose: parse one binary frame from a byte buffer. Rationale: packet rebuilding needs both the parsed frame and consumed length."""
    if len(buffer) < LEGACY_FRAME_HEADER_STRUCT.size:
        return None, 0

    (
        magic,
        version,
        packet_type,
        _reserved,
        frame_id,
        sample_count,
        effective_start,
        effective_count,
        flags,
        payload_bytes,
    ) = LEGACY_FRAME_HEADER_STRUCT.unpack_from(buffer)

    if magic != PACKET_MAGIC:
        return None, 1

    if version not in (1, 2, 3) or packet_type != PACKET_TYPE_FRAME:
        return None, 1

    if version >= 2:
        if len(buffer) < FRAME_HEADER_STRUCT.size:
            return None, 0
        if not valid_integration(struct.unpack_from("<I", buffer, 24)[0]):
            return None, 1

    if sample_count <= 0 or sample_count > MAX_BINARY_SAMPLE_COUNT:
        return None, 1

    expected_payload_bytes = sample_count * 2
    if payload_bytes != expected_payload_bytes:
        return None, 1

    header_size = {1: 24, 2: 28, 3: 32}[version]
    if effective_start + effective_count > sample_count:
        return None, 1
    total_bytes = header_size + payload_bytes + (4 if version == 3 else 0)
    if len(buffer) < total_bytes:
        return None, 0

    if version == 3 and zlib.crc32(buffer[:total_bytes - 4]) != struct.unpack_from("<I", buffer, total_bytes - 4)[0]:
        return None, 1
    payload = memoryview(buffer)[header_size:header_size + payload_bytes]
    adc_counts = np.frombuffer(payload, dtype="<u2", count=sample_count).copy()
    if np.any(adc_counts > 4095):
        return None, 1
    timestamp_ns = time.time_ns()

    return (
        BinaryFramePacket(
            frame_counter=frame_id,
            integration_us=struct.unpack_from("<I", buffer, 24)[0] if version >= 2 else None,
            timing_profile_id=struct.unpack_from("<I", buffer, 28)[0] if version == 3 else None,
            sample_count=sample_count,
            effective_start=effective_start,
            effective_count=effective_count,
            flags=flags,
            adc_counts=adc_counts,
            timestamp_ns=timestamp_ns,
            timestamp=datetime.fromtimestamp(timestamp_ns / 1_000_000_000.0, timezone.utc),
        ),
        total_bytes,
    )
