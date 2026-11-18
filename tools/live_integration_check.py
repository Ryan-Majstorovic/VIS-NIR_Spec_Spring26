"""Exercise production timing through USB CDC without requiring a CCD.

ADC values from a disconnected input are deliberately not optical evidence.
Run with the repository's Python dependencies available on PYTHONPATH.
"""
import argparse
import json
from pathlib import Path
import statistics
import struct
import time
import zlib

import serial

HEADER = struct.Struct('<4sBBHIHHHHIII')
SHORT = [us for us in range(10, 8001) if 8000 % us == 0]
LONG = [8001, 12500, 32000, 32001, 64001, 100001, 1000000, 5000000]


class Capture:
    def __init__(self, port, output):
        self.port = port
        self.raw = (output / 'usb.ccd1').open('wb')
        self.events = (output / 'events.jsonl').open('w')
        self.buffer = bytearray()
        self.frames = []
        self.lines = []
        self.bad = []
        self.synchronized = False
        self.startup_bytes = 0
        self.start = time.perf_counter()

    def poll(self):
        data = self.port.read(min(65536, max(1, self.port.in_waiting)))
        self.raw.write(data)
        self.buffer.extend(data)
        if not self.synchronized:
            magic = self.buffer.find(b'CCD1')
            if magic < 0:
                discard = max(0, len(self.buffer)-3)
                self.startup_bytes += discard
                del self.buffer[:discard]
                return
            self.startup_bytes += magic
            del self.buffer[:magic]
            self.synchronized = True
        while self.buffer:
            if self.buffer.startswith(b'CCD1'):
                if len(self.buffer) < HEADER.size:
                    break
                h = HEADER.unpack_from(self.buffer)
                size = HEADER.size + h[9] + 4
                if h[1:3] != (3, 1) or h[5:8] != (3694, 32, 3648) or h[9] != 7388 or h[11] != 65537:
                    self.bad.append(list(h[1:]))
                    del self.buffer[0]
                    continue
                if len(self.buffer) < size:
                    break
                if zlib.crc32(self.buffer[:size-4]) != struct.unpack_from('<I', self.buffer, size-4)[0]:
                    self.bad.append({'crc_error': h[4]})
                    del self.buffer[0]
                    continue
                samples = struct.unpack_from('<3694H', self.buffer, HEADER.size)
                frame = dict(t=time.perf_counter()-self.start, id=h[4], us=h[10],
                             flags=h[8], profile=h[11], minimum=min(samples), maximum=max(samples))
                self.frames.append(frame)
                self.events.write(json.dumps(frame)+'\n')
                del self.buffer[:size]
            else:
                newline = self.buffer.find(b'\n')
                magic = self.buffer.find(b'CCD1')
                if magic > 0 and (newline < 0 or magic < newline):
                    self.bad.append({'prefix_hex': self.buffer[:magic].hex()})
                    del self.buffer[:magic]
                elif newline >= 0:
                    line = bytes(self.buffer[:newline]).decode('ascii', errors='replace').strip()
                    self.lines.append(line)
                    self.events.write(json.dumps(dict(t=time.perf_counter()-self.start, line=line))+'\n')
                    del self.buffer[:newline+1]
                else:
                    break

    def wait(self, seconds):
        end = time.monotonic()+seconds
        while time.monotonic() < end:
            self.poll()

    def command(self, wire, expected, timeout):
        start = len(self.lines)
        self.port.write(wire)
        end = time.monotonic()+timeout
        while time.monotonic() < end:
            self.poll()
            if any(line.startswith(expected) for line in self.lines[start:]):
                return self.lines[start:]
        return self.lines[start:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', default='COM3')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--settings', nargs='+', type=int)
    parser.add_argument('--steady-seconds', type=float, default=0.15)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    with serial.Serial(args.port, 115200, timeout=0.02, write_timeout=1) as port:
        capture = Capture(port, args.output)
        try:
            capture.wait(2)
            print('Baseline:', len(capture.frames), 'frames;', len(capture.lines), 'lines', flush=True)
            for us in args.settings or SHORT + LONG + [10, 8000]:
                start = len(capture.frames)
                timeout = 18 if us == 5000000 else 7
                lines = capture.command(f'INTEG {us}\n'.encode(), f'OK INTEG {us} ', timeout)
                capture.wait(max(args.steady_seconds, 2.2*max(us, 8000)/1000000))
                frames = [f for f in capture.frames[start:] if f['us'] == us]
                intervals = [b['t']-a['t'] for a,b in zip(frames, frames[1:])]
                expected = max(us, 8000)/1000000
                median = statistics.median(intervals) if intervals else None
                mean = (frames[-1]['t']-frames[0]['t'])/(len(frames)-1) if len(frames)>1 else None
                result = dict(us=us, responses=lines, frames=len(frames), median_period_s=median,
                              expected_period_s=expected,
                              mean_period_s=mean,
                              missing_ids=sum(b['id']-a['id']-1 for a,b in zip(frames, frames[1:])),
                              ack=any(s.startswith(f'OK INTEG {us} ') for s in lines),
                              flags=sorted(set(f['flags'] for f in frames)))
                results.append(result)
                print(json.dumps(result), flush=True)
                if not result['ack'] or not frames:
                    break
            for wire in [b'INTEG 9\n', b'INTEG 3000\n', b'INTEG 5000001\n',
                         b'INTEG -1\n', b'INTEG 12.5\n', b'INTEG \n', b'BOGUS\n',
                         b'INTEG '+b'9'*60+b'\n']:
                lines = capture.command(wire, 'ERR ', 1)
                results.append(dict(command=wire.decode().strip(), responses=lines))
                print(json.dumps(results[-1]), flush=True)
            capture.wait(2)
        finally:
            capture.raw.close()
            capture.events.close()
            summary = dict(results=results, total_frames=len(capture.frames),
                           malformed=capture.bad, lines=capture.lines,
                           startup_discarded_bytes=capture.startup_bytes,
                           nonmonotonic=sum(b['id'] <= a['id'] for a,b in zip(capture.frames,capture.frames[1:])),
                           adc_out_of_range=sum(f['maximum'] > 4095 for f in capture.frames),
                           final_frame=capture.frames[-1] if capture.frames else None)
            (args.output/'summary.json').write_text(json.dumps(summary, indent=2))
            print('Saved', args.output/'summary.json', flush=True)


if __name__ == '__main__':
    main()
