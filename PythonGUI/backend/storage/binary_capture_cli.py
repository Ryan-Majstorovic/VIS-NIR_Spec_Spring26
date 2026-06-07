from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from time import perf_counter, time_ns

import numpy as np

from backend.device.packet_reader import DeviceStreamReader
from backend.device.protocol import FRAME_HEADER_STRUCT, PACKET_MAGIC, PACKET_TYPE_FRAME, PACKET_VERSION
from backend.models.config import CalibrationConfig, DeviceConfig
from backend.models.frames import BinaryFramePacket
from backend.storage.binary_capture import (
    DEFAULT_CHUNK_FRAMES,
    DenseBinaryRecorder,
    DenseFrameProcessor,
    export_hdf5_to_csv,
    inspect_hdf5,
)


def _build_synthetic_packet_bytes(frame_id: int, adc_counts: np.ndarray) -> bytes:
    payload = np.asarray(adc_counts, dtype="<u2").tobytes()
    header = FRAME_HEADER_STRUCT.pack(
        PACKET_MAGIC,
        PACKET_VERSION,
        PACKET_TYPE_FRAME,
        0,
        int(frame_id),
        int(adc_counts.size),
        32,
        max(int(adc_counts.size) - 46, 0),
        0x0001,
        len(payload),
    )
    return header + payload


def run_benchmark(path: Path, *, frames: int, sample_count: int, target_fps: float) -> int:
    device_config = DeviceConfig(sample_count=sample_count)
    processor = DenseFrameProcessor(device_config, CalibrationConfig())
    recorder = DenseBinaryRecorder(
        path,
        processor.static_data,
        processor.metadata_attributes(),
        chunk_frames=DEFAULT_CHUNK_FRAMES,
    )
    reader = DeviceStreamReader()
    rng = np.random.default_rng(125)
    max_queue_depth = 0

    recorder.start()
    started_s = perf_counter()
    for frame_id in range(frames):
        adc_counts = rng.integers(0, 4096, size=sample_count, dtype=np.uint16)
        packets = reader.feed(_build_synthetic_packet_bytes(frame_id, adc_counts))
        for packet in packets:
            if isinstance(packet, BinaryFramePacket):
                recorder.append(processor.build_record(packet))
        max_queue_depth = max(max_queue_depth, recorder.queue_depth())
    recorder.stop()
    elapsed_s = max(perf_counter() - started_s, 1e-9)
    observed_fps = frames / elapsed_s
    status = recorder.status()

    print(
        "Benchmark | "
        f"frames={frames} | samples={sample_count} | elapsed={elapsed_s:.3f}s | "
        f"rate={observed_fps:.1f} fps | max_queue_depth={max_queue_depth} | path={path}"
    )
    if status["failed"]:
        print(f"FAIL: {status['failure_message']}")
        return 1
    if observed_fps < target_fps:
        print(f"FAIL: below target {target_fps:.1f} fps")
        return 1
    print("PASS")
    return 0


def print_validation(path: Path) -> int:
    report = inspect_hdf5(path)
    print(f"File: {report['path']}")
    print(f"Frames: {report['frame_count']}")
    print(f"Frame ID gaps: {report['frame_id_gaps']} gaps, {report['missing_frame_ids']} missing IDs")
    for name in sorted(report["datasets"]):
        item = report["datasets"][name]
        print(f"{name}: shape={item['shape']} dtype={item['dtype']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dense binary capture tools for VIS-NIR spectrometer HDF5 files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert = subparsers.add_parser("convert", help="Convert a dense HDF5 capture to long-table CSV.")
    convert.add_argument("hdf5_path", type=Path)
    convert.add_argument("--csv", type=Path, default=None, help="Output CSV path. Defaults to the HDF5 path with .csv suffix.")
    convert.add_argument("--chunk-frames", type=int, default=DEFAULT_CHUNK_FRAMES)

    validate = subparsers.add_parser("validate", help="Inspect dense HDF5 datasets, dtypes, and frame ID gaps.")
    validate.add_argument("hdf5_path", type=Path)

    benchmark = subparsers.add_parser("benchmark", help="Run a synthetic parse + dense processing + HDF5 write benchmark.")
    benchmark.add_argument("--frames", type=int, default=1250)
    benchmark.add_argument("--sample-count", type=int, default=3694)
    benchmark.add_argument("--target-fps", type=float, default=125.0)
    benchmark.add_argument("--output", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "convert":
        output_path = export_hdf5_to_csv(args.hdf5_path, args.csv, chunk_frames=args.chunk_frames)
        print(f"CSV written: {output_path}")
        return 0
    if args.command == "validate":
        return print_validation(args.hdf5_path)
    if args.command == "benchmark":
        if args.output is not None:
            return run_benchmark(args.output, frames=args.frames, sample_count=args.sample_count, target_fps=args.target_fps)
        with tempfile.TemporaryDirectory(prefix=f"vis_nir_benchmark_{time_ns()}_") as temp_dir:
            return run_benchmark(
                Path(temp_dir) / "synthetic_dense_capture.h5",
                frames=args.frames,
                sample_count=args.sample_count,
                target_fps=args.target_fps,
            )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
