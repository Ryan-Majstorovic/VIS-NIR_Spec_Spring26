"""Validate the running production image without replacing it with diagnostic firmware."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'PythonGUI'))
import serial
from backend.device.packet_reader import DeviceStreamReader
from backend.models.frames import BinaryFramePacket
from scope import save_capture
from scope_protocol import ADC_TRIGGER_INTERNAL, read_capture


def set_integration(port, us, profile):
    reader = DeviceStreamReader()
    port.write(f'INTEG {us}\n'.encode())
    deadline = time.monotonic() + 18
    ack = frame = False
    while time.monotonic() < deadline:
        for packet in reader.feed(port.read(max(1, min(port.in_waiting, 65536)))):
            if isinstance(packet, BinaryFramePacket):
                frame |= packet.integration_us == us and packet.timing_profile_id == profile
            elif packet.text.startswith(f'OK INTEG {us} '):
                ack = True
            elif packet.text.startswith('ERR '):
                raise RuntimeError(packet.text)
        if ack and frame:
            return
    raise TimeoutError(f'No confirmed production integration {us}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', default='COM3')
    parser.add_argument('--profile', type=lambda value: int(value, 0), default=0x00010002)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    with serial.Serial(args.port, 115200, timeout=0.02, write_timeout=1) as port:
        for us, mode in [(100, 'production'), (100, 'productionoverview'), (10, 'production'),
                         (8000, 'production'), (8001, 'production'), (32001, 'production'),
                         (100001, 'production'), (5000000, 'production'), (100, 'production')]:
            set_integration(port, us, args.profile)
            trace = read_capture(port, mode, timeout=18)
            path, report = save_capture(trace, args.output)
            checks = {item['name']: item for item in report['checks']}
            required = ['Capture integrity', 'ADC DMA', 'ADC range', 'ADC conversion budget', 'ADC capture duration']
            if mode == 'production':
                required += ['Master clock target', 't1 ICG rise after SH fall', 't2 ICG fall to SH rise',
                             't3 SH high width', 'ADC clock output', 'ADC / master clock ratio']
                if args.profile == 0x00010001:
                    required.append('ADC trigger start')
            else:
                required += ['ICG readout high window']
            expected_internal = args.profile != 0x00010001
            internal = bool(trace.metadata['flags'] & ADC_TRIGGER_INTERNAL)
            passed = internal == expected_internal and all(checks[name]['status'] == 'PASS' for name in required) and not report['has_failures']
            result = dict(integration_us=us, mode=mode, passed=passed, path=str(path.resolve()),
                          sha256=hashlib.sha256(trace.wire).hexdigest(),
                          checks={name: {'status': item['status'], 'value': item['value']} for name, item in checks.items()})
            results.append(result)
            print(json.dumps({'us': us, 'mode': mode, 'passed': passed,
                              'unmet': {name: checks[name]['value'] for name in required if checks[name]['status'] != 'PASS'}}), flush=True)
    summary = dict(utc=datetime.now(timezone.utc).isoformat(), port=args.port, production_profile=args.profile,
                   passed=all(r['passed'] for r in results), sensor_pin_validation='UNVERIFIED', captures=results)
    (args.output/'production-validation.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return 0 if summary['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
