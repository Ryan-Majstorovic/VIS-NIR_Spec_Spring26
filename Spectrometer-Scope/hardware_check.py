"""Repeat real USB acquisitions and retain integrity and timing evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import serial
from scope import HERE, save_capture, source_label
from scope_protocol import decode, read_capture
from scope_validate import validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default="COM3")
    args = parser.parse_args()
    # Refresh earlier reports after analyzer improvements; original wire bytes
    # remain unchanged and can always be independently reanalyzed.
    for file in (HERE / "captures").glob("*.cscp"):
        capture = decode(file.read_bytes())
        report = validate(capture)
        report.update(source=source_label(capture), metadata=capture.metadata)
        file.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    captures = []
    with serial.Serial(args.port, 115200, timeout=0.15, write_timeout=1) as port:
        for mode in ("fast", "corrected", "slow", "fastoverview", "correctedoverview", "exposed", "exposedoverview", "exposed"):
            capture = read_capture(port, mode)
            path, report = save_capture(capture, HERE / "captures")
            checks = {c["name"]: c for c in report["checks"]}
            if any(checks[k]["status"] != "PASS" for k in ("Capture integrity", "ADC DMA", "ADC range", "ADC conversion budget", "ADC capture duration")):
                raise RuntimeError(f"Hardware acquisition failed: {path}")
            summary = {"path": str(path.relative_to(HERE)), "mode": mode, "capture_id": capture.metadata["capture_id"],
                       "sha256": hashlib.sha256(capture.wire).hexdigest(),
                       "logic_samples": len(capture.logic), "adc_samples": len(capture.adc),
                       "checks": {name: {"status": item["status"], "value": item["value"]} for name,item in checks.items()}}
            captures.append(summary)
            print(mode, capture.metadata["capture_id"], f"CRC PASS; ADC {len(capture.adc)}/{capture.metadata['adc_target_count']}; timing:",
                  {k:v["status"] for k,v in checks.items() if k.startswith(("t1", "t2", "t3", "t4", "Master", "ADC clock"))})
    result = {"utc": datetime.now(timezone.utc).isoformat(), "port": args.port,
              "usb_integrity_and_adc_check": "PASS", "sensor_pin_validation": "UNVERIFIED", "captures": captures}
    output = HERE / "captures/hardware-validation.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
