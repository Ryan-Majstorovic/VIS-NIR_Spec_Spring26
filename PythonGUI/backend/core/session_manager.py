from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from backend.core.performance_monitor import PerformanceMonitor
from backend.models.frames import SpectrogramHistoryFrame, SpectrumFrame
from backend.models.status import SessionStatus


DEFAULT_MAX_SPECTROGRAM_HISTORY_FRAMES = 3072


def utc_now() -> datetime:
    """Purpose: return the current UTC time. Rationale: session timestamps should use one shared helper."""
    return datetime.now(timezone.utc)


class SessionManager:
    """Keep recent full frames for bias capture and compact rows for the spectrogram."""
    def __init__(
        self,
        *,
        max_frames: int = 2000,
        max_spectrogram_frames: int = DEFAULT_MAX_SPECTROGRAM_HISTORY_FRAMES,
        performance_monitor: PerformanceMonitor | None = None,
    ) -> None:
        self._lock = Lock()
        self._max_frames = max_frames
        self._frames: deque[SpectrumFrame] = deque(maxlen=max_frames)
        self._max_spectrogram_frames = max_spectrogram_frames
        self._spectrogram_frames: deque[SpectrogramHistoryFrame] = deque(maxlen=max_spectrogram_frames)
        self._performance_monitor = performance_monitor
        self._session_id = self._new_session_id()
        self._started_at = utc_now()
        self._dropped_frames = 0

    @staticmethod
    def _new_session_id() -> str:
        """Create a short identifier for the current live session."""
        return uuid4().hex[:8]

    def set_max_frames(self, max_frames: int) -> None:
        """Purpose: resize the rolling frame buffer. Rationale: buffer depth may change without discarding the newest useful data."""
        with self._lock:
            current_frames = list(self._frames)[-max_frames:]
            if len(self._frames) > max_frames:
                self._dropped_frames += len(self._frames) - max_frames
            self._max_frames = max_frames
            self._frames = deque(current_frames, maxlen=max_frames)

    def set_max_spectrogram_frames(self, max_frames: int) -> None:
        """Resize the compact spectrogram history for longer rolling time windows."""
        with self._lock:
            current_frames = list(self._spectrogram_frames)[-max_frames:]
            self._max_spectrogram_frames = max_frames
            self._spectrogram_frames = deque(current_frames, maxlen=max_frames)

    def append_frame(self, frame: SpectrumFrame) -> None:
        """Purpose: add one frame to the session buffer. Rationale: capture history should roll forward automatically during streaming."""
        monitor = self._performance_monitor
        with self._lock:
            if len(self._frames) == self._frames.maxlen:
                self._dropped_frames += 1
                if monitor is not None:
                    monitor.increment("backend.session_frame_overwrites")
            self._frames.append(frame)
            if frame.spectrogram_row:
                if len(self._spectrogram_frames) == self._spectrogram_frames.maxlen and monitor is not None:
                    monitor.increment("backend.spectrogram_history_overwrites")
                self._spectrogram_frames.append(
                    SpectrogramHistoryFrame(
                        frame_id=frame.frame_id,
                        timestamp=frame.timestamp,
                        spectrogram_row=frame.spectrogram_row,
                    )
                )

    def frames(self) -> list[SpectrumFrame]:
        """Purpose: return buffered frames. Rationale: callers should get a copy rather than direct access to the deque."""
        with self._lock:
            return list(self._frames)

    def spectrogram_frames(self) -> list[SpectrogramHistoryFrame]:
        """Purpose: return compact spectrogram-history rows. Rationale: the rolling heatmap needs longer time coverage without forcing the full raw-frame buffer to grow dramatically."""
        with self._lock:
            return list(self._spectrogram_frames)

    def status(self) -> SessionStatus:
        """Purpose: summarize the current session buffer. Rationale: the UI needs lightweight session metadata during refresh."""
        with self._lock:
            return SessionStatus(
                session_id=self._session_id,
                started_at=self._started_at,
                frames_buffered=len(self._frames),
                dropped_frames=self._dropped_frames,
            )
