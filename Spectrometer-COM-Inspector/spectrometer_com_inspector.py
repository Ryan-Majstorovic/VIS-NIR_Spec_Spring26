from __future__ import annotations

import argparse
import struct
import sys
import time
from dataclasses import dataclass

try:
    import serial
    from serial import SerialException
    from serial.tools import list_ports
except ImportError:  # pragma: no cover - kept simple so missing dependency is obvious at runtime.
    serial = None
    SerialException = Exception
    list_ports = None


# User-adjustable defaults. USB CDC ignores the baud electrically, but pyserial
# still wants a value when opening the virtual COM port.
DEFAULT_PORT = "COM4"
DEFAULT_BAUDRATE = 115200
DEFAULT_TIMEOUT_S = 0.1
DEFAULT_REPORT_INTERVAL_S = 1.0
DEFAULT_READ_SIZE = 65536
ACCEPTANCE_MIN_FPS = 124.0
ACCEPTANCE_SAMPLE_COUNT = 3694
ACCEPTANCE_FLAGS = 0x0001

# Current STM32 CCD1 frame format. The little-endian layout mirrors the packed
# C header: magic, version, type, reserved, frame_id, geometry, flags, payload.
# DOC-UUID: C6B4929A-5CFB-46E8-A592-FD75E67ED745
PACKET_MAGIC = b"CCD1"
PACKET_VERSION = 1
PACKET_TYPE_FRAME = 1
FRAME_HEADER = struct.Struct("<4sBBHIHHHHI")
MAX_BINARY_SAMPLE_COUNT = 8192
RESYNC_BUFFER_LIMIT = 1024


@dataclass
class StreamStats:
    bytes_seen: int = 0
    frames_seen: int = 0
    missed_frames: int = 0
    bad_sync_bytes: int = 0
    text_lines_seen: int = 0
    last_frame_id: int | None = None
    last_sample_count: int | None = None
    last_effective_start: int | None = None
    last_effective_count: int | None = None
    last_flags: int | None = None


class Ccd1FrameCounter:
    def __init__(self) -> None:
        self.stats = StreamStats()
        self._buffer = bytearray()

    def feed(self, data: bytes) -> None:
        self.stats.bytes_seen += len(data)
        self._buffer.extend(data)

        while self._buffer:
            if self._buffer.startswith(PACKET_MAGIC):
                if not self._try_consume_frame():
                    break
                continue

            newline_index = self._buffer.find(b"\n")
            magic_index = self._buffer.find(PACKET_MAGIC)

            if newline_index >= 0 and (magic_index < 0 or newline_index < magic_index):
                del self._buffer[: newline_index + 1]
                self.stats.text_lines_seen += 1
                continue

            if magic_index > 0:
                self.stats.bad_sync_bytes += magic_index
                del self._buffer[:magic_index]
                continue

            if len(self._buffer) > RESYNC_BUFFER_LIMIT:
                # Keep three bytes because a valid four-byte magic may be split
                # across serial reads; discarding more would lose possible "CCD".
                discarded = len(self._buffer) - 3
                del self._buffer[:discarded]
                self.stats.bad_sync_bytes += discarded
            break

    def _try_consume_frame(self) -> bool:
        if len(self._buffer) < FRAME_HEADER.size:
            return False

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
        ) = FRAME_HEADER.unpack_from(self._buffer)

        if (
            magic != PACKET_MAGIC
            or version != PACKET_VERSION
            or packet_type != PACKET_TYPE_FRAME
            or sample_count == 0
            or sample_count > MAX_BINARY_SAMPLE_COUNT
            or payload_bytes != sample_count * 2
        ):
            del self._buffer[:1]
            self.stats.bad_sync_bytes += 1
            return True

        total_frame_bytes = FRAME_HEADER.size + payload_bytes
        if len(self._buffer) < total_frame_bytes:
            return False

        del self._buffer[:total_frame_bytes]
        self._record_frame(
            frame_id=frame_id,
            sample_count=sample_count,
            effective_start=effective_start,
            effective_count=effective_count,
            flags=flags,
        )
        return True

    def _record_frame(
        self,
        *,
        frame_id: int,
        sample_count: int,
        effective_start: int,
        effective_count: int,
        flags: int,
    ) -> None:
        if self.stats.last_frame_id is not None and frame_id > self.stats.last_frame_id + 1:
            self.stats.missed_frames += frame_id - self.stats.last_frame_id - 1

        self.stats.frames_seen += 1
        self.stats.last_frame_id = frame_id
        self.stats.last_sample_count = sample_count
        self.stats.last_effective_start = effective_start
        self.stats.last_effective_count = effective_count
        self.stats.last_flags = flags


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count CCD1 spectrometer frames arriving on a USB CDC COM port."
    )
    parser.add_argument("--port", default=DEFAULT_PORT, help=f"COM port to inspect. Default: {DEFAULT_PORT}")
    parser.add_argument("--baudrate", type=int, default=DEFAULT_BAUDRATE, help=f"Serial baudrate. Default: {DEFAULT_BAUDRATE}")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S, help=f"Serial read timeout in seconds. Default: {DEFAULT_TIMEOUT_S}")
    parser.add_argument("--interval", type=float, default=DEFAULT_REPORT_INTERVAL_S, help=f"Report interval in seconds. Default: {DEFAULT_REPORT_INTERVAL_S}")
    parser.add_argument("--read-size", type=int, default=DEFAULT_READ_SIZE, help=f"Maximum bytes to request per serial read. Default: {DEFAULT_READ_SIZE}")
    parser.add_argument("--duration", type=float, default=None, help="Stop after this many seconds and print a summary.")
    parser.add_argument("--require-125fps", action="store_true", help="Exit nonzero unless a duration run meets the 125 fps acceptance checks.")
    parser.add_argument("--list", action="store_true", help="List serial ports and exit.")
    return parser.parse_args()


