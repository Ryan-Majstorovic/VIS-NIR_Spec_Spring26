from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime, timezone
import logging
from pathlib import Path
import queue
import threading
from time import perf_counter

from backend.core.performance_monitor import PerformanceMonitor
from backend.core.session_manager import SessionManager
from backend.core.state_manager import StateManager
from backend.device.base_transport import BaseTransport
from backend.device.packet_reader import DeviceStreamReader
from backend.device.protocol import encode_raw_command
from backend.models.config import CalibrationConfig, UserConfig, ensure_pixel_mode_without_mapping
from backend.models.frames import BannerPacket, BinaryFramePacket, TextLinePacket
from backend.models.status import CommandResult, ConnectionState, RecordingStatus
from backend.processing.calibration_manager import CalibrationManager
from backend.processing.spectrum_builder import SpectrumBuilder
from backend.storage.binary_capture import DenseBinaryRecorder, DenseFrameProcessor, export_hdf5_to_csv


DEFAULT_LIVE_DISPLAY_FPS = 30.0


class CommandService:
    """Purpose: coordinate transport, parsing, state updates, and user commands. Rationale: one service keeps the data path organized."""
    def __init__(
        self,
        *,
        state_manager: StateManager,
        session_manager: SessionManager,
        transport: BaseTransport,
        calibration_manager: CalibrationManager,
        spectrum_builder: SpectrumBuilder,
        binary_export_dir: Path,
        performance_monitor: PerformanceMonitor | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Purpose: wire the command layer to its dependencies. Rationale: incoming device data and UI actions share one coordinator."""
        self._state_manager = state_manager
        self._session_manager = session_manager
        self._transport = transport
        self._calibration_manager = calibration_manager
        self._spectrum_builder = spectrum_builder
        self._binary_export_dir = binary_export_dir
        self._packet_reader = DeviceStreamReader()
        self._last_frame_id: int | None = None
        self._last_frame_arrival_s: float | None = None
        self._last_display_frame_s: float | None = None
        self._last_chunk_arrival_s: float | None = None
        self._frame_size_warning_emitted = False
        self._expected_sample_count = state_manager.get_user_config().device.sample_count
        self._live_display_interval_s = self._display_interval_from_config(state_manager.get_user_config())
        self._incoming_bytes: queue.Queue[tuple[bytes, float] | None] = queue.Queue()
        self._binary_recorder: DenseBinaryRecorder | None = None
        self._binary_processor: DenseFrameProcessor | None = None
        self._last_binary_recording_path: Path | None = None
        self._last_binary_csv_path: Path | None = None
        self._binary_failure_reported = False
        self._last_recording_status_publish_s = 0.0
        self._performance_monitor = performance_monitor
        self._logger = logger or logging.getLogger(__name__)
        self._processor_thread = threading.Thread(
            target=self._processing_loop,
            name="device-packet-processor",
            daemon=True,
        )
        self._processor_thread.start()
        self._transport.set_callbacks(
            on_bytes=self._handle_bytes,
            on_state=self._handle_transport_state,
        )

    def list_serial_ports(self) -> list[dict[str, str]]:
        """Purpose: return visible serial ports. Rationale: the UI should ask the service, not the transport, directly."""
        return self._transport.list_ports()

    def connect(self, port: str | None = None) -> CommandResult:
        """Purpose: open the device connection. Rationale: connect logic must reset parser state and update app status consistently."""
        config = self._state_manager.get_user_config()
        selected_port = port or config.serial.port
        self._packet_reader.reset()
        self._clear_pending_bytes()
        self._last_frame_id = None
        self._last_frame_arrival_s = None
        self._last_display_frame_s = None
        self._last_chunk_arrival_s = None
        self._frame_size_warning_emitted = False

        if not selected_port:
            ports = self.list_serial_ports()
            if not ports:
                return CommandResult(ok=False, message="No serial ports found.")
            selected_port = ports[0]["device"]

        try:
            self._transport.connect(
                port=selected_port,
                timeout_s=config.serial.timeout_s,
            )
        except Exception as exc:
            self._logger.exception("Failed to connect to serial device.")
            self._state_manager.set_connection_state(
                ConnectionState.error,
                port=selected_port,
                error=str(exc),
                message="Connection failed.",
            )
            self._state_manager.append_log(f"Connection failed: {exc}")
            return CommandResult(ok=False, message=str(exc))

        config.serial.port = selected_port
        self._state_manager.set_user_config(config)
        self._state_manager.set_connection_state(
            ConnectionState.connected,
            port=selected_port,
            message=f"Connected to {selected_port}.",
        )
        self._state_manager.reset_frame_tracking()
        self._state_manager.append_log(f"Connected to {selected_port}.")
        return CommandResult(ok=True, message=f"Connected to {selected_port}.")

    def disconnect(self) -> CommandResult:
        """Purpose: close the device connection and clear live frame state. Rationale: disconnects should leave the app in a clean state."""
        if self._binary_recorder is not None and self._binary_recorder.status()["active"]:
            self.stop_binary_recording()
        self._transport.disconnect()
        self._packet_reader.reset()
        self._clear_pending_bytes()
        self._last_frame_id = None
        self._last_frame_arrival_s = None
        self._last_display_frame_s = None
        self._last_chunk_arrival_s = None
        self._frame_size_warning_emitted = False
        self._state_manager.reset_frame_tracking()
        self._state_manager.set_connection_state(
            ConnectionState.disconnected,
            message="Disconnected.",
        )
        self._state_manager.append_log("Disconnected from spectrometer.")
        return CommandResult(ok=True, message="Disconnected.")

    def send_raw_command(self, command_text: str) -> CommandResult:
        """Purpose: send a text command to the device. Rationale: command writes should use the same service path as other actions."""
        cleaned = command_text.strip()
        if not cleaned:
            return CommandResult(ok=False, message="Command text is empty.")

        if not self._transport.is_connected():
            return CommandResult(ok=False, message="Device is not connected.")

        self._transport.write(encode_raw_command(cleaned))
        self._state_manager.append_log(f"TX > {cleaned}")
        return CommandResult(
            ok=True,
            message=(
                "Command sent over USB CDC. Device-side command handling depends on "
                "the active STM32 firmware."
            ),
        )

    def apply_user_config(self, config: UserConfig) -> None:
        """Purpose: apply new user settings to the running app. Rationale: config edits should immediately update dependent services."""
        self._state_manager.set_user_config(config)
        self._spectrum_builder.update_device_config(config.device)
        self._session_manager.set_max_frames(config.ui.max_session_frames)
        self._expected_sample_count = config.device.sample_count
        self._live_display_interval_s = self._display_interval_from_config(config)
        self._frame_size_warning_emitted = False
        self._state_manager.set_session_status(self._session_manager.status())
        self._state_manager.append_log("User configuration updated.")

    def apply_calibration_config(self, config: CalibrationConfig) -> None:
        """Purpose: apply new calibration settings. Rationale: calibration changes should flow through one controlled update point."""
        normalized_config = ensure_pixel_mode_without_mapping(config)
        self._calibration_manager.update_config(normalized_config)
        self._state_manager.set_calibration_config(normalized_config)
        latest_spectrum = self._state_manager.latest_spectrum()
        if latest_spectrum is not None:
            self._state_manager.set_last_spectrum(
                self._spectrum_builder.rebuild_live_frame(latest_spectrum)
            )
        self._state_manager.append_log("Calibration configuration updated.")

    def refresh_session_status(self) -> None:
        """Purpose: push the latest session summary into shared state. Rationale: UI reads should come from StateManager snapshots."""
        self._state_manager.set_session_status(self._session_manager.status())
        self._publish_recording_status()

    def start_binary_recording(self, path: Path | None = None) -> CommandResult:
        """Purpose: start full-rate dense HDF5 recording. Rationale: binary capture is the authoritative storage path."""
        if self._binary_recorder is not None and self._binary_recorder.status()["active"]:
            return CommandResult(ok=False, message="Binary recording is already running.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_path = Path(path) if path is not None else self._binary_export_dir / f"spectrometer_capture_{timestamp}.h5"
        try:
            config = self._state_manager.get_user_config()
            self._binary_processor = DenseFrameProcessor(config.device, self._calibration_manager.config)
            self._binary_recorder = DenseBinaryRecorder(
                output_path,
                self._binary_processor.static_data,
                self._binary_processor.metadata_attributes(),
            )
            self._binary_recorder.start()
        except Exception as exc:
            self._binary_recorder = None
            self._binary_processor = None
            self._state_manager.set_recording_status(
                RecordingStatus(
                    failed=True,
                    path=str(output_path),
                    last_path=str(self._last_binary_recording_path) if self._last_binary_recording_path else None,
                    last_csv_path=str(self._last_binary_csv_path) if self._last_binary_csv_path else None,
                    error=str(exc),
                )
            )
            self._state_manager.append_log(f"Binary recording failed to start: {exc}")
            return CommandResult(ok=False, message=f"Binary recording failed to start: {exc}")

        self._last_binary_recording_path = output_path
        self._binary_failure_reported = False
        self._last_recording_status_publish_s = 0.0
        self._publish_recording_status()
        self._state_manager.append_log(f"Started binary recording: {output_path}")
        return CommandResult(ok=True, message=f"Started binary recording: {output_path}")

    def stop_binary_recording(self) -> CommandResult:
        """Purpose: stop dense HDF5 recording and flush queued frames. Rationale: the file should be complete before conversion."""
        if self._binary_recorder is None:
            return CommandResult(ok=False, message="No binary recording is running.")

        self._binary_recorder.stop()
        status = self._binary_recorder.status()
        self._publish_recording_status()
        if status["failed"]:
            message = f"Binary recording stopped after failure: {status['failure_message']}"
            self._state_manager.append_log(message)
            return CommandResult(ok=False, message=message)

        message = f"Binary recording stopped: {status['frame_count']} frames written to {self._binary_recorder.path}"
        self._state_manager.append_log(message)
        return CommandResult(ok=True, message=message)

    def convert_last_binary_recording_to_csv(self) -> CommandResult:
        """Purpose: export the last dense HDF5 recording to CSV. Rationale: CSV should be generated only from stored binary arrays."""
        if self._binary_recorder is not None and self._binary_recorder.status()["active"]:
            return CommandResult(ok=False, message="Stop binary recording before converting it to CSV.")
        if self._last_binary_recording_path is None:
            return CommandResult(ok=False, message="No binary recording has been created yet.")

        try:
            csv_path = export_hdf5_to_csv(self._last_binary_recording_path)
        except Exception as exc:
            self._state_manager.append_log(f"Binary CSV conversion failed: {exc}")
            return CommandResult(ok=False, message=f"Binary CSV conversion failed: {exc}")

        self._last_binary_csv_path = csv_path
        self._publish_recording_status()
        self._state_manager.append_log(f"Converted binary recording to CSV: {csv_path}")
        return CommandResult(ok=True, message=f"Converted binary recording to CSV: {csv_path}")

    @staticmethod
    def _display_interval_from_config(config: UserConfig) -> float:
        live_display_fps = getattr(config.ui, "live_display_fps", DEFAULT_LIVE_DISPLAY_FPS)
        return 1.0 / max(float(live_display_fps), 1.0)

    def _display_frame_due(self, now_s: float) -> bool:
        if self._last_display_frame_s is None:
            self._last_display_frame_s = now_s
            return True
        if (now_s - self._last_display_frame_s) < self._live_display_interval_s:
            return False
        self._last_display_frame_s = now_s
        return True

    def _publish_recording_status(self) -> None:
        self._last_recording_status_publish_s = perf_counter()
        recorder_status = self._binary_recorder.status() if self._binary_recorder is not None else {}
        self._state_manager.set_recording_status(
            RecordingStatus(
                active=bool(recorder_status.get("active", False)),
                failed=bool(recorder_status.get("failed", False)),
                frame_count=int(recorder_status.get("frame_count", 0)),
                queue_depth=int(recorder_status.get("queue_depth", 0)),
                path=recorder_status.get("path"),
                last_path=str(self._last_binary_recording_path) if self._last_binary_recording_path else None,
                last_csv_path=str(self._last_binary_csv_path) if self._last_binary_csv_path else None,
                error=recorder_status.get("failure_message"),
            )
        )

    def _append_binary_record(self, packet: BinaryFramePacket) -> None:
        if self._binary_recorder is None or self._binary_processor is None:
            return
        current_status = self._binary_recorder.status()
        if current_status["failed"]:
            if not self._binary_failure_reported:
                self._binary_failure_reported = True
                self._state_manager.append_log(f"Binary recording failed: {current_status['failure_message']}")
                self._publish_recording_status()
            return
        if not current_status["active"]:
            return

        monitor = self._performance_monitor
        try:
            with (
                monitor.measure("backend.binary_dense_process")
                if monitor is not None
                else nullcontext()
            ):
                record = self._binary_processor.build_record(packet)
            with (
                monitor.measure("backend.binary_queue_append")
                if monitor is not None
                else nullcontext()
            ):
                accepted = self._binary_recorder.append(record)
        except Exception as exc:
            self._binary_recorder.fail(str(exc))
            accepted = False

        if monitor is not None:
            status = self._binary_recorder.status()
            monitor.record_value("backend.binary_queue_depth", status["queue_depth"])
            monitor.record_value("backend.binary_frames_written", status["frame_count"])

        if not accepted and not self._binary_failure_reported:
            self._binary_failure_reported = True
            status = self._binary_recorder.status()
            self._state_manager.append_log(f"Binary recording failed: {status['failure_message']}")
            self._publish_recording_status()
            return
        if (perf_counter() - self._last_recording_status_publish_s) >= 0.5:
            self._publish_recording_status()

    def _handle_transport_state(self, state: ConnectionState, detail: str | None) -> None:
        """Purpose: mirror transport state changes into app state. Rationale: the UI should react to connection events consistently."""
        if state == ConnectionState.error:
            self._state_manager.set_connection_state(
                ConnectionState.error,
                error=detail,
                message=detail,
            )
            if detail:
                self._state_manager.append_log(f"Transport error: {detail}")
            return

        if state == ConnectionState.disconnected:
            self._last_frame_id = None
            self._last_frame_arrival_s = None
            self._last_display_frame_s = None
            self._last_chunk_arrival_s = None

        self._state_manager.set_connection_state(state, message=detail)
        if detail:
            self._state_manager.append_log(detail)

    def _handle_bytes(self, data: bytes) -> None:
        """Purpose: enqueue raw device bytes. Rationale: the serial reader thread should stay light and avoid heavy parsing work."""
        if data:
            payload = bytes(data)
            chunk_arrival_s = perf_counter()
            self._incoming_bytes.put_nowait((payload, chunk_arrival_s))
            monitor = self._performance_monitor
            if monitor is not None:
                if self._last_chunk_arrival_s is not None:
                    monitor.record_value(
                        "transport.read_chunk_interval_ms",
                        (chunk_arrival_s - self._last_chunk_arrival_s) * 1000.0,
                    )
                monitor.increment("transport.bytes_in", len(payload))
                monitor.increment("transport.read_chunks")
                monitor.record_value("transport.read_chunk_bytes", len(payload))
                monitor.record_value("backend.bytes_queue_depth", self._incoming_bytes.qsize())
            self._last_chunk_arrival_s = chunk_arrival_s

    def _processing_loop(self) -> None:
        """Purpose: turn queued bytes into packets on a worker thread. Rationale: parsing and frame handling should not block serial reads."""
        while True:
            pending = self._incoming_bytes.get()
            if pending is None:
                return
            data, enqueued_at_s = pending
            monitor = self._performance_monitor
            if monitor is not None:
                monitor.record_value("backend.bytes_queue_wait_ms", (perf_counter() - enqueued_at_s) * 1000.0)
                monitor.record_value("backend.bytes_queue_depth", self._incoming_bytes.qsize())
                monitor.record_value("backend.packet_parse_input_bytes", len(data))
            with (
                monitor.measure("backend.packet_parse")
                if monitor is not None
                else nullcontext()
            ):
                packets = self._packet_reader.feed(data)
            if monitor is not None:
                monitor.record_value("backend.packets_per_chunk", len(packets))
                frame_packets = sum(1 for packet in packets if isinstance(packet, BinaryFramePacket))
                if frame_packets > 0:
                    monitor.record_value("backend.frames_per_chunk", frame_packets)
            for packet in packets:
                self._process_packet(packet)

    def _process_packet(self, packet: BannerPacket | TextLinePacket | BinaryFramePacket) -> None:
        """Purpose: apply one parsed packet to the app state. Rationale: each packet type affects the app differently but through one path."""
        if isinstance(packet, BannerPacket):
            self._state_manager.add_firmware_message(packet.text)
            self._state_manager.append_log(packet.text)
            return

        if isinstance(packet, TextLinePacket):
            self._state_manager.append_log(packet.text)
            return

        if isinstance(packet, BinaryFramePacket):
            monitor = self._performance_monitor
            with (
                monitor.measure("backend.frame_process")
                if monitor is not None
                else nullcontext()
            ):
                full_frame_process_start_s = perf_counter()
                arrival_time_s = perf_counter()
                if monitor is not None:
                    monitor.increment("backend.frames_processed")
                    if self._last_frame_arrival_s is not None:
                        monitor.record_value(
                            "backend.frame_interval_ms",
                            (arrival_time_s - self._last_frame_arrival_s) * 1000.0,
                        )
                self._last_frame_arrival_s = arrival_time_s
                if (
                    packet.sample_count != self._expected_sample_count
                    and not self._frame_size_warning_emitted
                ):
                    self._frame_size_warning_emitted = True
                    self._state_manager.append_log(
                        "Received a frame-size mismatch from the device: "
                        f"got {packet.sample_count} samples, expected {self._expected_sample_count}. "
                        "Check the active firmware and device layout settings."
                    )

                missed_frames = 0
                if self._last_frame_id is not None and packet.frame_counter > self._last_frame_id + 1:
                    missed_frames = packet.frame_counter - self._last_frame_id - 1
                    if monitor is not None:
                        monitor.increment("backend.frames_missed", missed_frames)
                    self._state_manager.append_log(
                        f"Missed {missed_frames} frame(s) before frame {packet.frame_counter}."
                    )

                self._last_frame_id = packet.frame_counter
                self._state_manager.update_from_frame(packet, missed_frames=missed_frames)
                self._append_binary_record(packet)
                if monitor is not None:
                    monitor.increment("backend.full_frames_processed")
                    monitor.record_duration("backend.full_frame_process", perf_counter() - full_frame_process_start_s)
                    monitor.record_value("backend.full_frame_sample_count", packet.sample_count)
                if not self._display_frame_due(arrival_time_s):
                    if monitor is not None:
                        monitor.increment("backend.display_frame_throttle_skips")
                    return

                display_frame_process_start_s = perf_counter()
                spectrum = self._spectrum_builder.build_from_frame(packet)
                self._state_manager.set_last_spectrum(spectrum)
                self._session_manager.append_frame(spectrum)
                session_status = self._session_manager.status()
                self._state_manager.set_session_status(session_status)
                if monitor is not None:
                    monitor.increment("backend.display_frames_processed")
                    monitor.record_duration("backend.display_frame_process", perf_counter() - display_frame_process_start_s)
                    monitor.record_value("backend.session_frames_buffered", session_status.frames_buffered)
                    monitor.record_value("backend.session_dropped_frames", session_status.dropped_frames)

    def _clear_pending_bytes(self) -> None:
        """Purpose: empty the queued raw-byte backlog. Rationale: reconnects should not process stale bytes from an old session."""
        while True:
            try:
                pending = self._incoming_bytes.get_nowait()
            except queue.Empty:
                return
            if pending is None:
                self._incoming_bytes.put_nowait(None)
                return
