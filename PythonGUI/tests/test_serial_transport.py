from __future__ import annotations

import multiprocessing
import os
import queue
import threading
import unittest
from unittest.mock import patch

import serial

from backend.device.serial_transport import SerialTransport
from backend.device.serial_worker import run_serial_worker


class _FakeSerial:
    def __init__(self, *, port: str, baudrate: int, timeout: float) -> None:
        if port == "busy":
            raise serial.SerialException("Port is busy")
        self._timeout = timeout
        self._ready = threading.Condition()
        self._buffer = bytearray(f"{os.getpid()}\n".encode())

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        pass

    @property
    def in_waiting(self) -> int:
        with self._ready:
            return len(self._buffer)

    def read(self, size: int) -> bytes:
        with self._ready:
            self._ready.wait_for(lambda: bool(self._buffer), timeout=self._timeout)
            chunk = bytes(self._buffer[:size])
            del self._buffer[:size]
            return chunk

    def write(self, payload: bytes) -> None:
        with self._ready:
            self._buffer.extend(payload)
            self._ready.notify()

    def flush(self) -> None:
        pass


def _run_with_fake_serial(*args) -> None:
    with patch("backend.device.serial_worker.serial.Serial", new=_FakeSerial):
        run_serial_worker(*args)


class SerialTransportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.transport = SerialTransport()
        self.addCleanup(self.transport.disconnect)
        worker = patch("backend.device.serial_transport.run_serial_worker", new=_run_with_fake_serial)
        worker.start()
        self.addCleanup(worker.stop)

    def test_worker_commands_and_stream_survive_a_blocked_receiver(self) -> None:
        receiving = threading.Event()
        release = threading.Event()
        received: queue.Queue[bytes] = queue.Queue()
        self.addCleanup(release.set)

        def handle_bytes(chunk: bytes) -> None:
            receiving.set()
            release.wait(timeout=5)
            received.put(chunk)

        self.transport.set_callbacks(on_bytes=handle_bytes)
        self.transport.connect(port="fake")
        self.assertTrue(receiving.wait(timeout=5))
        self.transport.write(b"first\n")
        self.transport.write(b"second\n")
        release.set()

        stream = bytearray()
        while stream.count(b"\n") < 3:
            stream.extend(received.get(timeout=5))
        worker_pid, first, second = stream.splitlines()
        self.assertNotEqual(int(worker_pid), os.getpid())
        self.assertEqual((first, second), (b"first", b"second"))

        self.transport.disconnect()
        self.assertFalse(self.transport.is_connected())
        self.assertNotIn(int(worker_pid), [process.pid for process in multiprocessing.active_children()])

    def test_open_error_leaves_transport_ready_to_retry(self) -> None:
        with self.assertRaisesRegex(serial.SerialException, "Port is busy"):
            self.transport.connect(port="busy")
        self.assertFalse(self.transport.is_connected())
        self.transport.connect(port="fake")
        self.assertTrue(self.transport.is_connected())

    def test_worker_closes_cleanly_when_command_pipe_closes(self) -> None:
        context = multiprocessing.get_context("spawn")
        control, worker_control = context.Pipe()
        stream, worker_stream = context.Pipe(duplex=False)
        process = context.Process(
            target=_run_with_fake_serial,
            args=("fake", 115200, 0.05, worker_control, worker_stream),
        )
        with control, stream, worker_control, worker_stream:
            process.start()
            try:
                worker_control.close()
                worker_stream.close()
                self.assertTrue(control.poll(5))
                self.assertIsNone(control.recv())
                self.assertTrue(stream.poll(5))
                self.assertEqual(int(stream.recv()), process.pid)
                control.close()
                process.join(timeout=2)
                self.assertEqual(process.exitcode, 0)
            finally:
                if process.is_alive():
                    process.terminate()
                    process.join()
                process.close()
