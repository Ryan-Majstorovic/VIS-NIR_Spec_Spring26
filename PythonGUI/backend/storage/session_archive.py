from __future__ import annotations

import io
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable
from zipfile import ZIP_DEFLATED, ZipFile

from backend.storage.binary_capture import DEFAULT_CHUNK_FRAMES, FORMAT_VERSION, require_h5py, write_frame_csv


ARCHIVE_VERSION = "vis-nir-session-v1"
LEGACY_FORMATS = {"dense-hdf5-v1", "dense-hdf5-v2", "dense-hdf5-v3"}
CORRECTION_DATASETS = ("qe_correction", "system_response_correction", "correction_factor_applied")


def _known_timing(value: Any) -> int | None:
    return int(value) or None


def _frame_ranges(
    frames: Any,
    frame_count: int,
    fields: dict[str, tuple[Callable[[Any], Any], Any]],
) -> list[dict[str, Any]]:
    datasets = {name: frames.get(name) for name in fields}
    if any(dataset is not None and dataset.shape != (frame_count,) for dataset in datasets.values()):
        raise ValueError("Recording contains misaligned frame metadata.")

    ranges: list[dict[str, Any]] = []
    previous = None
    for start in range(0, frame_count, DEFAULT_CHUNK_FRAMES):
        stop = min(start + DEFAULT_CHUNK_FRAMES, frame_count)
        columns = {
            name: dataset[start:stop] if dataset is not None else None
            for name, dataset in datasets.items()
        }
        for offset in range(stop - start):
            current = {
                name: convert(columns[name][offset]) if columns[name] is not None else missing
                for name, (convert, missing) in fields.items()
            }
            if current != previous:
                frame_index = start + offset
                if ranges:
                    ranges[-1]["end_frame_index"] = frame_index
                ranges.append({"start_frame_index": frame_index, "end_frame_index": frame_count, **current})
                previous = current
    return ranges


def _calibration_manifest(handle: Any, frame_count: int) -> dict[str, Any]:
    version = handle.attrs.get("format_version")
    frames = handle["frame"]
    if version == FORMAT_VERSION:
        for name in ("calibration_revision", "integration_us", "timing_profile_id", "dark_calibration_applied"):
            if name not in frames:
                raise ValueError(f"Recording is missing frame metadata: {name}.")
        snapshots = [
            {
                "calibration_revision": int(name),
                "config": json.loads(revision["config_json"].asstr()[()]),
                "wavelength_nm": revision["wavelength_nm"][:].tolist(),
                **{key: revision[key][:].tolist() for key in CORRECTION_DATASETS},
            }
            for name, revision in handle["calibration/revisions"].items()
        ]
        snapshots.sort(key=lambda snapshot: snapshot["calibration_revision"])
    elif version in LEGACY_FORMATS:
        snapshots = [{
            "calibration_revision": 0,
            "config": json.loads(handle.attrs["calibration_config_json"]),
            "wavelength_nm": handle["pixel/wavelength_nm"][:].tolist(),
            **{key: handle[f"correction/{key}"][:].tolist() for key in CORRECTION_DATASETS},
        }]
    else:
        raise ValueError(f"Unsupported recording format: {version!r}.")

    calibration_ranges = _frame_ranges(frames, frame_count, {
        "calibration_revision": (int, 0),
        "dark_calibration_applied": (bool, None),
    })
    if {entry["calibration_revision"] for entry in calibration_ranges} != {
        snapshot["calibration_revision"] for snapshot in snapshots
    }:
        raise ValueError("Recording contains mismatched calibration revisions.")

    return {
        "format_version": ARCHIVE_VERSION,
        "recording_format_version": version,
        "frame_count": frame_count,
        "device_config": json.loads(handle.attrs["device_config_json"]),
        "sample_indices": handle["pixel/sample_index"][:].tolist(),
        "calibrations": snapshots,
        "calibration_ranges": calibration_ranges,
        "timing_ranges": _frame_ranges(frames, frame_count, {
            "integration_us": (_known_timing, None),
            "timing_profile_id": (_known_timing, None),
        }),
    }


def export_session_archive(
    hdf5_path: Path,
    output_path: Path | None = None,
    *,
    on_progress: Callable[[int], None] | None = None,
) -> Path:
    """Export a completed recording to a ZIP without changing the source."""
    source = Path(hdf5_path)
    output = Path(output_path) if output_path is not None else source.with_suffix(".zip")
    if output.resolve() == source.resolve():
        raise ValueError("ZIP output must differ from the source recording.")
    h5 = require_h5py()
    with NamedTemporaryFile(prefix=".session-export-", suffix=".tmp", dir=output.parent, delete=False) as file:
        pending = Path(file.name)

    percent = 0

    def report_frames(written: int) -> None:
        nonlocal percent
        next_percent = min(99, 100 * written // frame_count)
        if next_percent > percent:
            percent = next_percent
            if on_progress is not None:
                on_progress(percent)

    try:
        with h5.File(source, "r") as handle:
            frame_count = len(handle["frame/frame_id"])
            if not frame_count:
                raise ValueError("The binary recording contains no frames.")
            manifest = _calibration_manifest(handle, frame_count)
            with ZipFile(pending, "w", compression=ZIP_DEFLATED, compresslevel=1) as archive:
                with archive.open("frames.csv", "w", force_zip64=True) as entry:
                    with io.TextIOWrapper(entry, encoding="utf-8", newline="") as csv_file:
                        write_frame_csv(handle, csv_file, on_frames_written=report_frames if on_progress else None)
                archive.writestr("calibration.json", json.dumps(manifest, indent=2, allow_nan=False) + "\n")
        pending.replace(output)
    finally:
        pending.unlink(missing_ok=True)
    if on_progress is not None:
        on_progress(100)
    return output
