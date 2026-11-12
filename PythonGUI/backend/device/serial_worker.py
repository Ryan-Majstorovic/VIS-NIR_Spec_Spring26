from __future__ import annotations

from multiprocessing.connection import Connection
from queue import Empty, Full, Queue
from threading import Event, Thread

import serial


# USB typically delivers several chunks per frame. Keep a bounded backlog so a
# busy GUI cannot immediately block COM reads or grow memory without a limit.
RECEIVE_QUEUE_SIZE = 4096
MAX_READ_BYTES = 65536


def _read_port(port: serial.Serial, incoming: Queue[bytes | str], stop: Event) -> None:
    try:
        while not stop.is_set():
            chunk = port.read(max(1, min(port.in_waiting, MAX_READ_BYTES)))
            if chunk:
                incoming.put_nowait(chunk)
        return
    except Full:
        error = "Serial receive backlog filled. Reconnect to resume acquisition."
    except OSError as exc:
        error = str(exc)
    if not stop.is_set():
        incoming.put(error)


def _write_commands(port: serial.Serial, control: Connection, stop: Event) -> None:
    try:
        while not stop.is_set():
            if not control.poll(0.05):
                continue
            payload = control.recv_bytes()
            try:
                port.write(payload)
                port.flush()
            except OSError as exc:
                control.send(str(exc))
            else:
                control.send(None)
    except (EOFError, OSError):
        stop.set()


def run_serial_worker(
    port_name: str,
    baudrate: int,
    timeout_s: float,
    control: Connection,
    stream: Connection,
) -> None:
    """Own the COM handle and buffer reads independently of the desktop process."""
    with control, stream:
        try:
            port = serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout_s)
        except (OSError, ValueError) as exc:
            control.send(str(exc))
            return

        with port:
            # Closing the parent end of the command pipe signals shutdown. The
            # serial loop only checks this worker-local event between reads.
            stop = Event()
            incoming: Queue[bytes | str] = Queue(maxsize=RECEIVE_QUEUE_SIZE)
            Thread(target=_read_port, args=(port, incoming, stop), daemon=True).start()
            control.send(None)
            Thread(target=_write_commands, args=(port, control, stop), daemon=True).start()
            try:
                while not stop.is_set():
                    try:
                        item = incoming.get(timeout=0.05)
                    except Empty:
                        continue
                    stream.send(item)
                    if isinstance(item, str):
                        break
            except (EOFError, OSError):
                return
