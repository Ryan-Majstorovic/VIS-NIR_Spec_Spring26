"""Track device-confirmed integration changes without substituting requested metadata."""
from collections.abc import Callable
from threading import RLock, Timer

from backend.device.integration import frame_interval_us, valid_integration
from backend.models.status import CommandResult


class IntegrationControl:
    def __init__(self, transport, state_manager):
        self.transport = transport
        self.state = state_manager
        self.lock = RLock()
        self.pending_us = None
        self.ack = None
        self.latest_frame = None
        self.timer = None
        self.generation = 0
        self._on_applied: Callable[[int], None] | None = None

    def request(self, us: int, *, on_applied: Callable[[int], None] | None = None) -> CommandResult:
        with self.lock:
            if not valid_integration(us):
                return CommandResult(ok=False, message="Unsupported integration time.")
            if self.pending_us is not None:
                return CommandResult(ok=False, message="An integration change is already pending.")
            if not self.transport.is_connected():
                return CommandResult(ok=False, message="Device is not connected.")
            current = self.state.snapshot(include_spectrum=False).device.integration_us or 10
            self.pending_us, self.ack = us, None
            self._on_applied = on_applied
            self.latest_frame = None
            self.state.set_integration_status("Pending", "Waiting for a complete exposure at the new setting.", us)
            # A request can arrive just after the old long exposure began.
            timeout = (frame_interval_us(current) + 2 * frame_interval_us(us)) / 1_000_000 + 1
            self.generation += 1
            self.timer = Timer(timeout, self._timeout, args=(self.generation,))
            self.timer.daemon = True
            try:
                self.transport.write(f"INTEG {us}\n".encode("ascii"))
            except Exception as exc:
                self._finish("Error", str(exc))
                return CommandResult(ok=False, message=str(exc))
            if self.pending_us is not None:
                self.timer.start()
            return CommandResult(ok=True, message=f"Requested {us} µs; awaiting device confirmation.")

    def receive_text(self, text: str) -> None:
        with self.lock:
            if text.startswith("ERR INTEG TIMING"):
                self._finish("Fault", "Device timing fault; valid acquisition stopped.")
            elif self.pending_us is not None and text.startswith("ERR INTEG "):
                self._finish("Error", text)
            elif self.pending_us is not None and text.startswith("OK INTEG "):
                fields = text.split()
                if len(fields) == 4 and fields[2].isdigit() and fields[3].isdigit():
                    if int(fields[2]) == self.pending_us:
                        self.ack = (int(fields[2]), int(fields[3]))
                        self._confirm()

    def receive_frame(self, frame) -> None:
        with self.lock:
            if frame.flags & 2:
                self._finish("Fault", "Frame reports a timing fault.")
                return
            self.latest_frame = (frame.integration_us, frame.frame_counter)
            if (self.pending_us is None and frame.integration_us is not None and
                    self.state.snapshot(include_spectrum=False).device.integration_state == "Unknown"):
                self.state.set_integration_status("Applied", f"Device reports {frame.integration_us} µs.")
            self._confirm()

    def _confirm(self) -> None:
        if self.ack is not None and self.latest_frame is not None:
            us, frame_id = self.latest_frame
            if us == self.ack[0] and frame_id >= self.ack[1]:
                on_applied = self._on_applied
                self._finish("Applied", f"Applied {us} µs; frame {frame_id} confirmed.")
                if on_applied is not None:
                    on_applied(us)

    def _timeout(self, generation=None) -> None:
        with self.lock:
            if self.pending_us is not None and (generation is None or generation == self.generation):
                self._finish("Timeout", "Integration confirmation timed out; requested metadata was not applied.")

    def reset(self) -> None:
        with self.lock:
            self._finish("Unknown", "Waiting for device timing metadata.")
            self.latest_frame = None

    def _finish(self, status: str, message: str) -> None:
        if self.timer is not None:
            self.timer.cancel()
        self.timer = None
        self.pending_us, self.ack = None, None
        self._on_applied = None
        self.state.set_integration_status(status, message)
