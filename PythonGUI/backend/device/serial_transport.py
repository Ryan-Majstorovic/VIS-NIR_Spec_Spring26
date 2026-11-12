from __future__ import annotations

import multiprocessing
import threading
from dataclasses import dataclass, field
from multiprocessing.connection import Connection
from multiprocessing.process import BaseProcess

import serial
from serial.tools import list_ports

from backend.device.base_transport import BaseTransport
from backend.device.serial_worker import run_serial_worker
from backend.models.status import ConnectionState


@dataclass
class _SerialSession:
    process: BaseProcess
    control: Connection
    stream: Connection
    stop: threading.Event = field(default_factory=threading.Event)
    finished: threading.Event = field(default_factory=threading.Event)
    receiver: threading.Thread | None = None

    def stop_worker(self) -> None:
        self.stop.set()
        self.control.close()
        if self.process.pid is not None:
            self.process.join(timeout=0.5)
            if self.process.is_alive():
                self.process.terminate()
                self.process.join()
        self.process.close()


class SerialTransport(BaseTransport):
    """Forward device bytes and commands between the app and the COM worker."""

    def __init__(self) -> None:
        super().__init__()
        self._context = multiprocessing.get_context("spawn")
        self._session: _SerialSession | None = None
        self._write_lock = threading.Lock()

    def connect(
        self,
        *,
        port: str | None = None,
        baudrate: int = 115200,
        timeout_s: float = 0.1,
    ) -> None:
        if self._session is not None:
            self.disconnect()

        selected_port = port
        if not selected_port:
            ports = self.list_ports()
            if not ports:
                raise RuntimeError("No serial ports found.")
            selected_port = ports[0]["device"]

        self._emit_state(ConnectionState.connecting, f"Opening {selected_port}...")
        control, worker_control = self._context.Pipe()
        stream, worker_stream = self._context.Pipe(duplex=False)
        process = self._context.Process(
            target=run_serial_worker,
            args=(selected_port, baudrate, timeout_s, worker_control, worker_stream),
            name="serial-acquisition",
            daemon=True,
        )
        session = _SerialSession(process, control, stream)
        try:
            with worker_control, worker_stream:
                process.start()
            if not control.poll(10):
                raise serial.SerialTimeoutException(f"Timed out opening {selected_port}.")
            error = control.recv()
            if error is not None:
                raise serial.SerialException(error)
        except BaseException:
            stream.close()
            session.stop_worker()
            raise

        self._session = session
        session.receiver = threading.Thread(
            target=self._receive, args=(session,), name="serial-receiver", daemon=True,
        )
        self._emit_state(ConnectionState.connected, f"Connected to {selected_port}.")
        session.receiver.start()

    def disconnect(self) -> None:
        with self._write_lock:
            session = self._session
            self._session = None
            if session is not None:
                session.stop_worker()
        if session is not None and session.receiver is not threading.current_thread():
            if session.receiver is not None:
                session.receiver.join(timeout=0.5)
        self._emit_state(ConnectionState.disconnected, "Serial connection closed.")

    def write(self, payload: bytes) -> None:
        with self._write_lock:
            session = self._session
            if session is None or session.stop.is_set() or session.finished.is_set():
                raise serial.SerialException("Serial port is not connected.")
            try:
                session.control.send_bytes(payload)
                if not session.control.poll(2):
                    raise serial.SerialTimeoutException("Serial worker did not confirm the write.")
                error = session.control.recv()
            except (EOFError, OSError) as exc:
                session.stop.set()
                session.control.close()
                failure = serial.SerialException(str(exc) or "Serial worker stopped during a write.")
            else:
                if error is not None:
                    raise serial.SerialException(error)
                return
        if self._session is session:
            self._emit_state(ConnectionState.error, str(failure))
        raise failure

    def is_connected(self) -> bool:
        session = self._session
        return session is not None and not session.stop.is_set() and not session.finished.is_set()

    def list_ports(self) -> list[dict[str, str]]:
        return [
            {"device": port.device, "description": port.description or "", "hwid": port.hwid or ""}
            for port in sorted(list_ports.comports(), key=lambda port: port.device)
        ]

    def _receive(self, session: _SerialSession) -> None:
        error = "Serial acquisition worker stopped."
        try:
            with session.stream:
                while not session.stop.is_set():
                    item = session.stream.recv()
                    if isinstance(item, str):
                        error = item
                        break
                    if not session.stop.is_set():
                        self._emit_bytes(item)
        except (EOFError, OSError):
            pass
        finally:
            session.finished.set()
            if not session.stop.is_set() and self._session is session:
                self._emit_state(ConnectionState.error, error)