def require_pyserial() -> None:
    if serial is not None and list_ports is not None:
        return

    print("pyserial is required. Install it with:", file=sys.stderr)
    print("  python -m pip install -r Spectrometer-COM-Inspector/requirements.txt", file=sys.stderr)
    raise SystemExit(1)


def list_serial_ports() -> None:
    require_pyserial()
    ports = sorted(list_ports.comports(), key=lambda item: item.device)
    if not ports:
        print("No serial ports found.")
        return

    for port in ports:
        description = port.description or ""
        hwid = port.hwid or ""
        print(f"{port.device:8} {description} {hwid}".rstrip())


def format_optional_int(value: int | None) -> str:
    return "-" if value is None else str(value)


def format_optional_hex(value: int | None) -> str:
    return "-" if value is None else f"0x{value:04X}"


def print_report(counter: Ccd1FrameCounter, previous: StreamStats, previous_time: float) -> tuple[StreamStats, float]:
    now = time.monotonic()
    elapsed_s = max(now - previous_time, 1e-9)
    current = counter.stats

    interval_frames = current.frames_seen - previous.frames_seen
    interval_bytes = current.bytes_seen - previous.bytes_seen

    # USB CDC read chunks do not align to frames, so the live rate is based on
    # completed frames divided by elapsed wall time for the reporting interval.
    frames_per_second = interval_frames / elapsed_s
    bytes_per_second = interval_bytes / elapsed_s

    print(
        f"{time.strftime('%H:%M:%S')} | "
        f"+{interval_frames:4d} frames/{elapsed_s:4.1f}s "
        f"({frames_per_second:6.1f} fps) | "
        f"total={current.frames_seen} | "
        f"last_id={format_optional_int(current.last_frame_id)} | "
        f"missed={current.missed_frames} | "
        f"flags={format_optional_hex(current.last_flags)} | "
        f"samples={format_optional_int(current.last_sample_count)} | "
        f"bad_sync={current.bad_sync_bytes} | "
        f"{bytes_per_second / 1_000_000:5.2f} MB/s"
    )
    return StreamStats(**vars(current)), now


def print_summary(counter: Ccd1FrameCounter, started_at: float, *, require_125fps: bool) -> int:
    elapsed_s = max(time.monotonic() - started_at, 1e-9)
    stats = counter.stats
    overall_fps = stats.frames_seen / elapsed_s
    overall_mbps = stats.bytes_seen / elapsed_s / 1_000_000

    print(
        "Summary | "
        f"elapsed={elapsed_s:0.1f}s | "
        f"fps={overall_fps:0.1f} | "
        f"total={stats.frames_seen} | "
        f"last_id={format_optional_int(stats.last_frame_id)} | "
        f"missed={stats.missed_frames} | "
        f"flags={format_optional_hex(stats.last_flags)} | "
        f"samples={format_optional_int(stats.last_sample_count)} | "
        f"bad_sync={stats.bad_sync_bytes} | "
        f"{overall_mbps:0.2f} MB/s"
    )

    if not require_125fps:
        return 0

    passed = (
        overall_fps >= ACCEPTANCE_MIN_FPS
        and stats.missed_frames == 0
        and stats.bad_sync_bytes == 0
        and stats.last_sample_count == ACCEPTANCE_SAMPLE_COUNT
        and stats.last_flags == ACCEPTANCE_FLAGS
    )
    print("Acceptance: PASS" if passed else "Acceptance: FAIL")
    return 0 if passed else 1


def inspect_port(args: argparse.Namespace) -> int:
    require_pyserial()
    counter = Ccd1FrameCounter()

    print(f"Opening {args.port} at {args.baudrate} baud. Press Ctrl+C to stop.")
    with serial.Serial(port=args.port, baudrate=args.baudrate, timeout=args.timeout) as ser:
        previous = StreamStats()
        started_at = time.monotonic()
        previous_time = started_at
        next_report_time = started_at + args.interval
        stop_time = started_at + args.duration if args.duration is not None else None

        while True:
            chunk = ser.read(max(1, args.read_size))
            if chunk:
                counter.feed(chunk)

            now = time.monotonic()
            if now >= next_report_time:
                previous, previous_time = print_report(counter, previous, previous_time)
                next_report_time = now + args.interval
            if stop_time is not None and now >= stop_time:
                return print_summary(counter, started_at, require_125fps=args.require_125fps)


def main() -> int:
    args = parse_args()
    if args.list:
        list_serial_ports()
        return 0

    try:
        return inspect_port(args)
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    except SerialException as exc:
        print(f"Serial error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
