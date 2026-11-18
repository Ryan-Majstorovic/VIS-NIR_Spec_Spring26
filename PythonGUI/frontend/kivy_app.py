from __future__ import annotations

import sys
from bisect import bisect_left
from collections import deque
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from math import ceil, hypot, isfinite
from pathlib import Path
from threading import Thread
from time import perf_counter
from typing import Callable, Literal, Sequence

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Mesh, Rectangle, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, ColorProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
import numpy as np

from decimal import Decimal, InvalidOperation
from backend.device.integration import UNIT_US, adjacent_settings, parse_duration, frame_interval_us
from backend.core.runtime import AppRuntime
from backend.models.config import (
    CalibrationConfig,
    CursorConfig,
    DEFAULT_LIVE_DISPLAY_FPS,
    DEFAULT_SATURATION_CAPTURE_FRAME_COUNT,
    DEFAULT_WAVELENGTH_COEFFICIENTS,
    PixelMappingPoint,
    SpectralResponsePoint,
    ensure_pixel_mode_without_mapping,
    has_saved_wavelength_mapping,
)
from backend.models.frames import SpectrogramHistoryFrame, SpectrumFrame
from backend.models.status import CommandResult, ConnectionState, DeviceStatus
from backend.processing.wavelength_map import indices_to_wavelengths
from frontend.choice_widgets import AppSpinner, RadioChoices, SettingSwitch
from frontend.spectrum_markers import (
    MarkerSelection, directional_extremum, global_extremum, marker_delta, marker_value, nearest_index, search_origin,
)
from frontend.tooltips import TooltipController
from frontend.windows_dialogs import choose_session_zip_path

# Shared layout metrics.
# Format:
# - `*_GAP`, `*_PAD`, `*_HEIGHT`, `*_WIDTH` use Kivy `dp(...)` units so the UI
#   keeps roughly the same physical sizing across displays.
APP_GAP = dp(12)
CARD_GAP = dp(8)
CARD_PAD = dp(12)
CONTROL_HEIGHT = dp(38)
BUTTON_HEIGHT = dp(40)
INFO_LABEL_HEIGHT = dp(24)
SMALL_LABEL_HEIGHT = dp(56)
AXIS_COLUMN_WIDTH = dp(28)
Y_AXIS_TICK_INTERVAL = 0.1
Y_AXIS_TICK_COUNT = int(round(1.0 / Y_AXIS_TICK_INTERVAL)) + 1
X_AXIS_HEIGHT = dp(20)
X_AXIS_TICK_COUNT = 10
MAXIMIZED_AXIS_COLUMN_WIDTH = dp(34)
MAXIMIZED_X_AXIS_HEIGHT = dp(24)
WINDOWED_PLOT_AXIS_SPACING = dp(6)
MAXIMIZED_PLOT_AXIS_SPACING = dp(8)
MAXIMIZED_WINDOW_WIDTH_RATIO = 0.96
MAXIMIZED_WINDOW_HEIGHT_RATIO = 0.90
PLOT_DISPLAY_MODE_WINDOWED = "windowed"
PLOT_DISPLAY_MODE_MAXIMIZED = "maximized"
SWITCH_ROW_HEIGHT = dp(32)
PLOT_AXIS_GAP = dp(0)
PLOT_HORIZONTAL_INNER_PAD = dp(0)
PLOT_VERTICAL_INNER_PAD = dp(0)
PLOT_MIN_DRAW_SIZE = dp(24)
NARROW_CONTROL_HEIGHT = dp(34)
NARROW_BUTTON_HEIGHT = dp(36)
NARROW_INFO_LABEL_HEIGHT = dp(34)
NARROW_SMALL_LABEL_HEIGHT = dp(88)
NARROW_SWITCH_ROW_HEIGHT = dp(52)
BUTTON_TEXT_PAD_X = dp(10)
BUTTON_TEXT_PAD_Y = dp(6)

# Main layout proportions and breakpoints.
# Format:
# - ratio values are fractional shares of available space and should usually add
#   up to about 1.0 for sibling containers.
# - `RESPONSIVE_BREAKPOINT` is the window width where the app switches from a
#   side-by-side layout to a stacked layout.
SIDEBAR_RATIO_WIDE = 0.28
DETAIL_RATIO_WIDE = 0.72
LOG_RATIO_WIDE = 0.25
RESPONSIVE_BREAKPOINT = dp(1200)
COMPACT_BREAKPOINT = dp(900)
SHORT_HEIGHT_BREAKPOINT = dp(760)
VERY_SHORT_HEIGHT_BREAKPOINT = dp(620)
BUTTON_STACK_BREAKPOINT = dp(430)
LARGE_DISPLAY_RESPONSIVE_WIDTH_RATIO = 0.55

# UI refresh timing.
# Format:
# - values ending in `_S` are seconds.
# - values ending in `_HZ` are refresh-rate caps in updates per second.
MIN_WIDE_STATUS_REFRESH_S = 0.1
MAX_PLOT_REFRESH_HZ = 30.0
MAX_SPECTROGRAM_REFRESH_HZ = 10.0
PLOT_REFRESH_STALE_S = 0.25

# Responsive-only fallback sizes.
# Format:
# - these are used when the layout is forced into the narrow stacked mode.
NARROW_LOG_CARD_HEIGHT = dp(220)
NOTICE_MIN_TEXT_WIDTH = dp(200)

# Plot rendering controls.
# Format:
# - vertex counts are plain integers.
# - line widths are canvas stroke widths in pixels.
PLOT_CHUNK_MAX_VERTICES = 384
PLOT_LINE_WIDTH = 1.2
PLOT_BORDER_WIDTH = 1.0
PLOT_CORNER_RADIUS = 16
GUIDE_LINE_WIDTH = 1.0
PLOT_CURSOR_DRAG_COOLDOWN_S = 0.10
SPECTROGRAM_MAX_COLUMNS = 256
SPECTROGRAM_MAX_ROWS = 256
SPECTROGRAM_Y_GRID_COUNT = 5
SPECTROGRAM_COLUMN_PEAK_BLEND = 0.15
SPECTROGRAM_TIME_ROW_PEAK_BLEND = 0.15
SPECTROGRAM_TIME_WINDOW_OPTIONS_S = (2.0, 5.0, 10.0, 20.0)
MIN_SPECTROGRAM_TIME_WINDOW_S = 1.0
MAX_SPECTROGRAM_TIME_WINDOW_S = max(SPECTROGRAM_TIME_WINDOW_OPTIONS_S)

LIVE_GRAPH_MODE_SPECTRUM = "spectrum"
LIVE_GRAPH_MODE_SPECTROGRAM = "spectrogram"

# Theme colors.
# Format:
# - RGBA tuples use normalized floats from 0.0 to 1.0 in the order
#   `(red, green, blue, alpha)`.
CARD_BACKGROUND_RGBA = (0.97, 0.95, 0.90, 0.96)
APP_BACKGROUND_RGBA = (1.0, 0.995, 0.975, 1.0)
APP_SURROUND_BACKGROUND_RGBA = (0.0, 0.0, 0.0, 1.0)
CARD_BORDER_RGBA = (0.82, 0.78, 0.69, 1.0)
GUIDE_LINE_RGBA = (0.82, 0.86, 0.82, 0.8)
PLOT_LINE_RGBA = (0.06, 0.46, 0.43, 1.0)
ACCENT_RED_RGB = (0.72, 0.19, 0.17)
PLOT_CURSOR_RGBA = (*ACCENT_RED_RGB, 0.95)
PLOT_MARKER_COLORS = (
    PLOT_CURSOR_RGBA,
    (0.28, 0.24, 0.65, 0.95),
    (0.68, 0.38, 0.08, 0.95),
    (0.02, 0.44, 0.33, 0.95),
)
HIGH_CONTRAST_MARKER_COLORS = (
    (0.06, 0.09, 0.13, 1.0),
    (0.00, 0.34, 0.61, 1.0),
    (0.54, 0.18, 0.00, 1.0),
    (0.49, 0.11, 0.40, 1.0),
)
CURSOR_POINT_RADII = {"small": 3, "standard": 4, "large": 6}
CURSOR_READOUT_FONT_SIZES = {"small": 11, "standard": 12, "large": 15}
TEXT_PRIMARY_RGBA = (0.13, 0.19, 0.24, 1.0)
TEXT_SECONDARY_RGBA = (0.16, 0.20, 0.24, 1.0)
TEXT_TERTIARY_RGBA = (0.28, 0.32, 0.36, 1.0)
NOTICE_RGBA = (0.17, 0.21, 0.26, 1.0)
DARK_INTEGRATION_WARNING_RGBA = (1.0, 0.88, 0.45, 1.0)
SATURATION_WARNING_RGBA = (1.0, 0.84, 0.82, 1.0)
BUTTON_BACKGROUND_RGBA = (0.06, 0.46, 0.43, 1.0)
STOP_RECORDING_BUTTON_BACKGROUND_RGBA = (*ACCENT_RED_RGB, 1.0)
BUTTON_TEXT_RGBA = (1.0, 1.0, 1.0, 1.0)
DESTRUCTIVE_BUTTON_BACKGROUND_RGBA = (0.61, 0.15, 0.14, 1.0)
CALIBRATION_SUCCESS_RGBA = (0.53, 0.89, 0.62, 1.0)
CALIBRATION_ERROR_RGBA = (1.0, 0.76, 0.71, 1.0)
MARKER_CLICK_SLOP = dp(3)

# Shared typography.
TITLE_FONT_SP = 24
SECTION_TITLE_FONT_SP = 18
BODY_FONT_SP = 14
SMALL_FONT_SP = 12
AXIS_FONT_SP = 11
COMPACT_TITLE_FONT_SP = 20
COMPACT_SECTION_TITLE_FONT_SP = 16
COMPACT_BODY_FONT_SP = 12
COMPACT_SMALL_FONT_SP = 11
COMPACT_AXIS_FONT_SP = 10

# Header card parameters.
# Format:
# - text values control visible wording in the header.
# - height/font values control the card title and notice line.
HEADER_CARD_TITLE_TEXT = "[b]VIS-NIR Spectrometer[/b]"
HEADER_CARD_INITIAL_NOTICE_TEXT = "Waiting for the spectrometer stream."
HEADER_TITLE_HEIGHT = dp(40)
HEADER_TITLE_HEIGHT_COMPACT = dp(34)
HEADER_TITLE_HEIGHT_SHORT = dp(28)
HEADER_NOTICE_HEIGHT = dp(28)
HEADER_NOTICE_HEIGHT_COMPACT = dp(44)
HEADER_NOTICE_HEIGHT_SHORT = dp(24)
HEADER_NOTICE_MIN_TEXT_WIDTH = dp(200)
HEADER_CARD_SPACING_COMPACT = dp(6)
HEADER_CARD_PADDING_COMPACT = dp(10)
HEADER_CARD_SPACING_SHORT = dp(4)
HEADER_CARD_PADDING_SHORT = dp(8)

# Connection card parameters.
# Format:
# - these values control all visible text and sizing for the connection card.
CONNECTION_CARD_TITLE_TEXT = "Connection"
CONNECTION_CARD_PORT_PLACEHOLDER = "Select COM Port"
CONNECTION_CARD_NO_PORTS_TEXT = "No COM Ports Found"
CONNECTION_CARD_STATUS_TEXT = "Status: disconnected"
CONNECTION_CARD_FIRMWARE_TEXT = "Firmware: waiting for banner"
CONNECTION_CARD_REFRESH_BUTTON_TEXT = "Refresh Ports"
CONNECTION_CARD_CONNECT_BUTTON_TEXT = "Connect"
CONNECTION_CARD_DISCONNECT_BUTTON_TEXT = "Disconnect"
CONNECTION_CARD_START_DISPLAY_BUTTON_TEXT = "Start Display"
CONNECTION_CARD_STOP_DISPLAY_BUTTON_TEXT = "Stop Display"

# Workspace launcher parameters.
# Format:
# - these values control the side-panel launcher card that opens full-screen tools.
WORKSPACE_CARD_TITLE_TEXT = "Tools"
WORKSPACE_CARD_BACKGROUND_RGBA = (0.94, 0.92, 0.84, 0.98)
WORKSPACE_CARD_BORDER_RGBA = (0.54, 0.47, 0.24, 1.0)
WORKSPACE_CARD_CALIBRATION_BUTTON_TEXT = "Calibration Manager"
WORKSPACE_CARD_DISPLAY_BUTTON_TEXT = "Display & Layout"

# Calibration card parameters.
# Format:
# - these values control the calibration card wording, hint text, and helper copy.
CALIBRATION_CARD_DARK_TEXT = "Apply dark subtraction"
CALIBRATION_CARD_INTENSITY_TEXT = "Apply intensity correction"
CALIBRATION_CARD_QE_TEXT = "Apply QE / response correction"
CALIBRATION_CARD_SAVE_BUTTON_TEXT = "Save Calibration"

# Calibration manager parameters.
# Format:
# - these values control the full-screen calibration workflow shown in the main content area.
CALIBRATION_MANAGER_TITLE_TEXT = "Calibration Manager"
CALIBRATION_MANAGER_SUBTITLE_TEXT = (
    "Capture references, fit the wavelength map, and save correction edits."
)
CALIBRATION_MANAGER_BACK_BUTTON_TEXT = "Return To Live Display"
CALIBRATION_MANAGER_LIST_TITLE_TEXT = "Calibration Routines"
CALIBRATION_MANAGER_SETTINGS_TITLE_TEXT = "Calibration Settings"
CALIBRATION_MANAGER_PIXEL_MAPPING_TEXT = "Run Pixel Mapping"
CALIBRATION_MANAGER_PIXEL_MAPPING_DESC = "Capture several reference light sources and fit pixel positions to known peaks."
CALIBRATION_MANAGER_DARK_REFERENCE_TEXT = "Capture Dark Reference"
CALIBRATION_MANAGER_DARK_REFERENCE_DESC = "Measure covered-sensor baseline counts for later subtraction."
CALIBRATION_MANAGER_INTENSITY_REFERENCE_TEXT = "Capture Intensity Reference"
CALIBRATION_MANAGER_INTENSITY_REFERENCE_DESC = "Record a flat-field style reference for response correction."
CALIBRATION_MANAGER_WAVELENGTH_REVIEW_TEXT = "Review Wavelength Fit"
CALIBRATION_MANAGER_WAVELENGTH_REVIEW_DESC = "Review the active wavelength fit and update the wavelength map."

# Display manager parameters.
# Format:
# - these values control the full-screen display layout menu shown in the main content area.
DISPLAY_MANAGER_TITLE_TEXT = "Display & Layout"
DISPLAY_MANAGER_SUBTITLE_TEXT = (
    "Choose which side-panel cards stay visible, trim the frame-data readout, and switch the live graph style."
)
DISPLAY_MANAGER_BACK_BUTTON_TEXT = "Return To Live Display"
DISPLAY_MANAGER_GRAPH_CARD_TITLE_TEXT = "Live Graph"
DISPLAY_MANAGER_GRAPH_HELPER_TEXT = "Switch between the line plot and a rolling spectrogram built from recent session frames."
DISPLAY_MANAGER_GRAPH_MODE_LABEL_TEXT = "Graph mode"
DISPLAY_MANAGER_GRAPH_MODE_SPECTRUM_TEXT = "Line Spectrum"
DISPLAY_MANAGER_GRAPH_MODE_SPECTROGRAM_TEXT = "Rolling Spectrogram"
DISPLAY_MANAGER_SCALING_LABEL_TEXT = "Spectrum scaling"
DISPLAY_MANAGER_SCALING_AUTO_TEXT = "Auto Range"
DISPLAY_MANAGER_SCALING_ABSOLUTE_TEXT = "Absolute Saturation"
DISPLAY_MANAGER_SPECTROGRAM_WINDOW_LABEL_TEXT = "Spectrogram time window"
DISPLAY_MANAGER_SPECTROGRAM_WINDOW_HELPER_TEXT = "Choose how much recent time the rolling spectrogram should show."
DISPLAY_MANAGER_PANELS_CARD_TITLE_TEXT = "Side Panels"
DISPLAY_MANAGER_PANELS_HELPER_TEXT = "Choose which side-panel cards remain visible in the main workspace."
DISPLAY_MANAGER_FRAME_CARD_TITLE_TEXT = "Frame Data"
DISPLAY_MANAGER_FRAME_HELPER_TEXT = "Pick which live status rows appear in the Frame Data card."
DISPLAY_MANAGER_SHOW_COMMAND_CARD_TEXT = "Show Integration and Recording card"
DISPLAY_MANAGER_SHOW_DIAGNOSTICS_CARD_TEXT = "Show Diagnostics card"
DISPLAY_MANAGER_SHOW_PERFORMANCE_CARD_TEXT = "Show Performance card"
DISPLAY_MANAGER_SHOW_FRAME_ROW_TEXT = "Show frame summary"
DISPLAY_MANAGER_SHOW_LAYOUT_ROW_TEXT = "Show layout summary"
DISPLAY_MANAGER_SHOW_EDGE_ROW_TEXT = "Show edge samples"
DISPLAY_MANAGER_SHOW_REFRESH_ROW_TEXT = "Show graph refresh"
DISPLAY_MANAGER_SHOW_SESSION_ROW_TEXT = "Show session status"

# Session and command card parameters.
# Format:
# - these values control the command/session card wording and button captions.
COMMAND_CARD_TITLE_TEXT = "Integration and Recording"
COMMAND_CARD_EXPORT_BUTTON_TEXT = "Export Session"
COMMAND_CARD_START_BINARY_BUTTON_TEXT = "Start Binary Recording"
COMMAND_CARD_STOP_BINARY_BUTTON_TEXT = "Stop Binary Recording"

# Spectrum card parameters.
# Format:
# - these values control the graph card labels, placeholder text, and status wording.
SPECTRUM_CARD_TITLE_TEXT = "Live Spectrum"
SPECTROGRAM_CARD_TITLE_TEXT = "Rolling Spectrogram"
SPECTRUM_CARD_STREAM_WAITING_TEXT = "Layout: waiting for stream"
SPECTRUM_CARD_LAYOUT_PAUSED_TEXT = "Layout: live display paused"
SPECTRUM_CARD_FRAME_LABEL_TEXT = "Frame: n/a"
SPECTRUM_CARD_LAYOUT_LABEL_TEXT = "Layout: n/a"
SPECTRUM_CARD_EDGE_LABEL_TEXT = "Edge samples: n/a"
SPECTRUM_CARD_REFRESH_LABEL_TEXT = "Graph Refresh: n/a"
SPECTRUM_CARD_REFRESH_PAUSED_TEXT = "Graph Refresh: paused"
SPECTRUM_CARD_SESSION_LABEL_TEXT = "Session: n/a"
SPECTRUM_CARD_LAYOUT_FULL_TEMPLATE = (
    "Layout: total={total} | effective={effective} | leading dummy={leading} | trailing dummy={trailing}"
)
SPECTRUM_CARD_LAYOUT_INCOMPLETE_TEMPLATE = (
    "Layout: incomplete frame with {total} samples received. The app is plotting exactly what the device sent."
)

# Diagnostics card parameters.
# Format:
# - these values control the diagnostics/log panel.
DIAGNOSTICS_CARD_TITLE_TEXT = "Diagnostics"
DIAGNOSTICS_CARD_TEXT_HEIGHT = dp(220)
DIAGNOSTICS_CARD_TEXT_HEIGHT_COMPACT = dp(180)
DIAGNOSTICS_LOG_HISTORY_LINES = 12
PERFORMANCE_CARD_TITLE_TEXT = "Performance"
PERFORMANCE_CARD_TEXT_HEIGHT = dp(420)
PERFORMANCE_CARD_TEXT_HEIGHT_COMPACT = dp(320)
PERFORMANCE_REPORT_REFRESH_S = 1.0
PERFORMANCE_REPORT_MAX_METRICS = 999
PERFORMANCE_REPORT_MAX_VALUES = 999
PERFORMANCE_REPORT_MAX_COUNTERS = 999
PERFORMANCE_CARD_PAUSED_TEXT = (
    "Performance monitoring paused.\nEnable the Performance card to resume sampling."
)
PERFORMANCE_CARD_COLLECTING_TEXT = (
    "Performance Snapshot\nCollecting samples..."
)
CALIBRATION_EDITOR_HEIGHT = dp(120)
CALIBRATION_EDITOR_HEIGHT_COMPACT = dp(96)

# Calibration manager bias/dark card parameters.
# Format:
# - these values control the bias capture and editing section.
CALIBRATION_BIAS_CARD_TITLE_TEXT = "Bias And Dark Terms"
CALIBRATION_BIAS_CARD_HELPER_TEXT = (
    "Capture B_p with the CCD fully blacked out. The frame-wise dark offset beta_f still comes from shielded pixels 16 to 28 in each live frame."
)
CALIBRATION_BIAS_CAPTURE_COUNT_HINT = "Frames to average for B_p"
CALIBRATION_BIAS_CAPTURE_BUTTON_TEXT = "Start Bias Calibration"
CALIBRATION_BIAS_VECTOR_HINT = "Master bias B_p counts (comma or whitespace separated)"
CALIBRATION_BIAS_SUMMARY_TEMPLATE = "Stored B_p samples: {count}"

# Calibration manager wavelength card parameters.
# Format:
# - these values control the pixel-mapping and polynomial fitting section.
CALIBRATION_WAVELENGTH_CARD_TITLE_TEXT = "Wavelength Mapping"
CALIBRATION_WAVELENGTH_CARD_HELPER_TEXT = (
    "Start guided mapping to add your laser wavelengths and capture their peaks. "
    "You can also edit the pixel and wavelength pairs directly."
)
CALIBRATION_WAVELENGTH_POINTS_HINT = "Pixel mapping points: one per line as pixel,wavelength_nm"
CALIBRATION_WAVELENGTH_GUIDED_START_BUTTON_TEXT = "Start Guided Mapping"
CALIBRATION_WAVELENGTH_GUIDED_RESET_BUTTON_TEXT = "Clear Wavelength Map"
CALIBRATION_WAVELENGTH_FIT_ORDER_TEXT = "Wavelength fit order"
CALIBRATION_WAVELENGTH_FIT_BUTTON_TEXT = "Fit Wavelength Map"

# Calibration manager flat-field card parameters.
# Format:
# - these values control the per-pixel flat-field / PRNU correction input.
CALIBRATION_FLAT_FIELD_CARD_TITLE_TEXT = "Flat-Field / PRNU"
CALIBRATION_FLAT_FIELD_CARD_HELPER_TEXT = (
    "Enter multiplicative per-pixel correction factors if you have measured a flat-field or PRNU calibration."
)
CALIBRATION_FLAT_FIELD_VECTOR_HINT = "Flat-field correction factors (comma or whitespace separated)"
CALIBRATION_FLAT_FIELD_SUMMARY_TEMPLATE = "Stored flat-field factors: {count}"

# Calibration manager QE card parameters.
# Format:
# - these values control the wavelength-dependent QE / response curve section.
CALIBRATION_QE_CARD_TITLE_TEXT = "QE / Response Curve"
CALIBRATION_QE_CARD_HELPER_TEXT = (
    "Enter wavelength,response pairs to correct detector and optical throughput. Values are normalized at the chosen reference wavelength."
)
CALIBRATION_QE_POINTS_HINT = "QE / response points: one per line as wavelength_nm,relative_value"
CALIBRATION_QE_NORMALIZATION_HINT = "QE normalization wavelength (nm)"
CALIBRATION_QE_SUMMARY_TEMPLATE = "QE reference points: {count}"


HEADER_SIDE_PANEL_BUTTON_TEXT = "Hide Side Panel"
HEADER_SIDE_PANEL_BUTTON_TEXT_HIDDEN = "Show Side Panel"
HEADER_SIDE_PANEL_BUTTON_WIDTH = dp(160)
HEADER_SIDE_PANEL_BUTTON_WIDTH_COMPACT = dp(136)


class Card(BoxLayout):
    """Purpose: render a styled panel container. Rationale: shared card styling keeps the UI layout consistent."""
    def __init__(self, **kwargs) -> None:
        """Purpose: build the card layout and background. Rationale: reusable visual framing should be created once in one widget."""
        background_rgba = kwargs.pop("background_rgba", CARD_BACKGROUND_RGBA)
        border_rgba = kwargs.pop("border_rgba", CARD_BORDER_RGBA)
        # Every card is a vertical stack with shared spacing and padding so the
        # content blocks line up consistently across the app.
        super().__init__(orientation="vertical", spacing=CARD_GAP, padding=CARD_PAD, **kwargs)
        with self.canvas.before:
            Color(*background_rgba)
            self._background = RoundedRectangle(radius=[18])
            Color(*border_rgba)
            self._border = Line(rounded_rectangle=[0, 0, 0, 0, 18], width=1.0)
        self.bind(pos=self._update_background, size=self._update_background)

    def _update_background(self, *_args) -> None:
        """Purpose: resize the rounded background to match the widget. Rationale: Kivy canvas shapes do not track widget size automatically."""
        self._background.pos = self.pos
        self._background.size = self.size
        self._border.rounded_rectangle = [self.x, self.y, self.width, self.height, 18]


class CalibrationDialog(Popup):
    """Give calibration routines a shared header, preview area, progress, and footer."""

    def __init__(self, title: str, *, height: int, body_min_height: int) -> None:
        super().__init__(title=title, auto_dismiss=False, size_hint=(None, None))
        layout = BoxLayout(orientation="vertical", spacing=CARD_GAP, padding=CARD_PAD)
        self._stage = self._message_label(bold=True, halign="center")
        self._heading = Label(bold=True, font_size=sp(28), size_hint_y=None, height=dp(42))
        with self._heading.canvas.after:
            Color(*CALIBRATION_SUCCESS_RGBA)
            self._check = Line(width=dp(2))
        self._heading.bind(pos=self._position_check, size=self._position_check, texture_size=self._position_check)
        self._instructions = self._message_label()
        layout.add_widget(self._stage)
        layout.add_widget(self._heading)
        layout.add_widget(self._instructions)

        self.body = BoxLayout(orientation="vertical", spacing=CARD_GAP, size_hint_y=None)
        self._body_scroll = ScrollView(
            do_scroll_x=False, bar_width=dp(6), always_overscroll=False, scroll_type=["bars"],
        )
        self._body_scroll.add_widget(self.body)
        self._body_scroll.bind(height=self._resize_body)
        layout.add_widget(self._body_scroll)

        self._feedback = self._message_label(color=CALIBRATION_ERROR_RGBA)
        self._progress_text = self._message_label(halign="center")
        self._progress = ProgressBar(size_hint_y=None, height=0, opacity=0)
        layout.add_widget(self._feedback)
        layout.add_widget(self._progress_text)
        layout.add_widget(self._progress)

        footer = BoxLayout(size_hint_y=None, height=BUTTON_HEIGHT, spacing=CARD_GAP)
        self.cancel = Button(
            text="Cancel Calibration", background_normal="", background_down="",
            background_color=DESTRUCTIVE_BUTTON_BACKGROUND_RGBA,
        )
        self.primary = Button(
            text="Complete", disabled=True, background_normal="", background_down="",
            background_color=BUTTON_BACKGROUND_RGBA,
        )
        footer.add_widget(self.cancel)
        footer.add_widget(self.primary)
        layout.add_widget(footer)
        self.content = layout
        self.set_size(height=height, body_min_height=body_min_height)

    @staticmethod
    def _message_label(**kwargs) -> Label:
        kwargs.setdefault("halign", "left")
        label = Label(valign="middle", size_hint_y=None, height=0, **kwargs)
        label.bind(width=lambda instance, width: setattr(instance, "text_size", (width, None)))
        label.bind(texture_size=lambda instance, size: setattr(instance, "height", size[1]))
        return label

    def set_size(self, *, height: int, body_min_height: int) -> None:
        self._body_min_height = dp(body_min_height)
        self.size = (min(dp(680), Window.width - dp(24)), min(dp(height), Window.height - dp(24)))
        self._body_scroll.scroll_y = 1
        self._resize_body()

    def _resize_body(self, *_args) -> None:
        self.body.height = max(self._body_min_height, self._body_scroll.height)
        self._body_scroll.do_scroll_y = self.body.height > self._body_scroll.height

    def set_step(self, heading: str, instructions: str, *, stage: str = "") -> None:
        self._stage.text = stage
        self._heading.text = heading
        self._heading.color = BUTTON_TEXT_RGBA
        self._instructions.text = instructions
        self._position_check()

    def set_error(self, message: str) -> None:
        self._feedback.text = message

    def set_progress(self, current: int, total: int, *, item: str) -> None:
        self._progress_text.text = f"{current} of {total} {item} captured"
        self._progress.max = total
        self._progress.value = current
        self._progress.height = dp(10)
        self._progress.opacity = 1

    def show_review(self, instructions: str) -> None:
        self.set_step("Capture complete", instructions)
        self._heading.color = CALIBRATION_SUCCESS_RGBA
        self._position_check()
        self.primary.disabled = False

    def _position_check(self, *_args) -> None:
        if tuple(self._heading.color) == CALIBRATION_SUCCESS_RGBA:
            x = self._heading.center_x - self._heading.texture_size[0] / 2 - dp(25)
            y = self._heading.center_y
            self._check.points = (x, y, x + dp(5), y - dp(5), x + dp(15), y + dp(6))
        else:
            self._check.points = []


class SpectrumWarnings(BoxLayout):
    """Show active warnings below the spectrum controls."""

    def __init__(self, plot_card: Card) -> None:
        super().__init__(orientation="vertical", size_hint_y=None, spacing=dp(4))
        self._plot_card = plot_card
        self._warnings: dict[str, tuple[str, tuple[float, ...]]] = {}
        self._dismissed: set[str] = set()
        self.bind(minimum_height=self.setter("height"))
        self.button = RaisedActionButton(
            text="Notifications", disabled=True, size_hint=(None, None), size=(dp(132), dp(32)),
            pos_hint={"top": 1}, font_size=sp(13), face_color=APP_BACKGROUND_RGBA,
            color=TEXT_PRIMARY_RGBA,
        )
        self.button.bind(on_release=self._toggle_warnings)

    def set_warning(self, key: str, text: str | None, color: tuple[float, ...]) -> None:
        warning = (text, color) if text is not None else None
        if warning == self._warnings.get(key):
            return
        self._dismissed.discard(key)
        if warning is None:
            self._warnings.pop(key)
        else:
            self._warnings[key] = warning
        self._refresh()

    def _dismiss(self, key: str) -> None:
        self._dismissed.add(key)
        self._refresh()

    def _toggle_warnings(self, *_args) -> None:
        self._dismissed = set() if self._dismissed else set(self._warnings) - {"overload"}
        self._refresh()

    def _refresh(self) -> None:
        self.clear_widgets()
        count = len(self._warnings)
        self.button.text = f"Notifications ({count})" if count else "Notifications"
        self.button.disabled = not (self._warnings.keys() - {"overload"})
        for key in ("overload", "saturation", "bias_exposure", "dark_exposure"):
            if key not in self._warnings or key in self._dismissed:
                continue
            text, color = self._warnings[key]
            card = Card(size_hint_y=None, background_rgba=color, border_rgba=color)
            card.orientation = "horizontal"
            card.padding = (dp(10), dp(6))
            card.bind(minimum_height=card.setter("height"))
            label = Label(
                text=text, markup=True, size_hint_y=None, halign="left",
                font_size=sp(14), color=TEXT_PRIMARY_RGBA,
            )
            label.bind(
                width=lambda widget, width: setattr(widget, "text_size", (max(1, width), None)),
                texture_size=lambda widget, size: setattr(widget, "height", size[1]),
            )
            card.add_widget(label)
            if key != "overload":
                dismiss = RaisedActionButton(
                    text="Dismiss", size_hint=(None, None), size=(dp(72), dp(30)),
                    pos_hint={"center_y": 0.5}, font_size=sp(13),
                    face_color=APP_BACKGROUND_RGBA, color=TEXT_PRIMARY_RGBA,
                )
                dismiss.bind(on_release=lambda _, name=key: self._dismiss(name))
                card.add_widget(dismiss)
            self.add_widget(card)
        if self.children and self.parent is None:
            self._plot_card.add_widget(self, index=1)
        elif not self.children and self.parent is self._plot_card:
            self._plot_card.remove_widget(self)


class RaisedActionButton(Button):
    """Draw the action button face within the existing Kivy hit area."""

    face_color = ColorProperty(BUTTON_BACKGROUND_RGBA)

    def __init__(self, **kwargs) -> None:
        super().__init__(
            background_color=(0, 0, 0, 0), background_normal="", background_down="",
            background_disabled_normal="", background_disabled_down="",
            disabled_color=TEXT_TERTIARY_RGBA, **kwargs,
        )
        with self.canvas.before:
            self._shadow_color = Color()
            self._shadow = RoundedRectangle()
            self._face_color = Color()
            self._face = RoundedRectangle()
            self._edge_color = Color()
            self._edge = Line(width=1)
            self._highlight_color = Color()
            self._highlight = Line(width=1)
        self.bind(pos=self._draw_face, size=self._draw_face, state=self._draw_face,
                  disabled=self._draw_face, face_color=self._draw_face)
        self._draw_face()

    def _draw_face(self, *_args) -> None:
        raised = not self.disabled and self.state == "normal"
        depth = 0 if self.disabled else min(dp(2), self.height)
        face_height = self.height - depth
        face_bottom = self.y + (depth if raised else 0)
        radius = min(dp(4), self.width / 2, face_height / 2)
        face = CARD_BORDER_RGBA if self.disabled else self.face_color
        shade = 0.92 if self.state == "down" and not self.disabled else 1

        self._shadow_color.rgba = (0.13, 0.19, 0.21, 0.32 if raised else 0)
        self._shadow.pos = self.pos
        self._shadow.size = (self.width, face_height)
        self._shadow.radius = [radius]
        self._face_color.rgba = (*(channel * shade for channel in face[:3]), face[3])
        self._face.pos = (self.x, face_bottom)
        self._face.size = (self.width, face_height)
        self._face.radius = [radius]
        self._edge_color.rgba = (*(channel * 0.74 for channel in face[:3]), 1)
        self._edge.rounded_rectangle = [self.x, face_bottom, self.width, face_height, radius]
        self._highlight_color.rgba = (1, 1, 1, 0.36 if raised else 0)
        top = face_bottom + face_height - dp(1)
        self._highlight.points = [self.x + radius, top, self.right - radius, top]


class CursorDropDown(DropDown):
    """Keep the spaced marker actions legible over the plot."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.container.padding = dp(5)
        self.container.spacing = dp(4)
        with self.canvas.before:
            Color(*CARD_BACKGROUND_RGBA[:3], 1)
            self._backdrop = RoundedRectangle(radius=[dp(5)])
            Color(*CARD_BORDER_RGBA)
            self._outline = Line(width=1)
        self.bind(pos=self._draw_backdrop, size=self._draw_backdrop)
        self._draw_backdrop()

    def _draw_backdrop(self, *_args) -> None:
        self._backdrop.pos = self.pos
        self._backdrop.size = self.size
        self._outline.rounded_rectangle = [*self.pos, *self.size, dp(5)]


class SpectrumPlot(Widget):
    """Purpose: draw the live spectrum line. Rationale: a custom plot widget gives full control over axes, scaling, and rendering speed."""

    reverse_horizontal_axis = BooleanProperty(False)

    def __init__(
        self, *, cursor_settings: CursorConfig | None = None,
        performance_monitor=None, performance_metric_name: str = "ui.spectrum_redraw", **kwargs,
    ) -> None:
        """Purpose: initialize plot state and redraw bindings. Rationale: the plot should react whenever data or size changes."""
        super().__init__(**kwargs)
        self.cursor_settings = cursor_settings if cursor_settings is not None else CursorConfig()
        self._performance_monitor = performance_monitor
        self._performance_metric_name = performance_metric_name
        # The plot stores raw x/y series and maps them into screen coordinates
        # during `_redraw`.
        self._x_values: Sequence[int] = ()
        self._y_values: Sequence[float] = ()
        self._adc_min = 0.0
        self._adc_max = float((1 << 12) - 1)
        self._cursor_index: int | None = None
        self._cursor_callback = None
        self._plot_bounds: tuple[float, float, float, float] | None = None
        self._x_grid_count = X_AXIS_TICK_COUNT
        self._y_grid_count = Y_AXIS_TICK_COUNT
        self._last_cursor_drag_update_s = 0.0
        self._pending_cursor_drag_x: float | None = None
        self._cursor_drag_flush_event = None
        self.bind(pos=self._redraw, size=self._redraw, reverse_horizontal_axis=self._redraw)

    def set_cursor_settings(self, settings: CursorConfig) -> None:
        if settings != self.cursor_settings:
            self.cursor_settings = settings
            self._redraw()

    def _marker_color(self, number: int) -> tuple[float, float, float, float]:
        palette = HIGH_CONTRAST_MARKER_COLORS if self.cursor_settings.palette == "high_contrast" else PLOT_MARKER_COLORS
        return palette[(number - 1) % len(palette)]

    def set_series(self, x_values: Sequence[int], y_values: Sequence[float]) -> None:
        """Purpose: store the current x/y series. Rationale: the UI should update the plot by replacing data, not drawing directly."""
        self._x_values = x_values
        self._y_values = y_values
        self._redraw()

    def set_cursor_callback(self, callback) -> None:
        """Purpose: register a cursor-selection callback. Rationale: the parent UI needs the selected point details without owning the plot math."""
        self._cursor_callback = callback

    def current_cursor_value(self) -> tuple[int, float] | None:
        """Purpose: report the currently selected sample. Rationale: the parent UI should be able to refresh the cursor readout as live data changes."""
        if (
            self._cursor_index is None
            or self._cursor_index < 0
            or self._cursor_index >= len(self._x_values)
            or self._cursor_index >= len(self._y_values)
            or not isfinite(self._y_values[self._cursor_index])
        ):
            return None
        return int(self._x_values[self._cursor_index]), float(self._y_values[self._cursor_index])

    def clear_cursor(self) -> None:
        self._cancel_pending_cursor_drag_flush()
        self._cursor_index = None
        self._redraw()

    def _cursor_points(self):
        point = self.current_cursor_value()
        if point is not None:
            yield point, self._marker_color(1)

    def set_adc_range(self, adc_min: float, adc_max: float) -> None:
        """Purpose: store the y-axis bounds. Rationale: the graph should use the fixed ADC scale chosen by the device config."""
        normalized_min = float(adc_min)
        normalized_max = float(max(adc_max, adc_min + 1))
        if abs(self._adc_min - normalized_min) < 1e-9 and abs(self._adc_max - normalized_max) < 1e-9:
            return
        self._adc_min = normalized_min
        self._adc_max = normalized_max
        self._redraw()

    def set_grid_counts(self, *, x_count: int, y_count: int) -> None:
        """Purpose: update the visible grid density. Rationale: maximized and windowed modes should be able to tune grid spacing without changing the plot data path."""
        self._x_grid_count = max(int(x_count), 2)
        self._y_grid_count = max(int(y_count), 2)
        self._redraw()

    def _horizontal_transform(self, left: float, width: float) -> tuple[float, float]:
        scale = width / max(self._x_values[-1] - self._x_values[0], 1)
        if self.reverse_horizontal_axis:
            return left + width, -scale
        return left, scale

    def _redraw(self, *_args) -> None:
        """Purpose: redraw the plot canvas. Rationale: Kivy plots are manual, so any visual update must be rendered explicitly."""
        monitor = self._performance_monitor
        with (
            monitor.measure(self._performance_metric_name)
            if monitor is not None
            else nullcontext()
        ):
            self.canvas.clear()
            with self.canvas:
                # Plot background panel.
                Color(*APP_BACKGROUND_RGBA)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[PLOT_CORNER_RADIUS])

                # Plot border so the graph area reads like a chart, not empty space.
                Color(*CARD_BORDER_RGBA)
                Line(
                    rounded_rectangle=[self.x, self.y, self.width, self.height, PLOT_CORNER_RADIUS],
                    width=PLOT_BORDER_WIDTH,
                )

                self._plot_bounds = None
                if (
                    not self._x_values
                    or not self._y_values
                    or self.width <= PLOT_MIN_DRAW_SIZE
                    or self.height <= PLOT_MIN_DRAW_SIZE
                ):
                    return

                left = self.x + PLOT_HORIZONTAL_INNER_PAD
                bottom = self.y + PLOT_VERTICAL_INNER_PAD
                plot_width = max(self.width - (PLOT_HORIZONTAL_INNER_PAD * 2), 1.0)
                plot_height = max(self.height - (PLOT_VERTICAL_INNER_PAD * 2), 1.0)
                self._plot_bounds = (left, bottom, plot_width, plot_height)

                # Convert sample coordinates into widget pixel coordinates.
                points: list[float] = []
                x_min = float(self._x_values[0])
                x_origin, x_scale = self._horizontal_transform(left, plot_width)
                y_scale = plot_height / (self._adc_max - self._adc_min)

                for x_value, sample in zip(self._x_values, self._y_values):
                    clamped_sample = min(max(float(sample), self._adc_min), self._adc_max)
                    x_pos = x_origin + ((float(x_value) - x_min) * x_scale)
                    y_pos = bottom + ((clamped_sample - self._adc_min) * y_scale)
                    points.extend((x_pos, y_pos))

                # Draw grid lines that match the visible y-axis and x-axis ticks.
                Color(*GUIDE_LINE_RGBA)
                for tick_index in range(1, self._y_grid_count - 1):
                    y_fraction = tick_index / (self._y_grid_count - 1)
                    y_pos = bottom + (plot_height * y_fraction)
                    Line(points=[left, y_pos, left + plot_width, y_pos], width=GUIDE_LINE_WIDTH)
                for tick_index in range(1, self._x_grid_count - 1):
                    x_fraction = tick_index / (self._x_grid_count - 1)
                    x_pos = left + (plot_width * x_fraction)
                    Line(points=[x_pos, bottom, x_pos, bottom + plot_height], width=GUIDE_LINE_WIDTH)

                # The spectrum is drawn in chunks because very long single Kivy lines
                # can render unreliably or become sluggish.
                Color(*PLOT_LINE_RGBA)
                for chunk in self._iter_line_chunks(points, max_vertices=PLOT_CHUNK_MAX_VERTICES):
                    Line(points=chunk, width=PLOT_LINE_WIDTH)

                for (pixel, value), color in self._cursor_points():
                    cursor_x = x_origin + (pixel - x_min) * x_scale
                    cursor_y = bottom + (min(max(value, self._adc_min), self._adc_max) - self._adc_min) * y_scale
                    if self.cursor_settings.line_style != "point_only":
                        Color(*color[:3], color[3] * 0.67)
                        self._draw_cursor_guide(cursor_x, bottom, plot_height)
                    Color(*color)
                    radius = dp(CURSOR_POINT_RADII[self.cursor_settings.point_size])
                    Line(circle=(cursor_x, cursor_y, radius), width=1)

    def _draw_cursor_guide(self, x: float, bottom: float, height: float) -> None:
        thickness = self.cursor_settings.line_thickness
        left = x - thickness / 2
        if self.cursor_settings.line_style == "solid":
            Rectangle(pos=(left, bottom), size=(thickness, height))
            return

        right = left + thickness
        dash, gap = dp(8), dp(5)
        top = bottom + height
        vertices, indices = [], []
        for offset in range(ceil(height / (dash + gap))):
            y = bottom + offset * (dash + gap)
            end = min(y + dash, top)
            index = len(vertices) // 4
            vertices.extend((left, y, 0, 0, right, y, 0, 0, right, end, 0, 0, left, end, 0, 0))
            indices.extend((index, index + 1, index + 2, index, index + 2, index + 3))
        Mesh(vertices=vertices, indices=indices, mode="triangles")

    def on_touch_down(self, touch) -> bool:
        """Purpose: place or move the plot cursor. Rationale: users should be able to inspect one plotted point interactively."""
        if super().on_touch_down(touch):
            return True
        if not self.collide_point(*touch.pos):
            return False
        self._cancel_pending_cursor_drag_flush()
        return self._update_cursor_from_touch(touch)

    def on_touch_move(self, touch) -> bool:
        """Purpose: drag the plot cursor across the graph. Rationale: cursor inspection should work smoothly while dragging."""
        if touch.grab_current is self:
            return self._update_cursor_from_drag(touch) or True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch) -> bool:
        """Purpose: release the cursor drag state. Rationale: grabbed touches should be released cleanly after interaction."""
        if touch.grab_current is self:
            self._cancel_pending_cursor_drag_flush()
            self._update_cursor_from_position(touch.x)
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

    def _update_cursor_from_touch(self, touch) -> bool:
        """Purpose: convert a touch position into the nearest plotted sample. Rationale: cursor selection should snap to real sample points."""
        return self._update_cursor_from_position(touch.x, touch=touch)

    def _update_cursor_from_drag(self, touch) -> bool:
        """Purpose: throttle cursor dragging work while the mouse is held. Rationale: rapid pointer-move events can redraw the full plot too often and hurt responsiveness."""
        now_s = perf_counter()
        elapsed_s = now_s - self._last_cursor_drag_update_s
        if elapsed_s >= PLOT_CURSOR_DRAG_COOLDOWN_S:
            self._cancel_pending_cursor_drag_flush()
            return self._update_cursor_from_touch(touch)

        self._pending_cursor_drag_x = float(touch.x)
        remaining_s = max(PLOT_CURSOR_DRAG_COOLDOWN_S - elapsed_s, 0.0)
        if self._cursor_drag_flush_event is None:
            self._cursor_drag_flush_event = Clock.schedule_once(self._flush_pending_cursor_drag, remaining_s)
        return True

    def _flush_pending_cursor_drag(self, _dt: float) -> None:
        """Purpose: apply the latest deferred drag position after the cooldown. Rationale: deferred cursor updates should use the most recent pointer position instead of replaying every intermediate move."""
        self._cursor_drag_flush_event = None
        if self._pending_cursor_drag_x is None:
            return
        pending_x = self._pending_cursor_drag_x
        self._pending_cursor_drag_x = None
        self._update_cursor_from_position(pending_x)

    def _cancel_pending_cursor_drag_flush(self) -> None:
        """Purpose: stop a queued drag update when a newer direct update supersedes it. Rationale: the cursor should not redraw twice for the same interaction frame."""
        if self._cursor_drag_flush_event is not None:
            self._cursor_drag_flush_event.cancel()
            self._cursor_drag_flush_event = None
        self._pending_cursor_drag_x = None

    def _update_cursor_from_position(self, touch_x: float, *, touch=None) -> bool:
        """Purpose: snap one horizontal pointer position to the nearest plotted sample. Rationale: both direct clicks and throttled drag updates should share one cursor-selection path."""
        if not self._x_values or not self._y_values or self._plot_bounds is None:
            return False

        left, _bottom, plot_width, _plot_height = self._plot_bounds
        if plot_width <= 0:
            return False

        relative_x = min(max(float(touch_x), left), left + plot_width) - left
        fraction = relative_x / plot_width
        if self.reverse_horizontal_axis:
            fraction = 1.0 - fraction
        nearest_index = int(round(fraction * max(len(self._x_values) - 1, 0)))
        nearest_index = min(max(nearest_index, 0), len(self._x_values) - 1)
        self._last_cursor_drag_update_s = perf_counter()
        if touch is not None and touch.grab_current is not self:
            touch.grab(self)
        self._select_cursor(nearest_index)
        return True

    def _select_cursor(self, index: int) -> None:
        self._cursor_index = index
        self._redraw()
        if self._cursor_callback is not None:
            self._cursor_callback(int(self._x_values[index]), float(self._y_values[index]))

    @staticmethod
    def _iter_line_chunks(points: list[float], *, max_vertices: int) -> list[list[float]]:
        """Purpose: split a long line into smaller pieces. Rationale: chunking large plots is more reliable for Kivy rendering."""
        if len(points) <= max_vertices * 2:
            return [points]

        chunks: list[list[float]] = []
        step = max(2, max_vertices * 2)
        start = 0
        last_pair_start = len(points) - 2

        while start < len(points):
            end = min(start + step, len(points))
            chunk = points[start:end]
            if start > 0:
                chunk = points[start - 2:start] + chunk
            if len(chunk) >= 4:
                chunks.append(chunk)
            if end >= len(points):
                break
            start = min(end, last_pair_start)

        return chunks or [points]


def _marker_drag_started(origin: tuple[float, float], touch) -> bool:
    return max(abs(touch.x - origin[0]), abs(touch.y - origin[1])) > MARKER_CLICK_SLOP


class MarkerReadout(Label):
    def __init__(
        self, *, anchor, width, accent,
        on_press: Callable[[bool], bool] | None = None,
        on_click: Callable[[bool], None] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            size_hint=(None, None), opacity=0, markup=True,
            color=TEXT_PRIMARY_RGBA, font_size=sp(12), halign="left",
            valign="middle", **kwargs,
        )
        self.default_anchor = anchor
        # Store anchors in detector order so a display flip mirrors the whole readout.
        self.anchor = anchor
        self.manually_placed = False
        self._base_width = width
        self.preferred_width = dp(width)
        self._preferred_height = dp(44)
        self._style = None
        self._on_press = on_press
        self._on_click = on_click
        self._bounds = (0, 0, 0, 0)
        self._reverse_horizontal_axis = False
        self._drag_offset = (0, 0)
        self._press_pos = (0, 0)
        self._drag_started = False
        self._double_click = False
        with self.canvas.before:
            Color(*APP_BACKGROUND_RGBA)
            self._background = RoundedRectangle(radius=[5])
            self._accent = Color(*accent)
            self._border = Line(width=1)
            Color(*TEXT_TERTIARY_RGBA)
            self._grip = [Ellipse(size=(dp(2), dp(2))) for _ in range(6)]
        self.bind(texture_size=self._refit)

    def apply_style(self, size: str, accent: tuple[float, float, float, float]) -> None:
        style = (size, accent)
        if style != self._style:
            self._style = style
            font_size = CURSOR_READOUT_FONT_SIZES[size]
            self.font_size = sp(font_size)
            self.preferred_width = dp(self._base_width * font_size / 12)
            self._preferred_height = dp(40 if size == "small" else 44)
            self._accent.rgba = accent

    def _refit(self, *_args) -> None:
        if self.opacity:
            self.place(self._bounds)

    def _horizontal_anchor(self, fraction: float) -> float:
        return 1.0 - fraction if self._reverse_horizontal_axis else fraction

    def place(self, bounds: tuple[float, float, float, float], *, reverse_horizontal_axis: bool | None = None) -> None:
        direction_changed = (
            reverse_horizontal_axis is not None and reverse_horizontal_axis != self._reverse_horizontal_axis
        )
        if reverse_horizontal_axis is not None:
            self._reverse_horizontal_axis = reverse_horizontal_axis
        keep_position = self.manually_placed and self._bounds == bounds and not direction_changed
        old_size = tuple(self.size)
        self._bounds = bounds
        left, bottom, width, height = bounds
        self.width = min(width, self.preferred_width)
        self.text_size = (max(self.width - dp(27), 1), None)
        self.height = min(height, max(self._preferred_height, self.texture_size[1] + dp(8)))
        if keep_position and tuple(self.size) != old_size:
            self.anchor = (
                self._horizontal_anchor(min(max((self.x - left) / max(width - self.width, 1), 0), 1)),
                min(max((self.y - bottom) / max(height - self.height, 1), 0), 1),
            )
        self.pos = (
            left + self._horizontal_anchor(self.anchor[0]) * (width - self.width),
            bottom + self.anchor[1] * (height - self.height),
        )
        self._background.pos = self.pos
        self._background.size = self.size
        self._border.rounded_rectangle = [*self.pos, *self.size, 5]
        for index, dot in enumerate(self._grip):
            dot.pos = (self.x + dp(5 + 4 * (index % 2)), self.center_y + dp(4 * (index // 2) - 5))

    def on_touch_down(self, touch) -> bool:
        if not self.opacity or not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self._drag_offset = (touch.x - self.x, touch.y - self.y)
        self._press_pos = touch.pos
        self._drag_started = False
        self._double_click = self._on_press(touch.is_double_tap) if self._on_press is not None else False
        touch.grab(self)
        return True

    def on_touch_move(self, touch) -> bool:
        if touch.grab_current is not self:
            return super().on_touch_move(touch)
        self._drag_readout(touch)
        return True

    def on_touch_up(self, touch) -> bool:
        if touch.grab_current is not self:
            return super().on_touch_up(touch)
        self._drag_readout(touch)
        touch.ungrab(self)
        if not self._drag_started and self._on_click is not None:
            self._on_click(self._double_click)
        return True

    def _drag_readout(self, touch) -> None:
        self._drag_started = self._drag_started or _marker_drag_started(self._press_pos, touch)
        if self._drag_started:
            self._drag_to(touch.x, touch.y)

    def _drag_to(self, x: float, y: float) -> None:
        left, bottom, width, height = self._bounds
        self.manually_placed = True
        screen_anchor = min(max((x - self._drag_offset[0] - left) / max(width - self.width, 1), 0), 1)
        self.anchor = (
            self._horizontal_anchor(screen_anchor),
            min(max((y - self._drag_offset[1] - bottom) / max(height - self.height, 1), 0), 1),
        )
        self.place(self._bounds)


class CalibrationSpectrumPlot(FocusBehavior, SpectrumPlot):
    """One detector-pixel selection for guided wavelength mapping."""

    @property
    def has_data(self) -> bool:
        return len(self._y_values) > 0

    def set_series(self, x_values: Sequence[int], y_values: Sequence[float]) -> None:
        previous = self.current_cursor_value()
        self._cursor_index = None
        if previous is not None:
            pixel = previous[0]
            if marker_value(x_values, y_values, pixel) is not None:
                self._cursor_index = bisect_left(x_values, pixel)
        super().set_series(x_values, y_values)

    def _select_cursor(self, index: int) -> None:
        super()._select_cursor(index)
        self.focus = True

    def search_peak(self, direction: int) -> bool:
        index = directional_extremum(
            self._y_values, self._cursor_index, direction=-direction if self.reverse_horizontal_axis else direction,
            maximum=True,
            prominence=(self._adc_max - self._adc_min) * self.cursor_settings.peak_sensitivity_percent / 100,
        )
        if index is None:
            return False
        self._select_cursor(index)
        return True

    def keyboard_on_key_down(self, window, keycode, text, modifiers) -> bool:
        key = keycode[1]
        if self.focus and key in ("left", "right") and not modifiers:
            current = self.current_cursor_value()
            if current is not None:
                step = -1 if key == "left" else 1
                target = current[0] + (-step if self.reverse_horizontal_axis else step)
                if marker_value(self._x_values, self._y_values, target) is not None:
                    self._select_cursor(bisect_left(self._x_values, target))
            return True
        return super().keyboard_on_key_down(window, keycode, text, modifiers)


class MarkerSpectrumPlot(SpectrumPlot):
    """Interactive numbered markers on the live trace, indexed by detector pixel."""

    def __init__(self, **kwargs) -> None:
        self.markers = MarkerSelection()
        self._readouts: dict[int, MarkerReadout] = {}
        self._difference_readout: MarkerReadout | None = None
        self._pending_marker_click = None
        super().__init__(**kwargs)
        self.on_marker_state_changed: Callable[[], None] | None = None
        self._wavelength_coefficients: tuple[float, ...] = ()
        self._signal_units = "intensity"
        self._difference_readout = MarkerReadout(anchor=(0.98, 0.96), width=232, accent=CARD_BORDER_RGBA)
        self.add_widget(self._difference_readout, canvas="after")

    def set_measurement_context(self, coefficients: Sequence[float], *, raw: bool) -> None:
        wavelength_coefficients = tuple(coefficients)
        units = "counts" if raw else "intensity"
        if (wavelength_coefficients, units) != (self._wavelength_coefficients, self._signal_units):
            self._wavelength_coefficients = wavelength_coefficients
            self._signal_units = units
            self._refresh_readouts()

    def toggle_add_marker(self) -> None:
        self._cancel_marker_click()
        self.markers.adding = not self.markers.adding
        self._notify_marker_state()

    def select_marker(self, number: int) -> None:
        self._cancel_marker_click()
        self.markers.selected = number
        self.markers.adding = False
        self._redraw()
        self._notify_marker_state()

    def set_reference(self, number: int | None) -> None:
        self.markers.reference = number
        self._refresh_readouts()
        self._notify_marker_state()

    def _cancel_marker_click(self) -> None:
        if self._pending_marker_click is not None:
            _, event = self._pending_marker_click
            event.cancel()
            self._pending_marker_click = None

    def _begin_marker_click(self, number: int, double_tap: bool) -> bool:
        pending = self._pending_marker_click
        double_click = double_tap and pending is not None and pending[0] == number
        self._cancel_marker_click()
        return double_click

    def _finish_marker_click(self, number: int, double_click: bool) -> None:
        self._cancel_marker_click()
        if number not in self.markers.pixels:
            return
        if double_click:
            if self.cursor_settings.swap_reference_on_double_click and self.markers.selected == number:
                previous_reference = self.markers.reference
                if previous_reference is None and len(self.markers.pixels) == 2:
                    previous_reference = next(marker for marker in self.markers.pixels if marker != number)
                if previous_reference is not None and previous_reference != number:
                    self.markers.reference = number
                    self.select_marker(previous_reference)
                    return
            self.set_reference(number)
            return

        def select_if_single(_dt: float) -> None:
            self._pending_marker_click = None
            if number in self.markers.pixels:
                self.select_marker(number)

        timeout = Config.getint("postproc", "double_tap_time") / 1000
        self._pending_marker_click = (number, Clock.schedule_once(select_if_single, timeout))

    def remove_marker(self) -> None:
        self._cancel_marker_click()
        self._cancel_pending_cursor_drag_flush()
        number = self.markers.remove_selected()
        if number is not None:
            self.remove_widget(self._readouts.pop(number))
        self._redraw()
        self._notify_marker_state()

    def clear_markers(self) -> None:
        self._cancel_marker_click()
        self._cancel_pending_cursor_drag_flush()
        self.markers = MarkerSelection()
        for readout in self._readouts.values():
            self.remove_widget(readout)
        self._readouts.clear()
        self._difference_readout.manually_placed = False
        self._difference_readout.anchor = self._difference_readout.default_anchor
        self._redraw()
        self._notify_marker_state()

    def search_extremum(self, *, maximum: bool, direction: int = 0) -> bool:
        self._cancel_marker_click()
        if direction:
            pixel = self.markers.pixels.get(self.markers.selected)
            index = directional_extremum(
                self._y_values, search_origin(self._x_values, pixel),
                direction=-direction if self.reverse_horizontal_axis else direction, maximum=maximum,
                prominence=(self._adc_max - self._adc_min) * self.cursor_settings.peak_sensitivity_percent / 100,
            )
        else:
            index = global_extremum(self._y_values, maximum=maximum)
        if index is None:
            return False
        self._place_marker(index)
        return True

    def _notify_marker_state(self) -> None:
        if self.on_marker_state_changed is not None:
            self.on_marker_state_changed()

    def _marker_point(self, number: int) -> tuple[int, float] | None:
        return marker_value(self._x_values, self._y_values, self.markers.pixels.get(number))

    def _cursor_points(self):
        for number in self.markers.pixels:
            point = self._marker_point(number)
            if point is not None:
                color = self._marker_color(number)
                opacity = 1.0 if number == self.markers.selected else self.cursor_settings.inactive_opacity_percent / 100
                yield point, (*color[:3], opacity)

    def _redraw(self, *_args) -> None:
        super()._redraw()
        self._refresh_readouts()

    def _refresh_readouts(self) -> None:
        if self._difference_readout is None:
            return
        selected, reference = self.markers.selected, self.markers.reference
        show_all = self.cursor_settings.readout_visibility == "all"
        points = {}
        wavelengths = {}
        for number, readout in self._readouts.items():
            point = self._marker_point(number)
            visible = show_all or number in (selected, reference)
            readout.opacity = float(visible and point is not None and self._plot_bounds is not None)
            if not readout.opacity:
                continue
            readout.apply_style(self.cursor_settings.readout_size, self._marker_color(number))
            points[number] = point
            pixel, value = point
            position = f"{pixel} px"
            if self._wavelength_coefficients:
                wavelength = float(indices_to_wavelengths([pixel], self._wavelength_coefficients)[0])
                wavelengths[number] = wavelength
                position += f"   {wavelength:.2f} nm"
            reference_suffix = " (ref)" if number == reference else ""
            readout.text = f"[b]M{number}{reference_suffix}[/b]   {position}\n{value:.4f} {self._signal_units}"
            if not readout.manually_placed:
                width = self._plot_bounds[2]
                span = max(self._x_values[-1] - self._x_values[0], 1)
                marker_x = width * (pixel - self._x_values[0]) / span
                available = max(width - readout.preferred_width, 1)
                left = marker_x - readout.preferred_width - dp(12)
                readout_x = left if left >= 0 else marker_x + dp(12)
                readout.anchor = (min(readout_x / available, 1), readout.default_anchor[1])
            readout.place(self._plot_bounds, reverse_horizontal_axis=self.reverse_horizontal_axis)

        show_difference = (
            self.cursor_settings.show_difference and selected != reference and selected in points and reference in points
        )
        self._difference_readout.opacity = float(show_difference)
        if show_difference:
            self._difference_readout.apply_style(self.cursor_settings.readout_size, CARD_BORDER_RGBA)
            pixels, signal = marker_delta(points[reference], points[selected])
            position = f"{pixels:+d} px"
            if selected in wavelengths and reference in wavelengths:
                position += f"   {wavelengths[selected] - wavelengths[reference]:+.2f} nm"
            self._difference_readout.text = (
                f"[b]Δ M{selected} − M{reference}[/b]   {position}\n{signal:+.4f} {self._signal_units}"
            )
            if not self._difference_readout.manually_placed:
                self._difference_readout.anchor = (0.98, 0.96 if self._plot_bounds[2] >= dp(590) else 0.03)
            self._difference_readout.place(self._plot_bounds, reverse_horizontal_axis=self.reverse_horizontal_axis)

    def _place_marker(self, index: int) -> None:
        pixel = int(self._x_values[index])
        if marker_value(self._x_values, self._y_values, pixel) is None:
            return
        if not self.markers.adding and self.markers.pixels.get(self.markers.selected) == pixel:
            return
        number = self.markers.place(pixel)
        if number not in self._readouts:
            vertical_slots = (0.95, 0.66, 0.37, 0.08)
            anchor = (0.0, vertical_slots[len(self._readouts) % len(vertical_slots)])
            color = self._marker_color(number)
            readout = MarkerReadout(
                anchor=anchor, width=186, accent=color,
                on_press=lambda double_tap: self._begin_marker_click(number, double_tap),
                on_click=lambda double_click: self._finish_marker_click(number, double_click),
            )
            self._readouts[number] = readout
            self.add_widget(readout, canvas="after")
        self._redraw()
        self._notify_marker_state()

    def on_touch_move(self, touch) -> bool:
        if touch.grab_current is self:
            pick = touch.ud.get(self)
            if pick is not None:
                number, origin, _ = pick
                if not _marker_drag_started(origin, touch):
                    return True
                touch.ud.pop(self)
                self.select_marker(number)
        return super().on_touch_move(touch)

    def on_touch_up(self, touch) -> bool:
        pick = touch.ud.pop(self, None) if touch.grab_current is self else None
        if pick is None:
            return super().on_touch_up(touch)
        number, origin, double_click = pick
        if _marker_drag_started(origin, touch):
            self.select_marker(number)
            return super().on_touch_up(touch)
        touch.ungrab(self)
        self._finish_marker_click(number, double_click)
        return True

    def _marker_under_pointer(self, x: float, y: float) -> int | None:
        left, bottom, width, height = self._plot_bounds
        first = self._x_values[0]
        x_origin, x_scale = self._horizontal_transform(left, width)
        point_only = self.cursor_settings.line_style == "point_only"
        radius = dp(CURSOR_POINT_RADII[self.cursor_settings.point_size])
        hit_limit = radius + dp(3) if point_only else dp(7)
        hits = []
        for number in self.markers.pixels:
            point = self._marker_point(number)
            if point is None:
                continue
            pixel, value = point
            dx = x - (x_origin + (pixel - first) * x_scale)
            distance = abs(dx)
            if point_only:
                clamped = min(max(value, self._adc_min), self._adc_max)
                point_y = bottom + (clamped - self._adc_min) * height / (self._adc_max - self._adc_min)
                distance = hypot(dx, y - point_y)
            if distance <= hit_limit:
                hits.append((distance, number))
        return min(hits)[1] if hits else None

    def _update_cursor_from_position(self, touch_x: float, *, touch=None) -> bool:
        if self._plot_bounds is None or not len(self._x_values):
            return False
        left, _, width, _ = self._plot_bounds
        x_origin, x_scale = self._horizontal_transform(left, width)
        target = self._x_values[0] + (touch_x - x_origin) / x_scale
        if touch is not None and touch.grab_current is not self:
            touch.grab(self)
            if self.markers.pixels and not self.markers.adding:
                number = self._marker_under_pointer(touch_x, touch.y)
                if number is not None:
                    double_click = self._begin_marker_click(number, touch.is_double_tap)
                    touch.ud[self] = (number, touch.pos, double_click)
                    return True
            self._cancel_marker_click()
        self._last_cursor_drag_update_s = perf_counter()
        self._place_marker(nearest_index(self._x_values, target))
        return True


class SpectrumMarkerToolbar(BoxLayout):
    def __init__(self, plot: MarkerSpectrumPlot, notice, set_sensitivity: Callable[[str], bool], **kwargs) -> None:
        super().__init__(size_hint_y=None, orientation="vertical", **kwargs)
        self.plot = plot
        self.notice = notice
        self._set_sensitivity = set_sensitivity
        self.grid = GridLayout(cols=7, spacing=CARD_GAP, size_hint=(None, None))
        self.add_widget(self.grid)
        self.menu = CursorDropDown(auto_width=False, width=dp(200))
        self.marker_menu = CursorDropDown(auto_width=False, width=dp(165))
        self._pending_marker_number: int | None = None
        self.marker_menu.bind(on_select=lambda _menu, number: plot.select_marker(number))
        self.add_marker = self._control("Add Marker", self._toggle_add_marker, primary=True)
        self.marker_selector = self._control("Select Marker", self._open_marker_menu)
        for button in (
            self.add_marker, self.marker_selector,
            self._control("Min", lambda *_: self._search(maximum=False)),
            self._control("Max", lambda *_: self._search(maximum=True)),
            self._control("Prev Peak", lambda *_: self._search(maximum=True, direction=-1)),
            self._control("Next Peak", lambda *_: self._search(maximum=True, direction=1)),
            self._control("More...", self.menu.open),
        ):
            self.grid.add_widget(button)
        for text, action in (
            ("Previous Valley", lambda: self._search(maximum=False, direction=-1)),
            ("Next Valley", lambda: self._search(maximum=False, direction=1)),
            ("Search Sensitivity", self._show_sensitivity),
        ):
            self.menu.add_widget(self._control(text, lambda *_, action=action: self._menu_action(action)))
        self.set_reference_button = self._control(
            "Set as Reference", lambda *_: self._menu_action(lambda: plot.set_reference(plot.markers.selected)),
        )
        self.clear_reference_button = self._control(
            "Clear Reference", lambda *_: self._menu_action(lambda: plot.set_reference(None)),
        )
        self.remove_marker_button = self._control(
            "Remove Marker", lambda *_: self._menu_action(plot.remove_marker), destructive=True,
        )
        self.clear_markers_button = self._control(
            "Clear Markers", lambda *_: self._menu_action(plot.clear_markers), destructive=True,
        )
        for button in (
            self.set_reference_button, self.clear_reference_button, self.remove_marker_button, self.clear_markers_button,
        ):
            self.menu.add_widget(button)
        plot.on_marker_state_changed = self._update_selection
        self._update_selection()
        self.bind(width=self._resize)
        self._resize()

    @staticmethod
    def _control(text: str, action, *, primary: bool = False, destructive: bool = False) -> Button:
        face_color = APP_BACKGROUND_RGBA
        if destructive:
            face_color = DESTRUCTIVE_BUTTON_BACKGROUND_RGBA
        elif primary:
            face_color = BUTTON_BACKGROUND_RGBA
        button = RaisedActionButton(
            text=text, size_hint_y=None, height=dp(32), font_size=sp(13), face_color=face_color,
            color=BUTTON_TEXT_RGBA if primary or destructive else TEXT_PRIMARY_RGBA,
        )
        button.bind(on_release=action)
        return button

    def _resize(self, *_args) -> None:
        self.grid.width = min(self.width, dp(660))
        self.grid.cols = min(7, max(1, int((self.grid.width + CARD_GAP) / (dp(78) + CARD_GAP))))
        rows = ceil(7 / self.grid.cols)
        self.grid.height = self.height = rows * dp(32) + (rows - 1) * CARD_GAP

    def _update_selection(self) -> None:
        markers = self.plot.markers
        self.add_marker.text = "Cancel Add" if markers.adding else "Add Marker"
        self.marker_selector.text = f"Marker {markers.selected}..." if markers.selected is not None else "Select Marker"
        self.marker_selector.disabled = markers.selected is None
        self.set_reference_button.disabled = markers.selected is None or markers.selected == markers.reference
        self.clear_reference_button.disabled = markers.reference is None
        self.remove_marker_button.disabled = markers.selected is None
        self.clear_markers_button.disabled = not markers.pixels
        if self._pending_marker_number is not None and not markers.adding:
            number = self._pending_marker_number
            self.notice(f"Marker {number} placed." if number in markers.pixels else "Add Marker canceled.")
            self._pending_marker_number = None

    def _toggle_add_marker(self, *_args) -> None:
        if not self.plot.markers.adding:
            self._pending_marker_number = self.plot.markers.next_number
            self.notice("Click the plot or run a search to place a new marker.")
        self.plot.toggle_add_marker()

    def _open_marker_menu(self, button) -> None:
        self.marker_menu.clear_widgets()
        for number in self.plot.markers.pixels:
            suffix = " (reference)" if number == self.plot.markers.reference else ""
            self.marker_menu.add_widget(self._control(
                f"Marker {number}{suffix}", lambda *_, number=number: self.marker_menu.select(number),
            ))
        self.marker_menu.open(button)

    def _search(self, *, maximum: bool, direction: int = 0) -> None:
        if self.plot.search_extremum(maximum=maximum, direction=direction):
            return
        if direction:
            feature = "peak" if maximum else "valley"
            side = "left" if direction < 0 else "right"
            self.notice(f"No qualifying {feature} to the {side}.")
        else:
            self.notice("No spectrum samples are available.")

    def _menu_action(self, action) -> None:
        self.menu.dismiss()
        action()

    def _show_sensitivity(self) -> None:
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        content.add_widget(Label(text="Minimum prominence (% of displayed Y range)"))
        field = TextInput(
            text=f"{self.plot.cursor_settings.peak_sensitivity_percent:g}",
            multiline=False, size_hint_y=None, height=dp(36),
        )
        content.add_widget(field)
        popup = Popup(title="Search Sensitivity", content=content, size_hint=(None, None), size=(dp(355), dp(174)))

        def apply(*_args) -> None:
            if not self._set_sensitivity(field.text):
                field.select_all()
                field.focus = True
                return
            popup.dismiss()

        field.bind(on_text_validate=apply)
        content.add_widget(self._control("Apply", apply, primary=True))
        popup.open()


class SpectrogramPlot(Widget):
    """Purpose: draw a rolling spectrogram heatmap. Rationale: the live view should be able to show recent frame history instead of only one line plot."""

    reverse_horizontal_axis = BooleanProperty(False)

    def __init__(
        self,
        *,
        performance_monitor=None,
        performance_metric_name: str = "ui.spectrogram_redraw",
        texture_build_metric_name: str = "ui.spectrogram_texture_build",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._performance_monitor = performance_monitor
        self._performance_metric_name = performance_metric_name
        self._texture_build_metric_name = texture_build_metric_name
        self._texture: Texture | None = None
        self._texture_buffer: bytearray | None = None
        self._texture_width = 0
        self._texture_height = 0
        self._row_frame_ids: list[int] = []
        self._plot_bounds: tuple[float, float, float, float] | None = None
        self._x_grid_count = X_AXIS_TICK_COUNT
        self._y_grid_count = SPECTROGRAM_Y_GRID_COUNT
        self.bind(pos=self._redraw, size=self._redraw, reverse_horizontal_axis=self._redraw)

    def set_grid_counts(self, *, x_count: int, y_count: int) -> None:
        """Purpose: update the visible grid density. Rationale: the spectrogram should follow the same responsive layout rules as the line plot."""
        self._x_grid_count = max(int(x_count), 2)
        self._y_grid_count = max(int(y_count), 2)
        self._redraw()

    def set_frame_history(self, frame_rows: Sequence[Sequence[float]], *, frame_ids: Sequence[int] | None = None) -> None:
        """Purpose: replace the visible frame history. Rationale: the spectrogram should reuse its existing texture when the history only advanced by a few new rows instead of rebuilding everything every refresh."""
        rows = [list(row) for row in frame_rows if row]
        normalized_frame_ids = [int(frame_id) for frame_id in frame_ids[-len(rows):]] if frame_ids is not None and rows else []
        if not rows:
            self._texture = None
            self._texture_buffer = None
            self._texture_width = 0
            self._texture_height = 0
            self._row_frame_ids = []
            self._redraw()
            return

        monitor = self._performance_monitor
        with (
            monitor.measure(self._texture_build_metric_name)
            if monitor is not None
            else nullcontext()
        ):
            history_rows, history_frame_ids = self._fit_history_height(rows, normalized_frame_ids, target_height=SPECTROGRAM_MAX_ROWS)
            can_incrementally_update = len(rows) <= SPECTROGRAM_MAX_ROWS
            if can_incrementally_update and self._try_incremental_texture_update(history_rows, history_frame_ids):
                pass
            else:
                self._texture, self._texture_buffer, self._texture_width, self._texture_height = self._build_texture(history_rows)
                self._row_frame_ids = list(history_frame_ids)
        self._redraw()

    @staticmethod
    def _fit_history_height(
        frame_rows: Sequence[Sequence[float]],
        frame_ids: Sequence[int],
        *,
        target_height: int,
    ) -> tuple[list[list[float]], list[int]]:
        """Purpose: fit the full requested time history into the available texture height. Rationale: long spectrogram windows should show the entire time span instead of silently truncating to the newest rows."""
        rows = [list(row) for row in frame_rows if row]
        if not rows:
            return [], []

        safe_target_height = max(int(target_height), 1)
        normalized_frame_ids = [int(frame_id) for frame_id in frame_ids[-len(rows):]] if frame_ids else []
        if len(rows) <= safe_target_height:
            return rows, normalized_frame_ids[-len(rows):] if normalized_frame_ids else []

        target_width = max((len(row) for row in rows), default=0)
        if target_width <= 0:
            return [], []

        normalized_rows = [
            SpectrogramPlot._fit_row_width(row, target_width=target_width)
            if len(row) != target_width
            else [min(max(float(value), 0.0), 1.0) for value in row]
            for row in rows
        ]
        row_matrix = np.asarray(normalized_rows, dtype=np.float32)
        boundaries = np.linspace(0, row_matrix.shape[0], safe_target_height + 1, dtype=int)
        compressed_rows: list[list[float]] = []
        compressed_frame_ids: list[int] = []
        for bucket_index in range(safe_target_height):
            start = int(boundaries[bucket_index])
            end = max(int(boundaries[bucket_index + 1]), start + 1)
            segment = row_matrix[start:end]
            segment_peak = np.max(segment, axis=0)
            segment_rms = np.sqrt(np.mean(segment * segment, axis=0))
            blended_segment = (
                (segment_rms * (1.0 - SPECTROGRAM_TIME_ROW_PEAK_BLEND))
                + (segment_peak * SPECTROGRAM_TIME_ROW_PEAK_BLEND)
            )
            compressed_rows.append(np.clip(blended_segment, 0.0, 1.0).tolist())
            if normalized_frame_ids:
                compressed_frame_ids.append(normalized_frame_ids[min(end - 1, len(normalized_frame_ids) - 1)])
        return compressed_rows, compressed_frame_ids

    def _try_incremental_texture_update(self, frame_rows: Sequence[Sequence[float]], frame_ids: Sequence[int]) -> bool:
        """Purpose: update the current texture using only the newly arrived rows. Rationale: the rolling spectrogram usually shifts forward by a few frames, so a full texture rebuild wastes work."""
        if (
            self._texture is None
            or self._texture_buffer is None
            or self._texture_width <= 0
            or self._texture_height <= 0
            or not frame_rows
            or not frame_ids
            or len(frame_rows) != len(frame_ids)
            or len(frame_rows) != self._texture_height
            or len(self._row_frame_ids) != self._texture_height
        ):
            return False

        if any(len(row) != self._texture_width for row in frame_rows):
            return False

        existing_ids = self._row_frame_ids
        new_ids = list(frame_ids)
        if new_ids == existing_ids:
            return False

        overlap_start = None
        if new_ids and new_ids[0] in existing_ids:
            candidate_start = existing_ids.index(new_ids[0])
            overlap_count = len(existing_ids) - candidate_start
            if existing_ids[candidate_start:] == new_ids[:overlap_count]:
                overlap_start = candidate_start
        if overlap_start is None or overlap_start <= 0:
            return False

        appended_count = overlap_start
        row_stride = self._texture_width * 4
        shift_bytes = row_stride * appended_count
        self._texture_buffer[:-shift_bytes] = self._texture_buffer[shift_bytes:]

        new_rows = frame_rows[-appended_count:]
        for row_index, row in enumerate(new_rows):
            start = (self._texture_height - appended_count + row_index) * row_stride
            self._texture_buffer[start:start + row_stride] = self._encode_row_rgba(row)

        self._texture.blit_buffer(bytes(self._texture_buffer), colorfmt="rgba", bufferfmt="ubyte")
        self._row_frame_ids = new_ids
        return True

    def _build_texture(self, frame_rows: Sequence[Sequence[float]]) -> tuple[Texture | None, bytearray | None, int, int]:
        """Purpose: build one RGBA texture from recent frames. Rationale: stretching one texture is much cheaper than drawing thousands of individual heatmap cells."""
        if not frame_rows:
            return None, None, 0, 0

        target_height = max(1, min(len(frame_rows), SPECTROGRAM_MAX_ROWS))
        normalized_rows = [self._fit_row_width(row, target_width=SPECTROGRAM_MAX_COLUMNS) for row in frame_rows[:target_height]]
        target_width = max((len(row) for row in normalized_rows), default=0)
        if target_width <= 0:
            return None, None, 0, 0

        buffer = bytearray(target_width * target_height * 4)
        for row_index, row in enumerate(normalized_rows):
            row_offset = row_index * target_width * 4
            buffer[row_offset:row_offset + (target_width * 4)] = self._encode_row_rgba(row)

        texture = Texture.create(size=(target_width, target_height), colorfmt="rgba")
        texture.blit_buffer(bytes(buffer), colorfmt="rgba", bufferfmt="ubyte")
        texture.mag_filter = "nearest"
        texture.min_filter = "nearest"
        return texture, buffer, target_width, target_height

    @staticmethod
    def _fit_row_width(row: Sequence[float], target_width: int) -> list[float]:
        """Purpose: fit one prepared row to the texture width. Rationale: fallback rows should preserve a smooth value-to-color grade instead of letting one hot sample dominate an entire display bucket."""
        if not row:
            return [0.0] * target_width
        if len(row) <= target_width:
            padded = [min(max(float(value), 0.0), 1.0) for value in row]
            if len(padded) < target_width:
                padded.extend([padded[-1] if padded else 0.0] * (target_width - len(padded)))
            return padded

        source_width = len(row)
        downsampled: list[float] = []
        for column_index in range(target_width):
            start = int((column_index * source_width) / target_width)
            end = max(start + 1, int(((column_index + 1) * source_width) / target_width))
            segment_values = [min(max(float(value), 0.0), 1.0) for value in row[start:end]]
            if not segment_values:
                downsampled.append(0.0)
                continue
            segment_peak = max(segment_values)
            segment_rms = (sum(value * value for value in segment_values) / len(segment_values)) ** 0.5
            blended_value = (
                (segment_rms * (1.0 - SPECTROGRAM_COLUMN_PEAK_BLEND))
                + (segment_peak * SPECTROGRAM_COLUMN_PEAK_BLEND)
            )
            downsampled.append(min(max(blended_value, 0.0), 1.0))
        return downsampled

    def _encode_row_rgba(self, row: Sequence[float]) -> bytes:
        """Purpose: convert one normalized row into RGBA bytes. Rationale: incremental texture updates should only recolor the new rows instead of rebuilding the whole image in Python."""
        fitted_row = row if len(row) == self._texture_width and self._texture_width > 0 else self._fit_row_width(row, target_width=max(self._texture_width, 1, len(row)))
        buffer = bytearray(len(fitted_row) * 4)
        for column_index, value in enumerate(fitted_row):
            red, green, blue = self._heatmap_rgb(value)
            pixel_offset = column_index * 4
            buffer[pixel_offset] = red
            buffer[pixel_offset + 1] = green
            buffer[pixel_offset + 2] = blue
            buffer[pixel_offset + 3] = 255
        return bytes(buffer)

    @staticmethod
    def _heatmap_rgb(value: float) -> tuple[int, int, int]:
        """Purpose: map one normalized intensity to a heatmap color. Rationale: the spectrogram should follow the reference image while keeping the darkest background pixels dimmer and less visually noisy."""
        clamped = min(max(float(value), 0.0), 1.0)
        contrasted = pow(clamped, 1.14)
        color_stops = (
            (0.00, (0, 0, 4)),
            (0.08, (1, 1, 12)),
            (0.18, (6, 3, 30)),
            (0.34, (32, 10, 68)),
            (0.52, (125, 20, 126)),
            (0.70, (186, 30, 110)),
            (0.84, (231, 74, 56)),
            (0.94, (249, 142, 33)),
            (1.00, (255, 214, 92)),
        )
        for stop_index in range(1, len(color_stops)):
            start_position, start_color = color_stops[stop_index - 1]
            end_position, end_color = color_stops[stop_index]
            if contrasted <= end_position:
                span = max(end_position - start_position, 1e-9)
                blend = (contrasted - start_position) / span
                return tuple(
                    int(round(start_color[channel] + ((end_color[channel] - start_color[channel]) * blend)))
                    for channel in range(3)
                )
        return color_stops[-1][1]

    def _redraw(self, *_args) -> None:
        """Purpose: redraw the spectrogram panel. Rationale: Kivy heatmaps still need manual canvas drawing on any size or data change."""
        monitor = self._performance_monitor
        with (
            monitor.measure(self._performance_metric_name)
            if monitor is not None
            else nullcontext()
        ):
            self.canvas.clear()
            with self.canvas:
                Color(*APP_BACKGROUND_RGBA)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[PLOT_CORNER_RADIUS])

                Color(*CARD_BORDER_RGBA)
                Line(
                    rounded_rectangle=[self.x, self.y, self.width, self.height, PLOT_CORNER_RADIUS],
                    width=PLOT_BORDER_WIDTH,
                )

                if self.width <= PLOT_MIN_DRAW_SIZE or self.height <= PLOT_MIN_DRAW_SIZE:
                    return

                left = self.x + PLOT_HORIZONTAL_INNER_PAD
                bottom = self.y + PLOT_VERTICAL_INNER_PAD
                plot_width = max(self.width - (PLOT_HORIZONTAL_INNER_PAD * 2), 1.0)
                plot_height = max(self.height - (PLOT_VERTICAL_INNER_PAD * 2), 1.0)
                self._plot_bounds = (left, bottom, plot_width, plot_height)

                if self._texture is None:
                    return

                Color(1.0, 1.0, 1.0, 1.0)
                coords = self._texture.tex_coords
                if self.reverse_horizontal_axis:
                    coords = coords[2:4] + coords[:2] + coords[6:8] + coords[4:6]
                Rectangle(texture=self._texture, tex_coords=coords, pos=(left, bottom), size=(plot_width, plot_height))

                Color(*GUIDE_LINE_RGBA)
                for tick_index in range(1, self._y_grid_count - 1):
                    y_fraction = tick_index / (self._y_grid_count - 1)
                    y_pos = bottom + (plot_height * y_fraction)
                    Line(points=[left, y_pos, left + plot_width, y_pos], width=GUIDE_LINE_WIDTH)
                for tick_index in range(1, self._x_grid_count - 1):
                    x_fraction = tick_index / (self._x_grid_count - 1)
                    x_pos = left + (plot_width * x_fraction)
                    Line(points=[x_pos, bottom, x_pos, bottom + plot_height], width=GUIDE_LINE_WIDTH)


class XAxisLabels(Widget):
    """Purpose: draw x-axis tick labels for one plot. Rationale: canvas-drawn labels stay aligned to the local plot width without layout drift during resize."""
    def __init__(
        self, *, font_sp: float, text_color=TEXT_TERTIARY_RGBA,
        performance_monitor=None, performance_metric_name: str = "ui.x_axis_redraw", **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._labels: list[str] = []
        self._font_sp = float(font_sp)
        self._text_color = text_color
        self._performance_monitor = performance_monitor
        self._performance_metric_name = performance_metric_name
        self._plot_widget: SpectrumPlot | SpectrogramPlot | None = None
        self.bind(pos=self._redraw, size=self._redraw)

    def set_labels(self, labels: Sequence[str]) -> None:
        """Purpose: replace the visible tick texts. Rationale: plot refresh should update the axis labels without rebuilding widgets."""
        normalized_labels = [str(label) for label in labels]
        if normalized_labels == self._labels:
            return
        self._labels = normalized_labels
        self._redraw()

    def set_font_sp(self, font_sp_value: float) -> None:
        """Purpose: update the label font size. Rationale: axis labels should follow responsive typography changes."""
        normalized_font_sp = float(font_sp_value)
        if abs(self._font_sp - normalized_font_sp) < 1e-9:
            return
        self._font_sp = normalized_font_sp
        self._redraw()

    def set_plot_widget(self, plot_widget: SpectrumPlot | SpectrogramPlot | None) -> None:
        """Purpose: follow one plot widget's horizontal span. Rationale: x-axis labels should align to the real chart bounds instead of the surrounding layout box."""
        if self._plot_widget is plot_widget:
            return
        if self._plot_widget is not None:
            self._plot_widget.unbind(pos=self._redraw, size=self._redraw, reverse_horizontal_axis=self._redraw)
        self._plot_widget = plot_widget
        if self._plot_widget is not None:
            self._plot_widget.bind(pos=self._redraw, size=self._redraw, reverse_horizontal_axis=self._redraw)
        self._redraw()

    def _plot_horizontal_span(self) -> tuple[float, float]:
        """Purpose: return the plot's left edge and width. Rationale: labels should line up with the spectrum draw area, not just the axis widget width."""
        if self._plot_widget is None:
            return self.x, self.width
        plot_bounds = getattr(self._plot_widget, "_plot_bounds", None)
        if plot_bounds is not None:
            return float(plot_bounds[0]), float(plot_bounds[2])
        return float(self._plot_widget.x), float(self._plot_widget.width)

    def _redraw(self, *_args) -> None:
        """Purpose: redraw the x-axis labels. Rationale: custom axis widgets must repaint whenever text or size changes."""
        monitor = self._performance_monitor
        with (
            monitor.measure(self._performance_metric_name)
            if monitor is not None
            else nullcontext()
        ):
            self.canvas.clear()
            if not self._labels or self.width <= 0 or self.height <= 0:
                return

            count = max(len(self._labels), 2)
            plot_left, plot_width = self._plot_horizontal_span()
            if plot_width <= 0:
                return
            labels = self._labels
            if self._plot_widget is not None and self._plot_widget.reverse_horizontal_axis:
                labels = labels[::-1]
            with self.canvas:
                for tick_index, text in enumerate(labels):
                    core_label = CoreLabel(
                        text=text,
                        font_size=sp(self._font_sp),
                        color=self._text_color,
                    )
                    core_label.refresh()
                    texture = core_label.texture
                    if texture is None:
                        continue
                    if tick_index == 0:
                        x_pos = plot_left
                    elif tick_index == count - 1:
                        x_pos = (plot_left + plot_width) - texture.width
                    else:
                        fraction = tick_index / (count - 1)
                        x_pos = (plot_left + (plot_width * fraction)) - (texture.width / 2.0)
                    y_pos = self.y + max((self.height - texture.height) / 2.0, 0.0)
                    Color(1.0, 1.0, 1.0, 1.0)
                    Rectangle(texture=texture, pos=(x_pos, y_pos), size=texture.size)


class YAxisLabels(Widget):
    """Purpose: draw y-axis tick labels for one plot. Rationale: canvas-drawn labels can stay linearly aligned to the plot height without fragile child-layout math."""
    def __init__(self, *, font_sp: float, performance_monitor=None, performance_metric_name: str = "ui.y_axis_redraw", **kwargs) -> None:
        super().__init__(**kwargs)
        self._labels: list[str] = []
        self._font_sp = float(font_sp)
        self._performance_monitor = performance_monitor
        self._performance_metric_name = performance_metric_name
        self._plot_widget: SpectrumPlot | None = None
        self.bind(pos=self._redraw, size=self._redraw)

    def set_labels(self, labels: Sequence[str]) -> None:
        """Purpose: replace the visible y-axis texts. Rationale: the axis should be able to update without rebuilding the widget tree."""
        normalized_labels = [str(label) for label in labels]
        if normalized_labels == self._labels:
            return
        self._labels = normalized_labels
        self._redraw()

    def set_font_sp(self, font_sp_value: float) -> None:
        """Purpose: update the label font size. Rationale: y-axis text should follow responsive typography changes."""
        normalized_font_sp = float(font_sp_value)
        if abs(self._font_sp - normalized_font_sp) < 1e-9:
            return
        self._font_sp = normalized_font_sp
        self._redraw()

    def set_plot_widget(self, plot_widget: SpectrumPlot | None) -> None:
        """Purpose: follow one plot widget's vertical span. Rationale: y-axis labels should align to the actual chart height instead of the axis widget height."""
        if self._plot_widget is plot_widget:
            return
        if self._plot_widget is not None:
            self._plot_widget.unbind(pos=self._redraw, size=self._redraw)
        self._plot_widget = plot_widget
        if self._plot_widget is not None:
            self._plot_widget.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _plot_vertical_span(self) -> tuple[float, float]:
        """Purpose: return the plot's bottom edge and height. Rationale: y labels should track the real graph rectangle when the surrounding layout changes shape."""
        if self._plot_widget is None:
            return self.y, self.height
        plot_bounds = getattr(self._plot_widget, "_plot_bounds", None)
        if plot_bounds is not None:
            return float(plot_bounds[1]), float(plot_bounds[3])
        return float(self._plot_widget.y), float(self._plot_widget.height)

    def _redraw(self, *_args) -> None:
        """Purpose: redraw the y-axis labels. Rationale: custom axis widgets must repaint whenever text or size changes."""
        monitor = self._performance_monitor
        with (
            monitor.measure(self._performance_metric_name)
            if monitor is not None
            else nullcontext()
        ):
            self.canvas.clear()
            if not self._labels or self.width <= 0 or self.height <= 0:
                return

            count = max(len(self._labels), 2)
            plot_bottom, plot_height = self._plot_vertical_span()
            if plot_height <= 0:
                return
            with self.canvas:
                for tick_index, text in enumerate(self._labels):
                    core_label = CoreLabel(
                        text=text,
                        font_size=sp(self._font_sp),
                        color=TEXT_TERTIARY_RGBA,
                    )
                    core_label.refresh()
                    texture = core_label.texture
                    if texture is None:
                        continue
                    fraction = tick_index / (count - 1)
                    target_center_y = plot_bottom + (plot_height * fraction)
                    y_pos = min(
                        max(target_center_y - (texture.height / 2.0), plot_bottom),
                        (plot_bottom + plot_height) - texture.height,
                    )
                    x_pos = self.right - texture.width
                    Color(1.0, 1.0, 1.0, 1.0)
                    Rectangle(texture=texture, pos=(x_pos, y_pos), size=texture.size)


class DesktopSpectrometerApp(App):
    """Purpose: own the desktop window and all UI behavior. Rationale: Kivy apps usually centralize event handling in one app object."""
    def __init__(self, runtime: AppRuntime, **kwargs) -> None:
        """Purpose: store the runtime and widget references. Rationale: later refresh methods need access to both services and UI controls."""
        super().__init__(**kwargs)
        self.runtime = runtime
        self.title = "VIS-NIR Spectrometer"
        # These fields are filled in during `build()` and then reused by button
        # handlers and refresh timers.
        self.port_spinner: AppSpinner | None = None
        self.display_toggle_button: Button | None = None
        self.integration_input = None
        self.integration_unit = None
        self.integration_status = None
        self.wavelength_fit_order_input: TextInput | None = None
        self.pixel_mapping_input: TextInput | None = None
        self._guided_wavelengths: list[float] = []
        self._guided_mapping_popup: CalibrationDialog | None = None
        self.bias_capture_count_input: TextInput | None = None
        self.bias_vector_input: TextInput | None = None
        self.flat_field_input: TextInput | None = None
        self.qe_points_input: TextInput | None = None
        self.qe_normalization_input: TextInput | None = None
        self.status_label: Label | None = None
        self.banner_label: Label | None = None
        self._spectrum_warnings: SpectrumWarnings | None = None
        self._saturation_summary: Label | None = None
        self._saturation_activity: Label | None = None
        self._saturation_vector_input: TextInput | None = None
        self._close_after_saturation = False
        self.frame_label: Label | None = None
        self.layout_label: Label | None = None
        self.edge_label: Label | None = None
        self.refresh_rate_label: Label | None = None
        self.session_label: Label | None = None
        self.notice_label: Label | None = None
        self.log_area: TextInput | None = None
        self.performance_area: Label | None = None
        self.bias_summary_label: Label | None = None
        self.flat_field_summary_label: Label | None = None
        self.pixel_mapping_summary_label: Label | None = None
        self.qe_summary_label: Label | None = None
        self.guided_mapping_status_label: Label | None = None
        self.raw_adc_view = False
        self._live_graph_choices: tuple[RadioChoices, ...] = ()
        self._graph_mode_choices: RadioChoices | None = None
        self._time_window_choices: RadioChoices | None = None
        self._cursor_sensitivity_input: TextInput | None = None
        self.plot: MarkerSpectrumPlot | None = None
        self._marker_toolbar: SpectrumMarkerToolbar | None = None
        self._marker_toolbar_host: BoxLayout | None = None
        self.spectrogram_plot: SpectrogramPlot | None = None
        self.calibration_plot: CalibrationSpectrumPlot | None = None
        self.plot_y_axis: YAxisLabels | None = None
        self.plot_x_axis: XAxisLabels | None = None
        self.calibration_plot_x_axis: XAxisLabels | None = None
        self._plot_host: BoxLayout | None = None
        self._plot_title_label: Label | None = None
        self._plot_shell: BoxLayout | None = None
        self._plot_x_axis_shell: BoxLayout | None = None
        self._plot_x_axis_spacer: Widget | None = None
        self._plot_display_mode = PLOT_DISPLAY_MODE_WINDOWED
        self._plot_x_tick_count = X_AXIS_TICK_COUNT
        self._window_is_maximized = False
        self._last_plot_signature: tuple[object, ...] | None = None
        self._last_spectrogram_signature: tuple[object, ...] | None = None
        self._last_calibration_plot_signature: tuple[object, ...] | None = None
        self._last_spectrogram_refresh_s = 0.0
        self._last_refresh_plot_call_s = 0.0
        self._last_plot_update_s = 0.0
        self._last_performance_report_refresh_s = 0.0
        self._plot_update_times: deque[float] = deque(maxlen=48)
        self._live_display_running = True
        self._body: BoxLayout | None = None
        self._left_column: BoxLayout | None = None
        self._right_column: BoxLayout | None = None
        self._main_content_container: BoxLayout | None = None
        self._plot_card: Card | None = None
        self._calibration_manager_card: BoxLayout | None = None
        self._calibration_scroll_content: BoxLayout | None = None
        self._calibration_header_card: Card | None = None
        self._display_manager_card: BoxLayout | None = None
        self._display_scroll_content: BoxLayout | None = None
        self._display_header_card: Card | None = None
        self._header_card: Card | None = None
        self._header_title_label: Label | None = None
        self._header_top_row: BoxLayout | None = None
        self._side_panel_button: Button | None = None
        self._left_scroll: ScrollView | None = None
        self._connection_buttons: BoxLayout | None = None
        self._recording_button: Button | None = None
        self._export_session_button: Button | None = None
        self._export_worker: Thread | None = None
        self._tooltips = TooltipController()
        self._connection_card: Card | None = None
        self._workspace_card: Card | None = None
        self._command_card: Card | None = None
        self._metadata_card: Card | None = None
        self._diagnostics_card: Card | None = None
        self._performance_card: Card | None = None
        self._side_panel_cards: list[Card] = []
        self._side_panel_visible = True
        self._main_content_mode = "spectrum"
        self._current_info_label_height = INFO_LABEL_HEIGHT
        self._setting_switches: list[SettingSwitch] = []
        self._labels_for_wrapping: list[Label] = []
        self._text_inputs: list[TextInput] = []
        self._multiline_editors: list[TextInput] = []
        self._buttons: list[Button] = []
        self._section_titles: list[Label] = []
        self._info_labels: list[Label] = []
        self._small_labels: list[Label] = []

    def build(self) -> BoxLayout:
        """Purpose: construct the full desktop layout. Rationale: Kivy expects one method to create the root widget tree."""
        user_config = self.runtime.state_manager.get_user_config()
        calibration_config = self.runtime.state_manager.get_calibration_config()
        self.raw_adc_view = user_config.ui.raw_adc_view
        Window.clearcolor = APP_SURROUND_BACKGROUND_RGBA

        # Root app shell: header on top, main content below.
        root = BoxLayout(
            orientation="vertical",
            spacing=APP_GAP,
            padding=APP_GAP,
        )
        with root.canvas.before:
            Color(*APP_SURROUND_BACKGROUND_RGBA)
            root._background = Rectangle(pos=root.pos, size=root.size)  # type: ignore[attr-defined]
        root.bind(
            pos=lambda instance, _value: self._update_fill_background(instance),
            size=lambda instance, _value: self._update_fill_background(instance),
        )

        header = Card(size_hint_y=None)
        header.bind(minimum_height=header.setter("height"))
        self._header_card = header
        header_top_row = BoxLayout(orientation="horizontal", spacing=CARD_GAP, size_hint_y=None, height=HEADER_TITLE_HEIGHT)
        self._header_top_row = header_top_row
        self._header_title_label = Label(
            text=HEADER_CARD_TITLE_TEXT,
            markup=True,
            font_size=f"{TITLE_FONT_SP}sp",
            color=TEXT_PRIMARY_RGBA,
            size_hint_y=None,
            height=HEADER_TITLE_HEIGHT,
            halign="left",
            valign="middle",
        )
        self._configure_label_wrapping(self._header_title_label)
        self._header_title_label.bind(size=lambda *_args: self._update_header_text_wrapping())
        header_top_row.add_widget(self._header_title_label)
        self._side_panel_button = self._button(
            HEADER_SIDE_PANEL_BUTTON_TEXT,
            self.toggle_side_panel,
            size_hint_x=None,
            width=HEADER_SIDE_PANEL_BUTTON_WIDTH,
            size_hint_y=None,
            height=BUTTON_HEIGHT,
        )
        header_top_row.add_widget(self._side_panel_button)
        header.add_widget(header_top_row)
        self.notice_label = Label(
            text=HEADER_CARD_INITIAL_NOTICE_TEXT,
            color=NOTICE_RGBA,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=HEADER_NOTICE_HEIGHT,
        )
        self._configure_label_wrapping(self.notice_label)
        self.notice_label.bind(size=lambda *_args: self._update_header_text_wrapping())
        header.add_widget(self.notice_label)
        root.add_widget(header)

        # Body is the responsive region that flips between horizontal and vertical.
        body = BoxLayout(spacing=APP_GAP)
        root.add_widget(body)
        self._body = body

        left_scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"],
            size_hint_x=SIDEBAR_RATIO_WIDE,
        )
        body.add_widget(left_scroll)
        self._left_scroll = left_scroll
        left_scroll.bind(scroll_x=self._tooltips.dismiss, scroll_y=self._tooltips.dismiss)

        # Left column: controls and session management.
        left_column = BoxLayout(
            orientation="vertical",
            spacing=APP_GAP,
            size_hint_y=None,
        )
        left_column.bind(minimum_height=left_column.setter("height"))
        left_scroll.add_widget(left_column)
        left_scroll.bind(width=lambda _instance, value: setattr(left_column, "width", value))
        self._left_column = left_column

        # Right column: graph and diagnostics.
        right_column = BoxLayout(
            orientation="vertical",
            spacing=APP_GAP,
            size_hint_x=DETAIL_RATIO_WIDE,
        )
        body.add_widget(right_column)
        self._right_column = right_column
        main_content_container = BoxLayout(orientation="vertical", size_hint_y=1.0)
        right_column.add_widget(main_content_container)
        self._main_content_container = main_content_container

        # Connection card keeps device discovery and connect/disconnect actions together.
        connection_card = Card(size_hint_y=None)
        connection_card.bind(minimum_height=connection_card.setter("height"))
        self._connection_card = connection_card
        self._side_panel_cards.append(connection_card)
        connection_card.add_widget(self._section_title(CONNECTION_CARD_TITLE_TEXT))
        self.port_spinner = AppSpinner(
            text=user_config.serial.port or CONNECTION_CARD_PORT_PLACEHOLDER,
            values=(),
            size_hint_y=None,
            height=CONTROL_HEIGHT,
            sync_height=True,
        )
        self.port_spinner.font_size = f"{BODY_FONT_SP}sp"
        self._tooltips.register(self.port_spinner, "Select the COM port for the spectrometer connection.")
        connection_card.add_widget(self.port_spinner)
        connection_buttons = BoxLayout(size_hint_y=None, height=BUTTON_HEIGHT, spacing=CARD_GAP)
        self._connection_buttons = connection_buttons
        connection_buttons.add_widget(self._button(CONNECTION_CARD_REFRESH_BUTTON_TEXT, self.refresh_ports))
        connection_buttons.add_widget(self._button(CONNECTION_CARD_CONNECT_BUTTON_TEXT, self.connect_device))
        connection_buttons.add_widget(self._button(CONNECTION_CARD_DISCONNECT_BUTTON_TEXT, self.disconnect_device))
        connection_card.add_widget(connection_buttons)
        self.display_toggle_button = self._button(
            CONNECTION_CARD_STOP_DISPLAY_BUTTON_TEXT,
            self.toggle_live_display,
            size_hint_y=None,
            height=BUTTON_HEIGHT,
        )
        connection_card.add_widget(self.display_toggle_button)
        self.status_label = self._info_label(CONNECTION_CARD_STATUS_TEXT)
        self.banner_label = self._info_label(CONNECTION_CARD_FIRMWARE_TEXT)
        connection_card.add_widget(self.status_label)
        connection_card.add_widget(self.banner_label)

        # Workspace card opens the larger full-screen tool views.
        workspace_card = Card(
            size_hint_y=None,
            background_rgba=WORKSPACE_CARD_BACKGROUND_RGBA,
            border_rgba=WORKSPACE_CARD_BORDER_RGBA,
        )
        workspace_card.bind(minimum_height=workspace_card.setter("height"))
        self._workspace_card = workspace_card
        self._side_panel_cards.append(workspace_card)
        workspace_card.add_widget(self._section_title(WORKSPACE_CARD_TITLE_TEXT))
        workspace_card.add_widget(
            self._button(
                WORKSPACE_CARD_CALIBRATION_BUTTON_TEXT,
                self.open_calibration_manager,
                size_hint_y=None,
                height=BUTTON_HEIGHT,
            )
        )
        workspace_card.add_widget(
            self._button(
                WORKSPACE_CARD_DISPLAY_BUTTON_TEXT,
                self.open_display_manager,
                size_hint_y=None,
                height=BUTTON_HEIGHT,
            )
        )

        # Integration and recording share the existing card visibility setting.
        command_card = Card(size_hint_y=None)
        command_card.bind(minimum_height=command_card.setter("height"))
        self._command_card = command_card
        self._side_panel_cards.append(command_card)
        command_card.add_widget(self._section_title(COMMAND_CARD_TITLE_TEXT))
        command_card.add_widget(self._small_label("Hover over a control in this card for help."))
        command_card.add_widget(self._section_title("Integration time"))
        exposure_row = BoxLayout(size_hint_y=None, height=CONTROL_HEIGHT, spacing=CARD_GAP)
        unit = user_config.ui.integration_unit
        duration = format(Decimal(user_config.ui.integration_us) / UNIT_US[unit], "f")
        self.integration_input = TextInput(text=duration, multiline=False, write_tab=False)
        self._configure_text_input(
            self.integration_input, tooltip="Set how long the detector collects light per exposure.",
        )
        self.integration_unit = AppSpinner(
            text=unit,
            values=("µs", "ms", "s"),
            size_hint_x=0.35,
        )
        self._tooltips.register(self.integration_unit, "Choose microseconds, milliseconds, or seconds.")
        exposure_row.add_widget(self.integration_input)
        exposure_row.add_widget(self.integration_unit)
        command_card.add_widget(exposure_row)
        exposure_buttons = BoxLayout(size_hint_y=None, height=BUTTON_HEIGHT, spacing=CARD_GAP)
        exposure_buttons.add_widget(self._button(
            "-", lambda *_: self.step_integration(-1), tooltip="Select the next shorter supported integration time.",
        ))
        exposure_buttons.add_widget(self._button(
            "+", lambda *_: self.step_integration(1), tooltip="Select the next longer supported integration time.",
        ))
        exposure_buttons.add_widget(self._button(
            "Apply", self.apply_integration, tooltip="Send the selected integration time to the spectrometer.",
        ))
        command_card.add_widget(exposure_buttons)
        self.integration_status = self._small_label("Waiting for device timing metadata.", fit_content=False)
        self._tooltips.register(
            self.integration_status, "Shows the reported exposure and its corresponding frame rate.",
        )
        command_card.add_widget(self.integration_status)
        self._recording_button = self._button(
            COMMAND_CARD_START_BINARY_BUTTON_TEXT,
            self.toggle_binary_recording,
            tooltip="Start or stop saving full-rate frames to an HDF5 recording.",
            size_hint_y=None,
            height=BUTTON_HEIGHT,
        )
        command_card.add_widget(self._recording_button)
        self._export_session_button = self._button(
            COMMAND_CARD_EXPORT_BUTTON_TEXT,
            self.export_session,
            tooltip="After a recording with frames stops successfully, save its data and calibration history as a ZIP.",
            size_hint_y=None,
            height=BUTTON_HEIGHT,
            disabled=True,
        )
        command_card.add_widget(self._export_session_button)

        # Plot card is the main live-view area for the CCD output.
        plot_card = Card()
        self._plot_card = plot_card
        self._plot_title_label = self._section_title(SPECTRUM_CARD_TITLE_TEXT)
        plot_card.add_widget(self._plot_title_label)

        # Plot shell keeps the y-axis aligned only to the chart area, while the
        # x-axis sits underneath in its own footer row.
        plot_shell = BoxLayout(orientation="vertical", spacing=WINDOWED_PLOT_AXIS_SPACING)
        self._plot_shell = plot_shell
        plot_area_row = BoxLayout(orientation="horizontal", spacing=PLOT_AXIS_GAP, size_hint_y=1.0)
        self.plot_y_axis = YAxisLabels(
            font_sp=AXIS_FONT_SP,
            performance_monitor=self.runtime.performance_monitor,
            performance_metric_name="ui.live_y_axis_redraw",
            size_hint_x=None,
            width=AXIS_COLUMN_WIDTH,
        )
        self.plot_y_axis.set_labels([f"{tick_index * Y_AXIS_TICK_INTERVAL:.1f}" for tick_index in range(Y_AXIS_TICK_COUNT)])
        plot_area_row.add_widget(self.plot_y_axis)

        self.plot = MarkerSpectrumPlot(
            size_hint_y=1.0,
            reverse_horizontal_axis=user_config.ui.reverse_horizontal_axis,
            cursor_settings=user_config.ui.cursor,
            performance_monitor=self.runtime.performance_monitor,
            performance_metric_name="ui.live_spectrum_redraw",
        )
        self.plot.set_adc_range(0.0, 1.0)
        self.plot.set_grid_counts(x_count=self._plot_x_tick_count, y_count=Y_AXIS_TICK_COUNT)
        self.spectrogram_plot = SpectrogramPlot(
            size_hint_y=1.0,
            reverse_horizontal_axis=user_config.ui.reverse_horizontal_axis,
            performance_monitor=self.runtime.performance_monitor,
            performance_metric_name="ui.live_spectrogram_redraw",
            texture_build_metric_name="ui.live_spectrogram_texture_build",
        )
        self.spectrogram_plot.set_grid_counts(x_count=self._plot_x_tick_count, y_count=SPECTROGRAM_Y_GRID_COUNT)
        plot_host = BoxLayout(orientation="vertical", size_hint_y=1.0)
        self._plot_host = plot_host
        plot_area_row.add_widget(plot_host)
        plot_shell.add_widget(plot_area_row)

        x_axis_shell = BoxLayout(
            orientation="horizontal",
            spacing=PLOT_AXIS_GAP,
            size_hint_y=None,
            height=X_AXIS_HEIGHT,
        )
        self._plot_x_axis_shell = x_axis_shell
        self._plot_x_axis_spacer = Widget(size_hint_x=None, width=AXIS_COLUMN_WIDTH)
        x_axis_shell.add_widget(self._plot_x_axis_spacer)
        self.plot_x_axis = XAxisLabels(
            font_sp=AXIS_FONT_SP,
            performance_monitor=self.runtime.performance_monitor,
            performance_metric_name="ui.live_x_axis_redraw",
            size_hint_x=1.0,
        )
        x_axis_shell.add_widget(self.plot_x_axis)
        plot_shell.add_widget(x_axis_shell)
        self._marker_toolbar = SpectrumMarkerToolbar(self.plot, self.set_notice, self._set_cursor_sensitivity)
        self._spectrum_warnings = SpectrumWarnings(plot_card)
        controls = BoxLayout(size_hint_y=None, height=dp(32), spacing=CARD_GAP)
        marker_host = BoxLayout()
        self._marker_toolbar_host = marker_host
        marker_host.add_widget(self._marker_toolbar)
        self._marker_toolbar.bind(height=controls.setter("height"))
        controls.add_widget(marker_host)
        controls.add_widget(self._spectrum_warnings.button)
        plot_card.add_widget(controls)
        plot_card.add_widget(plot_shell)

        calibration_manager_view = BoxLayout(orientation="vertical", spacing=APP_GAP)
        calibration_manager_scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"],
        )
        calibration_manager_card = BoxLayout(
            orientation="vertical",
            spacing=APP_GAP,
            size_hint_y=None,
        )
        calibration_manager_card.bind(minimum_height=calibration_manager_card.setter("height"))
        calibration_manager_scroll.add_widget(calibration_manager_card)
        calibration_manager_scroll.bind(
            width=lambda _instance, value: setattr(calibration_manager_card, "width", value),
            scroll_x=self._tooltips.dismiss,
            scroll_y=self._tooltips.dismiss,
        )

        calibration_header_card = Card(size_hint_y=None)
        calibration_header_card.bind(minimum_height=calibration_header_card.setter("height"))
        calibration_header_card.add_widget(self._section_title(CALIBRATION_MANAGER_TITLE_TEXT))
        calibration_header_card.add_widget(self._small_label(CALIBRATION_MANAGER_SUBTITLE_TEXT))
        calibration_header_actions = BoxLayout(size_hint_y=None, height=BUTTON_HEIGHT, spacing=CARD_GAP)
        calibration_header_actions.add_widget(
            self._button(
                CALIBRATION_MANAGER_BACK_BUTTON_TEXT,
                self.show_spectrum_view,
            )
        )
        calibration_header_actions.add_widget(
            self._button(CALIBRATION_CARD_SAVE_BUTTON_TEXT, self.save_calibration)
        )
        calibration_header_card.add_widget(calibration_header_actions)
        calibration_manager_view.add_widget(calibration_header_card)
        calibration_manager_view.add_widget(calibration_manager_scroll)

        calibration_bias_card = Card(size_hint_y=None)
        calibration_bias_card.bind(minimum_height=calibration_bias_card.setter("height"))
        calibration_bias_card.add_widget(self._section_title(CALIBRATION_BIAS_CARD_TITLE_TEXT))
        calibration_bias_card.add_widget(self._small_label(CALIBRATION_BIAS_CARD_HELPER_TEXT))
        calibration_bias_card.add_widget(
            self._setting_switch(
                CALIBRATION_CARD_DARK_TEXT, calibration_config.apply_dark_subtraction,
                lambda value: self._set_correction_enabled("apply_dark_subtraction", value),
                tooltip="Subtract the shielded-pixel dark level and any matching stored dark offsets.",
            )
        )
        self.bias_capture_count_input = TextInput(
            text=str(calibration_config.bias_capture_frame_count),
            multiline=False,
            hint_text=CALIBRATION_BIAS_CAPTURE_COUNT_HINT,
            size_hint_y=None,
            height=CONTROL_HEIGHT,
        )
        self._configure_text_input(
            self.bias_capture_count_input, tooltip="Set how many covered frames to average for the bias reference.",
        )
        calibration_bias_card.add_widget(self.bias_capture_count_input)
        calibration_bias_card.add_widget(
            self._button(
                CALIBRATION_BIAS_CAPTURE_BUTTON_TEXT,
                self.capture_bias_reference,
                size_hint_y=None,
                height=BUTTON_HEIGHT,
            )
        )
        self.bias_summary_label = self._small_label(self._bias_summary_text(calibration_config))
        calibration_bias_card.add_widget(self.bias_summary_label)
        self.bias_vector_input = TextInput(
            text=self._format_float_vector(calibration_config.bias_counts),
            multiline=True,
            hint_text=CALIBRATION_BIAS_VECTOR_HINT,
            size_hint_y=None,
            height=CALIBRATION_EDITOR_HEIGHT,
        )
        self._configure_text_input(
            self.bias_vector_input, tooltip="Set the baseline ADC offset for each detector sample.",
        )
        self._register_multiline_editor(self.bias_vector_input)
        calibration_bias_card.add_widget(self.bias_vector_input)
        calibration_manager_card.add_widget(calibration_bias_card)
        calibration_manager_card.add_widget(self._build_saturation_card(calibration_config))

        calibration_wavelength_card = Card(size_hint_y=None)
        calibration_wavelength_card.bind(minimum_height=calibration_wavelength_card.setter("height"))
        calibration_wavelength_card.add_widget(self._section_title(CALIBRATION_WAVELENGTH_CARD_TITLE_TEXT))
        calibration_wavelength_card.add_widget(self._setting_switch(
            "Apply wavelength fit", calibration_config.apply_wavelength_mapping,
            lambda value: self._set_correction_enabled("apply_wavelength_mapping", value),
            tooltip="Switch between wavelength and pixel units while keeping the fit.",
        ))
        calibration_wavelength_card.add_widget(self._small_label(CALIBRATION_WAVELENGTH_CARD_HELPER_TEXT))
        calibration_wavelength_card.add_widget(self._button(
            CALIBRATION_WAVELENGTH_GUIDED_START_BUTTON_TEXT,
            self.start_guided_pixel_mapping,
            size_hint_y=None,
            height=BUTTON_HEIGHT,
        ))
        self.guided_mapping_status_label = self._small_label("")
        calibration_wavelength_card.add_widget(self.guided_mapping_status_label)
        self.pixel_mapping_summary_label = self._info_label(self._wavelength_fit_status(calibration_config))
        calibration_wavelength_card.add_widget(self.pixel_mapping_summary_label)
        self.pixel_mapping_input = TextInput(
            text=self._format_mapping_points(calibration_config.pixel_mapping_points),
            multiline=True,
            hint_text=CALIBRATION_WAVELENGTH_POINTS_HINT,
            size_hint_y=None,
            height=CALIBRATION_EDITOR_HEIGHT,
        )
        self._configure_text_input(
            self.pixel_mapping_input, tooltip="Pair detector pixel indices with known wavelengths in nanometers.",
        )
        self._register_multiline_editor(self.pixel_mapping_input)
        calibration_wavelength_card.add_widget(self.pixel_mapping_input)
        calibration_wavelength_card.add_widget(self._small_label(CALIBRATION_WAVELENGTH_FIT_ORDER_TEXT))
        wavelength_fit_row = BoxLayout(size_hint_y=None, height=BUTTON_HEIGHT, spacing=CARD_GAP)
        self.wavelength_fit_order_input = TextInput(
            text=str(calibration_config.wavelength_fit_order),
            multiline=False,
            size_hint=(0.3, None),
            height=CONTROL_HEIGHT,
            pos_hint={"center_y": 0.5},
        )
        self._configure_text_input(
            self.wavelength_fit_order_input, tooltip="Set the polynomial degree for the pixel-to-wavelength fit.",
        )
        wavelength_fit_row.add_widget(self.wavelength_fit_order_input)
        wavelength_fit_row.add_widget(
            self._button(CALIBRATION_WAVELENGTH_FIT_BUTTON_TEXT, self.fit_wavelength_coefficients_from_points)
        )
        wavelength_fit_row.add_widget(self._button(
            CALIBRATION_WAVELENGTH_GUIDED_RESET_BUTTON_TEXT,
            self.reset_guided_pixel_mapping,
            background_color=DESTRUCTIVE_BUTTON_BACKGROUND_RGBA,
        ))
        calibration_wavelength_card.add_widget(wavelength_fit_row)
        calibration_manager_card.add_widget(calibration_wavelength_card)

        calibration_flat_field_card = Card(size_hint_y=None)
        calibration_flat_field_card.bind(minimum_height=calibration_flat_field_card.setter("height"))
        calibration_flat_field_card.add_widget(self._section_title(CALIBRATION_FLAT_FIELD_CARD_TITLE_TEXT))
        calibration_flat_field_card.add_widget(self._small_label(CALIBRATION_FLAT_FIELD_CARD_HELPER_TEXT))
        calibration_flat_field_card.add_widget(
            self._setting_switch(
                CALIBRATION_CARD_INTENSITY_TEXT, calibration_config.apply_intensity_correction,
                lambda value: self._set_correction_enabled("apply_intensity_correction", value),
                tooltip="Apply the stored flat-field multipliers to correct pixel-to-pixel sensitivity.",
            )
        )
        self.flat_field_summary_label = self._info_label(
            CALIBRATION_FLAT_FIELD_SUMMARY_TEMPLATE.format(count=len(calibration_config.intensity_correction))
        )
        calibration_flat_field_card.add_widget(self.flat_field_summary_label)
        self.flat_field_input = TextInput(
            text=self._format_float_vector(calibration_config.intensity_correction),
            multiline=True,
            hint_text=CALIBRATION_FLAT_FIELD_VECTOR_HINT,
            size_hint_y=None,
            height=CALIBRATION_EDITOR_HEIGHT,
        )
        self._configure_text_input(
            self.flat_field_input, tooltip="Set a sensitivity correction multiplier for each detector sample.",
        )
        self._register_multiline_editor(self.flat_field_input)
        calibration_flat_field_card.add_widget(self.flat_field_input)
        calibration_manager_card.add_widget(calibration_flat_field_card)

        calibration_qe_card = Card(size_hint_y=None)
        calibration_qe_card.bind(minimum_height=calibration_qe_card.setter("height"))
        calibration_qe_card.add_widget(self._section_title(CALIBRATION_QE_CARD_TITLE_TEXT))
        calibration_qe_card.add_widget(self._small_label(CALIBRATION_QE_CARD_HELPER_TEXT))
        calibration_qe_card.add_widget(
            self._setting_switch(
                CALIBRATION_CARD_QE_TEXT, calibration_config.apply_quantum_efficiency_correction,
                lambda value: self._set_correction_enabled("apply_quantum_efficiency_correction", value),
                tooltip="Correct intensity for changes in detector sensitivity across wavelengths.",
            )
        )
        self.qe_summary_label = self._info_label(
            CALIBRATION_QE_SUMMARY_TEMPLATE.format(count=len(calibration_config.quantum_efficiency_points))
        )
        calibration_qe_card.add_widget(self.qe_summary_label)
        self.qe_normalization_input = TextInput(
            text=""
            if calibration_config.quantum_efficiency_normalization_wavelength_nm is None
            else str(calibration_config.quantum_efficiency_normalization_wavelength_nm),
            multiline=False,
            hint_text=CALIBRATION_QE_NORMALIZATION_HINT,
            size_hint_y=None,
            height=CONTROL_HEIGHT,
        )
        self._configure_text_input(
            self.qe_normalization_input, tooltip="Set the wavelength in nanometers where the response correction is one.",
        )
        calibration_qe_card.add_widget(self.qe_normalization_input)
        self.qe_points_input = TextInput(
            text=self._format_response_points(calibration_config.quantum_efficiency_points),
            multiline=True,
            hint_text=CALIBRATION_QE_POINTS_HINT,
            size_hint_y=None,
            height=CALIBRATION_EDITOR_HEIGHT,
        )
        self._configure_text_input(
            self.qe_points_input, tooltip="Pair wavelengths in nanometers with their measured relative response.",
        )
        self._register_multiline_editor(self.qe_points_input)
        calibration_qe_card.add_widget(self.qe_points_input)
        calibration_manager_card.add_widget(calibration_qe_card)

        self._calibration_manager_card = calibration_manager_view
        self._calibration_scroll_content = calibration_manager_card
        self._calibration_header_card = calibration_header_card

        display_manager_view = BoxLayout(orientation="vertical", spacing=APP_GAP)
        display_manager_scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"],
        )
        display_manager_card = BoxLayout(
            orientation="vertical",
            spacing=APP_GAP,
            size_hint_y=None,
        )
        display_manager_card.bind(minimum_height=display_manager_card.setter("height"))
        display_manager_scroll.add_widget(display_manager_card)
        display_manager_scroll.bind(
            width=lambda _instance, value: setattr(display_manager_card, "width", value),
            scroll_x=self._tooltips.dismiss,
            scroll_y=self._tooltips.dismiss,
        )

        display_header_card = Card(size_hint_y=None)
        display_header_card.bind(minimum_height=display_header_card.setter("height"))
        display_header_card.add_widget(self._section_title(DISPLAY_MANAGER_TITLE_TEXT))
        display_header_card.add_widget(self._small_label(DISPLAY_MANAGER_SUBTITLE_TEXT))
        display_header_actions = BoxLayout(size_hint_y=None, height=BUTTON_HEIGHT, spacing=CARD_GAP)
        display_header_actions.add_widget(
            self._button(DISPLAY_MANAGER_BACK_BUTTON_TEXT, self.show_spectrum_view)
        )
        display_header_actions.add_widget(self._button("Save Display Settings", self.save_display_settings))
        display_header_card.add_widget(display_header_actions)
        display_manager_view.add_widget(display_header_card)
        display_manager_view.add_widget(display_manager_scroll)

        display_graph_card = Card(size_hint_y=None)
        display_graph_card.bind(minimum_height=display_graph_card.setter("height"))
        display_graph_card.add_widget(self._section_title(DISPLAY_MANAGER_GRAPH_CARD_TITLE_TEXT))
        self._graph_mode_choices = RadioChoices(
            (
                (DISPLAY_MANAGER_GRAPH_MODE_SPECTRUM_TEXT, LIVE_GRAPH_MODE_SPECTRUM),
                (DISPLAY_MANAGER_GRAPH_MODE_SPECTROGRAM_TEXT, LIVE_GRAPH_MODE_SPECTROGRAM),
            ),
            self._current_live_graph_mode(),
            self._set_live_graph_mode,
        )
        data_view_choices = RadioChoices(
            (("Processed spectrum", False), ("Raw ADC - full frame", True)),
            self.raw_adc_view,
            self._set_raw_view,
        )
        spectrum_scaling_choices = RadioChoices(
            (
                (DISPLAY_MANAGER_SCALING_ABSOLUTE_TEXT, "absolute_saturation"),
                (DISPLAY_MANAGER_SCALING_AUTO_TEXT, "auto_peak"),
            ),
            calibration_config.display_normalization_mode,
            self._set_spectrum_scaling,
        )
        time_window = self._current_spectrogram_time_window_s()
        time_options = sorted({*SPECTROGRAM_TIME_WINDOW_OPTIONS_S, time_window})
        self._time_window_choices = RadioChoices(
            [(self._spectrogram_time_window_display_text(seconds), seconds) for seconds in time_options],
            time_window,
            self._set_spectrogram_time_window,
        )
        self._live_graph_choices = (
            self._graph_mode_choices, data_view_choices, spectrum_scaling_choices, self._time_window_choices,
        )
        for (label, tooltip), group in zip(
            (
                (DISPLAY_MANAGER_GRAPH_MODE_LABEL_TEXT, "Choose a line spectrum or a rolling spectrogram."),
                ("Data view", "Choose processed data or raw ADC counts for the full frame."),
                (
                    DISPLAY_MANAGER_SCALING_LABEL_TEXT,
                    "Scale intensity to the current frame peak or the detector saturation level.",
                ),
                (DISPLAY_MANAGER_SPECTROGRAM_WINDOW_LABEL_TEXT, "Set how much recent history the spectrogram shows."),
            ),
            self._live_graph_choices,
            strict=True,
        ):
            section = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(3))
            section.bind(minimum_height=section.setter("height"))
            caption = self._small_label(label)
            caption.bold = True
            section.add_widget(caption)
            self._tooltips.register(group, tooltip)
            section.add_widget(group)
            display_graph_card.add_widget(section)
        display_graph_card.add_widget(self._setting_switch(
            "Reverse Horizontal Axis",
            user_config.ui.reverse_horizontal_axis,
            self._set_horizontal_axis_reversed,
            tooltip="Mirror the spectrum and spectrogram from left to right.",
        ))
        display_manager_card.add_widget(display_graph_card)
        display_manager_card.add_widget(self._build_cursor_settings_card(user_config.ui.cursor))

        display_panels_card = Card(size_hint_y=None)
        display_panels_card.bind(minimum_height=display_panels_card.setter("height"))
        display_panels_card.add_widget(self._section_title(DISPLAY_MANAGER_PANELS_CARD_TITLE_TEXT))
        display_panels_card.add_widget(self._small_label(DISPLAY_MANAGER_PANELS_HELPER_TEXT))
        ui_config = self.runtime.state_manager.get_user_config().ui
        for label, active, handler, tooltip in (
            (
                DISPLAY_MANAGER_SHOW_COMMAND_CARD_TEXT, ui_config.show_command_card,
                self._set_command_card_visibility, "Show the integration time and recording controls in the sidebar.",
            ),
            (
                DISPLAY_MANAGER_SHOW_DIAGNOSTICS_CARD_TEXT, ui_config.show_diagnostics_card,
                self._set_diagnostics_card_visibility, "Show recent app and device messages in the sidebar.",
            ),
            (
                DISPLAY_MANAGER_SHOW_PERFORMANCE_CARD_TEXT, ui_config.show_performance_card,
                self._set_performance_card_visibility, "Show timing and throughput metrics in the sidebar.",
            ),
        ):
            display_panels_card.add_widget(self._setting_switch(label, active, handler, tooltip=tooltip))
        display_manager_card.add_widget(display_panels_card)

        display_frame_card = Card(size_hint_y=None)
        display_frame_card.bind(minimum_height=display_frame_card.setter("height"))
        display_frame_card.add_widget(self._section_title(DISPLAY_MANAGER_FRAME_CARD_TITLE_TEXT))
        display_frame_card.add_widget(self._small_label(DISPLAY_MANAGER_FRAME_HELPER_TEXT))
        frame_row_options = (
            (DISPLAY_MANAGER_SHOW_FRAME_ROW_TEXT, "show_frame_data_frame", "Show frame IDs, sample counts, and missed frames."),
            (DISPLAY_MANAGER_SHOW_LAYOUT_ROW_TEXT, "show_frame_data_layout", "Show how each frame is divided into pixel regions."),
            (DISPLAY_MANAGER_SHOW_EDGE_ROW_TEXT, "show_frame_data_edge", "Show a preview of the ADC samples at the frame edges."),
            (DISPLAY_MANAGER_SHOW_REFRESH_ROW_TEXT, "show_frame_data_refresh", "Show the live plot update rate."),
            (DISPLAY_MANAGER_SHOW_SESSION_ROW_TEXT, "show_frame_data_session", "Show buffer counts and recording status."),
        )
        for label_text, field_name, tooltip in frame_row_options:
            display_frame_card.add_widget(
                self._setting_switch(
                    label_text, getattr(ui_config, field_name),
                    lambda value, target=field_name: self._set_frame_data_visibility(target, value),
                    tooltip=tooltip,
                )
            )
        display_manager_card.add_widget(display_frame_card)

        self._display_manager_card = display_manager_view
        self._display_scroll_content = display_manager_card
        self._display_header_card = display_header_card
        self._refresh_main_content()

        metadata_card = Card(size_hint_y=None)
        metadata_card.bind(minimum_height=metadata_card.setter("height"))
        self._metadata_card = metadata_card
        self._side_panel_cards.append(metadata_card)
        metadata_card.add_widget(self._section_title("Frame Data"))
        self.frame_label = self._info_label(SPECTRUM_CARD_FRAME_LABEL_TEXT)
        self.layout_label = self._info_label(SPECTRUM_CARD_LAYOUT_LABEL_TEXT)
        self.edge_label = self._info_label(SPECTRUM_CARD_EDGE_LABEL_TEXT)
        self.refresh_rate_label = self._info_label(SPECTRUM_CARD_REFRESH_LABEL_TEXT)
        self.session_label = self._info_label(SPECTRUM_CARD_SESSION_LABEL_TEXT)
        metadata_card.add_widget(self.frame_label)
        metadata_card.add_widget(self.layout_label)
        metadata_card.add_widget(self.edge_label)
        metadata_card.add_widget(self.refresh_rate_label)
        metadata_card.add_widget(self.session_label)

        diagnostics_card = Card(size_hint_y=None)
        diagnostics_card.bind(minimum_height=diagnostics_card.setter("height"))
        self._diagnostics_card = diagnostics_card
        self._side_panel_cards.append(diagnostics_card)
        diagnostics_card.add_widget(self._section_title(DIAGNOSTICS_CARD_TITLE_TEXT))
        self.log_area = TextInput(readonly=True, multiline=True, size_hint_y=None, height=DIAGNOSTICS_CARD_TEXT_HEIGHT)
        self._configure_text_input(self.log_area)
        diagnostics_card.add_widget(self.log_area)

        performance_card = Card(size_hint_y=None)
        performance_card.bind(minimum_height=performance_card.setter("height"))
        self._performance_card = performance_card
        self._side_panel_cards.append(performance_card)
        performance_card.add_widget(self._section_title(PERFORMANCE_CARD_TITLE_TEXT))
        self.performance_area = Label(
            text="Performance Snapshot\nNo timing samples recorded yet.",
            color=TEXT_SECONDARY_RGBA,
            font_size=f"{SMALL_FONT_SP}sp",
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        self._configure_report_label(self.performance_area, min_height=PERFORMANCE_CARD_TEXT_HEIGHT)
        performance_card.add_widget(self.performance_area)

        self._apply_live_graph_mode()
        self._apply_performance_monitor_state(reset_metrics=False)
        self._apply_frame_data_label_visibility(INFO_LABEL_HEIGHT)
        self._refresh_side_panel_cards()

        Window.bind(
            size=self._apply_responsive_layout,
            on_maximize=self._handle_window_maximize,
            on_restore=self._handle_window_restore,
            on_keyboard=self._focus_choices_on_tab,
            on_key_down=self._save_settings_on_key_down,
            on_request_close=self._cancel_saturation_on_close,
        )
        self._apply_responsive_layout()

        return root

    def on_start(self) -> None:
        """Purpose: start periodic refresh tasks after the UI loads. Rationale: timers should only begin once the window exists."""
        self._tooltips.start()
        self.refresh_ports()
        # Plot refresh is allowed to run fast; status/log refresh runs slower to
        # keep the UI responsive.
        ui_config = self.runtime.state_manager.get_user_config().ui
        live_display_fps = max(float(getattr(ui_config, "live_display_fps", DEFAULT_LIVE_DISPLAY_FPS)), 1.0)
        plot_refresh_s = max(
            max(ui_config.refresh_interval_ms / 1000.0, 0.001),
            1.0 / min(live_display_fps, MAX_PLOT_REFRESH_HZ),
        )
        status_refresh_s = max(MIN_WIDE_STATUS_REFRESH_S, plot_refresh_s * 12.0)
        Clock.schedule_interval(self.refresh_plot, plot_refresh_s)
        Clock.schedule_interval(self.refresh_status, status_refresh_s)
        self.refresh_view()
        if self.runtime.state_manager.get_user_config().serial.reconnect_on_start:
            Clock.schedule_once(lambda *_args: self.connect_device(), 0.1)
        try:
            Window.maximize()
            self._window_is_maximized = True
            Clock.schedule_once(lambda *_args: self._apply_responsive_layout(), 0)
        except Exception:
            pass

    def on_stop(self) -> None:
        """Purpose: clean up the device connection on app exit. Rationale: the serial port should not be left open after closing the window."""
        self._tooltips.stop()
        Window.unbind(
            size=self._apply_responsive_layout,
            on_maximize=self._handle_window_maximize,
            on_restore=self._handle_window_restore,
            on_keyboard=self._focus_choices_on_tab,
            on_key_down=self._save_settings_on_key_down,
            on_request_close=self._cancel_saturation_on_close,
        )
        if self.runtime.transport.is_connected():
            self.runtime.command_service.disconnect()
        self.runtime.command_service.stop_binary_recording()

    def refresh_ports(self, *_args) -> None:
        """Purpose: refresh the COM-port choices shown in the UI. Rationale: devices may be plugged in or removed while the app is open."""
        ports = self.runtime.command_service.list_serial_ports()
        devices = [item["device"] for item in ports]
        if self.port_spinner is None:
            return

        # Prefer the saved port, then the current selection, then the first device found.
        self.port_spinner.values = devices
        remembered = self.runtime.state_manager.get_user_config().serial.port
        current = self.port_spinner.text if self.port_spinner.text in devices else None
        if remembered in devices:
            self.port_spinner.text = remembered
        elif current is not None:
            self.port_spinner.text = current
        elif devices:
            self.port_spinner.text = devices[0]
        else:
            self.port_spinner.text = CONNECTION_CARD_NO_PORTS_TEXT

        self.set_notice(f"Detected {len(devices)} serial port(s).")

    def connect_device(self, *_args) -> None:
        """Purpose: connect using the current UI settings. Rationale: button clicks should flow through one method that validates input first."""
        port = None if self.port_spinner is None else self.port_spinner.text
        if port == CONNECTION_CARD_NO_PORTS_TEXT:
            port = None

        result = self.runtime.command_service.connect(port=port)
        self.set_notice(result.message)
        self.refresh_view()

    def disconnect_device(self, *_args) -> None:
        """Purpose: disconnect from the current device. Rationale: the UI should expose a direct way to end the session cleanly."""
        result = self.runtime.command_service.disconnect()
        self.set_notice(result.message)
        self.refresh_view()

    def toggle_live_display(self, *_args) -> None:
        """Purpose: pause or resume the GUI-side live display. Rationale: users may want to freeze the plot temporarily without changing the device stream or backend capture flow."""
        self._live_display_running = not self._live_display_running
        self._plot_update_times.clear()
        self._last_plot_signature = None
        self._last_spectrogram_signature = None
        self._last_calibration_plot_signature = None
        self._last_spectrogram_refresh_s = 0.0
        self._update_live_display_button()
        self.refresh_plot()
        if self._live_display_running:
            self.set_notice("Live display resumed. Device streaming continued in the background.")
        else:
            self.set_notice("Live display paused. Device streaming continues in the background.")

    def _update_live_display_button(self) -> None:
        """Purpose: keep the connection-card toggle text in sync with the current GUI display state. Rationale: the button should advertise the next available action clearly."""
        if self.display_toggle_button is None:
            return
        self.display_toggle_button.text = (
            CONNECTION_CARD_STOP_DISPLAY_BUTTON_TEXT
            if self._live_display_running
            else CONNECTION_CARD_START_DISPLAY_BUTTON_TEXT
        )

    def _build_cursor_settings_card(self, settings: CursorConfig) -> Card:
        card = Card(size_hint_y=None)
        card.bind(minimum_height=card.setter("height"))
        card.add_widget(self._section_title("Cursor Settings"))
        sizes = {"Small": "small", "Standard": "standard", "Large": "large"}
        choices = (
            ("Marker line thickness", "line_thickness", {f"{step / 2:g}": step / 2 for step in range(2, 9)}),
            ("Marker line style", "line_style", {"Solid": "solid", "Dashed": "dashed", "Point only": "point_only"}),
            ("Marker point size", "point_size", sizes),
            ("Inactive marker opacity", "inactive_opacity_percent", {f"{p}%": p for p in range(25, 91, 5)}),
            ("Marker colors", "palette", {"Current": "current", "High contrast": "high_contrast"}),
            ("Readout text size", "readout_size", sizes),
            ("Readout visibility", "readout_visibility", {"All markers": "all", "Selected and reference": "selected_reference"}),
        )
        for title, name, options in choices:
            current = getattr(settings, name)
            selected = next(label for label, value in options.items() if value == current)
            spinner = AppSpinner(text=selected, values=tuple(options), sync_height=True, font_size=sp(13))
            spinner.bind(text=lambda _, label, name=name, options=options: self._set_cursor_setting(name, options[label]))
            card.add_widget(self._cursor_settings_row(title, spinner))

        for title, name in (
            ("Show signed difference", "show_difference"),
            ("Swap active marker and reference on double-click", "swap_reference_on_double_click"),
        ):
            card.add_widget(self._setting_switch(
                title, getattr(settings, name), lambda value, name=name: self._set_cursor_setting(name, value),
            ))

        sensitivity = TextInput(text=f"{settings.peak_sensitivity_percent:g}", multiline=False, input_filter="float")
        self._configure_text_input(sensitivity)
        self._cursor_sensitivity_input = sensitivity
        sensitivity.bind(
            text=lambda _, text: self._set_cursor_sensitivity(text, sync_field=False),
            on_text_validate=self._finish_cursor_sensitivity_edit,
            focus=lambda field, focused: None if focused else self._finish_cursor_sensitivity_edit(field),
        )
        card.add_widget(self._cursor_settings_row("Peak search sensitivity (%)", sensitivity))
        card.add_widget(self._button("Save Cursor Settings", self._save_cursor_settings, size_hint_y=None, height=BUTTON_HEIGHT))
        return card

    @staticmethod
    def _cursor_settings_row(title: str, control: Widget) -> BoxLayout:
        row = BoxLayout(size_hint_y=None, height=CONTROL_HEIGHT, spacing=CARD_GAP)
        label = Label(text=title, color=TEXT_PRIMARY_RGBA, font_size=sp(13), halign="left", valign="middle")
        label.bind(size=lambda widget, size: setattr(widget, "text_size", size))
        row.add_widget(label)
        row.add_widget(control)
        return row

    def _set_cursor_setting(self, name: str, value: str | bool | float) -> None:
        current = self.runtime.state_manager.get_user_config().ui.cursor
        if getattr(current, name) == value:
            return
        settings = CursorConfig.model_validate({**current.model_dump(), name: value})
        self.runtime.state_manager.set_cursor_config(settings)
        for plot in (self.plot, self.calibration_plot):
            if plot is not None:
                plot.set_cursor_settings(settings)

    def _set_cursor_sensitivity(self, text: str, *, sync_field: bool = True) -> bool:
        try:
            percent = float(text)
        except ValueError:
            return False
        if not 0 <= percent <= 100:
            return False
        self._set_cursor_setting("peak_sensitivity_percent", percent)
        if sync_field and self._cursor_sensitivity_input is not None:
            self._cursor_sensitivity_input.text = f"{percent:g}"
        return True

    def _finish_cursor_sensitivity_edit(self, field: TextInput) -> None:
        if not self._set_cursor_sensitivity(field.text):
            current = self.runtime.state_manager.get_user_config().ui.cursor
            field.text = f"{current.peak_sensitivity_percent:g}"
            self.set_notice("Peak search sensitivity must be between 0% and 100%.")

    def _save_cursor_settings(self, *_args) -> None:
        settings = self.runtime.state_manager.get_user_config().ui.cursor
        try:
            self.runtime.config_store.save_cursor(settings)
        except (OSError, ValueError):
            self.runtime.logger.exception("Could not save cursor settings")
            self.set_notice("Could not save cursor settings.")
            return
        self.set_notice("Cursor settings saved.")

    def save_user_config(self, *_args) -> None:
        """Purpose: save current connection and UI settings. Rationale: user preferences should persist across restarts."""
        path = self._save_user_config_state()
        if path is None:
            return
        self.set_notice(f"Saved user config to {path}.")

    def save_display_settings(self, *_args) -> None:
        try:
            user_config = self.runtime.config_store.load()
            user_config.ui = self.runtime.state_manager.get_user_config().ui
            calibration = self.runtime.calibration_store.load()
            scaling = self.runtime.state_manager.get_calibration_config().display_normalization_mode
            self.runtime.config_store.save(user_config)
            if calibration.display_normalization_mode != scaling:
                calibration.display_normalization_mode = scaling
                self.runtime.calibration_store.save(calibration)
        except (OSError, ValueError) as exc:
            self.runtime.logger.exception("Could not save all display settings")
            self.set_notice(f"Could not save all display settings. {exc}")
            return
        self.set_notice("Display settings saved.")

    def _save_settings_on_key_down(self, _window, key, _scan, _text, modifiers) -> bool:
        if key == ord("s") and set(modifiers or ()) - {"capslock", "numlock"} == {"ctrl"}:
            self.save_calibration()
            return True
        return False

    def _save_user_config_state(self) -> str | None:
        """Purpose: persist the current user settings without forcing a specific UI message. Rationale: calibration save should be able to keep user config in sync without duplicating the save logic."""
        if self.port_spinner is None:
            return None

        config = self.runtime.state_manager.get_user_config()
        config.serial.port = None if self.port_spinner.text == CONNECTION_CARD_NO_PORTS_TEXT else self.port_spinner.text
        path = self.runtime.config_store.save(config)
        self.runtime.command_service.apply_user_config(config)
        return str(path)

    def save_calibration(self, *_args) -> None:
        """Purpose: save the current calibration settings. Rationale: calibration changes should be editable from the desktop UI."""
        config = self._read_calibration_form()
        if config is None:
            return

        try:
            user_config_path = self._save_user_config_state()
            path = self.runtime.calibration_store.save(config)
        except (OSError, ValueError) as exc:
            self.runtime.logger.exception("Could not save all settings")
            self.set_notice(f"Could not save all settings. {exc}")
            return
        self._apply_calibration_changes(config, saved=True)
        if user_config_path is None:
            self.set_notice(f"Saved calibration config to {path}.")
        else:
            self.set_notice(f"Saved calibration config to {path} and synced user config.")

    def _set_correction_enabled(self, field: str, enabled: bool) -> None:
        config = self.runtime.state_manager.get_calibration_config()
        setattr(config, field, enabled)
        self._apply_calibration_changes(config)

    def _set_spectrum_scaling(self, mode: Literal["absolute_saturation", "auto_peak"]) -> None:
        config = self.runtime.state_manager.get_calibration_config()
        config.display_normalization_mode = mode
        self._apply_calibration_changes(config)

    def _apply_calibration_changes(
        self, config: CalibrationConfig, *, saved: bool = False, persisted_config: CalibrationConfig | None = None,
    ) -> None:
        self.runtime.command_service.apply_calibration_config(config, saved=saved, persisted_config=persisted_config)
        self._refresh_calibration_summaries(config)
        # The rebuilt frame has the same ID and may have identical sampled values.
        self._last_plot_signature = None
        self._last_calibration_plot_signature = None
        self.refresh_view()

    def _save_guided_calibration(
        self, dialog: CalibrationDialog, config: CalibrationConfig, *fields: str,
    ) -> bool:
        store = self.runtime.calibration_store
        try:
            persisted = store.load().model_copy(update={field: getattr(config, field) for field in fields})
            store.save(persisted)
        except (OSError, ValueError) as exc:
            self.runtime.logger.exception("Could not save %s", dialog.title)
            dialog.set_error(f"Could not save the calibration. {exc}")
            return False
        self._apply_calibration_changes(config, persisted_config=persisted)
        return True

    def _calibration_pixel_preview(
        self, body: BoxLayout, hint_text: str,
    ) -> Callable[..., None]:
        adc_max = (1 << self.runtime.state_manager.get_user_config().device.adc_resolution_bits) - 1
        plot = SpectrumPlot(disabled=True)
        plot.set_adc_range(0, adc_max)
        plot.set_grid_counts(x_count=5, y_count=3)
        body.add_widget(plot)
        label = Label(text="Raw ADC counts (read only)", size_hint_y=None, height=dp(22))
        body.add_widget(label)
        values = TextInput(
            multiline=True, readonly=True, cursor_width=0, write_tab=False,
            background_normal="", background_active="", background_color=(0.13, 0.15, 0.17, 1),
            foreground_color=BUTTON_TEXT_RGBA, hint_text_color=(0.69, 0.72, 0.75, 1),
            hint_text=hint_text,
        )
        body.add_widget(values)

        def show_counts(counts: Sequence[float], pixels: range, *, averaged: bool = False) -> None:
            scroll_y = values.scroll_y
            values.text = self._format_float_vector(counts)
            values.scroll_y = scroll_y
            plot.set_series(pixels, counts[pixels.start:pixels.stop])
            if averaged:
                label.text = "Averaged raw ADC counts (read only)"

        return show_counts

    def _build_saturation_card(self, config: CalibrationConfig) -> Card:
        card = Card(size_hint_y=None)
        card.bind(minimum_height=card.setter("height"))
        card.add_widget(self._section_title("Saturation Calibration"))
        card.add_widget(self._setting_switch(
            "Use calibrated limit for plot scaling",
            config.use_calibrated_saturation_scale,
            lambda value: self._set_correction_enabled("use_calibrated_saturation_scale", value),
            tooltip="Set 1.0 on the live spectrum using the calibrated white-light plateau.",
        ))
        card.add_widget(self._setting_switch(
            "Show potential saturation warning",
            config.show_potential_saturation_warning,
            lambda value: self._set_correction_enabled("show_potential_saturation_warning", value),
            tooltip="With a compatible warning reference, warn when three neighboring pixels reach 87.5% of their limits.",
        ))
        card.add_widget(self._small_label(
            "Set the plot's 1.0 reference from eight white-light frames at 1 second integration.",
        ))
        self._saturation_summary = self._small_label("")
        card.add_widget(self._saturation_summary)
        reference = config.saturation_plot_reference or config.saturation_reference
        card.add_widget(self._button(
            "Start Saturation Calibration", lambda *_: self._start_saturation_calibration(),
            size_hint_y=None, height=BUTTON_HEIGHT,
        ))
        self._saturation_activity = self._small_label("")
        card.add_widget(self._saturation_activity)
        card.add_widget(self._small_label("Averaged raw ADC counts (read only)"))
        self._saturation_vector_input = TextInput(
            text=self._format_float_vector(reference.raw_counts) if reference else "",
            multiline=True, readonly=True, cursor_width=0, write_tab=False,
            hint_text="Complete a capture to see the averaged pixel values",
            size_hint_y=None, height=CALIBRATION_EDITOR_HEIGHT,
        )
        self._configure_text_input(self._saturation_vector_input)
        self._register_multiline_editor(self._saturation_vector_input)
        card.add_widget(self._saturation_vector_input)
        return card

    def _start_saturation_calibration(self) -> None:
        activity = self._saturation_activity
        assert activity is not None
        count = DEFAULT_SATURATION_CAPTURE_FRAME_COUNT
        capture = self.runtime.command_service.saturation_capture
        result = capture.start(count)
        if not result.ok:
            activity.text = result.message
            return

        dialog = CalibrationDialog("Saturation Calibration", height=630, body_min_height=240)
        active_pixels = capture.active_pixels
        adc_max = (1 << self.runtime.state_manager.get_user_config().device.adc_resolution_bits) - 1
        preview_summary = Label(size_hint_y=None, height=dp(38), halign="left", valign="middle")
        preview_summary.bind(size=lambda label, size: setattr(label, "text_size", size))
        dialog.body.add_widget(Label(
            text=f"Active pixels {active_pixels.start}–{active_pixels.stop - 1} · ADC 0–{adc_max:,}",
            size_hint_y=None, height=dp(22),
        ))
        show_counts = self._calibration_pixel_preview(dialog.body, "Waiting for the next exposure")
        dialog.body.add_widget(preview_summary)
        confirm_button = Button(
            text="Confirm White Light", disabled=True, size_hint_y=None, height=BUTTON_HEIGHT,
        )
        dialog.body.add_widget(confirm_button)

        stages = {
            "cover_ready": ("Setup", "Cover the SMA port"),
            "covering": ("Setup", "Measuring the covered reference"),
            "covered": ("Setup", "Setting 1 second exposure"),
            "setting": ("Setup", "Setting 1 second exposure"),
            "ready": ("Setup", "Confirm white light"),
            "verifying": ("Verification", "Checking active-pixel flatness"),
            "capturing": ("Capture", "Averaging calibration frames"),
            "restore_pending": ("Exposure restore", "Restoring previous exposure"),
            "restoring": ("Exposure restore", "Restoring previous exposure"),
        }
        shown_counts = None
        cancel_requested = False

        def refresh_progress() -> None:
            nonlocal shown_counts
            phase = capture.phase
            if phase not in stages:
                return
            stage, heading = stages[phase]
            message = capture.message
            if cancel_requested:
                message = "Discarding the capture and waiting for the device to restore its previous exposure."
            dialog.set_step(heading, message, stage=stage)
            dialog.set_progress(capture.frames_collected, count, item="frames")
            preview_summary.text = capture.preview_summary
            preview_summary.height = dp(38) if preview_summary.text else 0
            confirm_button.text = "Confirm Covered" if phase in ("cover_ready", "covering") else "Confirm White Light"
            confirm_button.disabled = phase not in ("cover_ready", "ready")
            counts = capture.preview_counts
            if counts is not None and counts is not shown_counts:
                shown_counts = counts
                show_counts(counts.tolist(), active_pixels)
            activity.text = f"{heading}\n{message}"

        def confirm_light(*_args) -> None:
            capture.begin()
            refresh_progress()

        def cancel_capture(*_args) -> None:
            nonlocal cancel_requested
            cancel_requested = True
            if capture.active:
                capture.cancel()
                refresh_progress()
            else:
                activity.text = "Saturation calibration cancelled."
                self.set_notice(activity.text)
                dialog.dismiss()

        def complete_calibration(*_args) -> None:
            reference = capture.reference
            if reference is None or capture.active or cancel_requested:
                return
            config = self.runtime.state_manager.get_calibration_config()
            config.saturation_plot_reference = reference
            if not self._save_guided_calibration(dialog, config, "saturation_plot_reference"):
                return
            assert self._saturation_vector_input is not None
            self._saturation_vector_input.text = self._format_float_vector(reference.raw_counts)
            activity.text = "Saturation calibration complete and saved."
            self.set_notice(activity.text)
            dialog.dismiss()

        confirm_button.bind(on_release=confirm_light)
        dialog.cancel.bind(on_release=cancel_capture)
        dialog.primary.bind(on_release=complete_calibration)

        def update(_dt: float) -> bool:
            capture.poll()
            if capture.active:
                refresh_progress()
                return True
            activity.text = capture.message
            if cancel_requested and capture.reference is not None:
                activity.text = f"Saturation calibration cancelled. {capture.message}"
            self.set_notice(activity.text)
            if self._close_after_saturation:
                dialog.dismiss()
                self.stop()
            elif cancel_requested:
                dialog.dismiss()
            elif capture.reference is not None:
                show_counts(capture.reference.raw_counts, active_pixels, averaged=True)
                dialog.set_progress(count, count, item="frames")
                dialog.body.remove_widget(preview_summary)
                dialog.body.remove_widget(confirm_button)
                dialog.show_review(
                    f"{capture.message} The trimmed average is {capture.reference.plateau_adc:,.1f} ADC counts. "
                    "Choose Complete to save the plot reference."
                )
            else:
                confirm_button.disabled = True
                dialog.set_step("Capture ended", capture.message)
            return False

        refresh_progress()
        dialog.open()
        Clock.schedule_interval(update, 0.1)

    def _cancel_saturation_on_close(self, *_args, **_kwargs) -> bool:
        capture = self.runtime.command_service.saturation_capture
        if capture.active:
            self._close_after_saturation = True
            capture.cancel()
            return True
        return False

    def _refresh_saturation_summary(self, device: DeviceStatus, calibration: CalibrationConfig) -> None:
        if self._saturation_summary is None:
            return
        plot_reference = calibration.saturation_plot_reference
        reference = plot_reference or calibration.saturation_reference
        if reference is None:
            self._saturation_summary.text = "No measured plot reference."
        elif device.connection_state != ConnectionState.connected or device.timing_profile_id is None:
            self._saturation_summary.text = "Reference available. Connect the device to check compatibility."
        elif reference.matches(
            device.timing_profile_id, device.sample_count, device.effective_start_index, device.effective_sample_count,
            self.runtime.state_manager.get_user_config().device.adc_resolution_bits,
        ):
            if plot_reference is not None:
                self._saturation_summary.text = f"Plot reference at 1.0 · {plot_reference.plateau_adc:,.1f} ADC counts"
            else:
                self._saturation_summary.text = f"Plot reference from {reference.frame_count} frames."
        else:
            self._saturation_summary.text = "Reference is incompatible with the current timing profile or pixel layout."

    def capture_bias_reference(self, *_args) -> None:
        """Guide the operator through capturing a bias from the covered frame buffer."""
        assert self.bias_capture_count_input is not None and self.bias_vector_input is not None
        try:
            frame_count = max(int(self.bias_capture_count_input.text.strip() or "1"), 1)
        except ValueError:
            self.set_notice("Enter a whole number of frames to average for bias capture.")
            return
        buffer_limit = self.runtime.state_manager.get_user_config().ui.max_session_frames
        if frame_count > buffer_limit:
            self.set_notice(f"The current frame buffer holds up to {buffer_limit} frames for bias capture.")
            return

        dialog = CalibrationDialog("Bias Reference Calibration", height=550, body_min_height=205)
        dialog.set_step(
            "Cover the detector",
            f"Block all light and stream at least {frame_count} covered frames. "
            "Keep the exposure fixed, then choose Capture Covered Frames.",
            stage="Setup",
        )
        show_counts = self._calibration_pixel_preview(dialog.body, "Waiting for covered frames")
        capture_button = Button(text="Capture Covered Frames", size_hint_y=None, height=BUTTON_HEIGHT)
        dialog.body.add_widget(capture_button)
        dialog.set_progress(0, frame_count, item="frames")
        bias_counts: list[float] = []
        selected: list[SpectrumFrame] = []

        def capture_frames(*_args) -> None:
            nonlocal bias_counts, selected
            selected = [frame for frame in self.runtime.session_manager.frames()[-frame_count:] if frame.adc_counts]
            if len(selected) < frame_count:
                dialog.set_error(f"Waiting for {frame_count} covered frames. {len(selected)} buffered frames are available.")
                return
            identities = {(frame.timing_profile_id, frame.integration_us, len(frame.adc_counts)) for frame in selected}
            if len(identities) > 1:
                dialog.set_error("Timing, exposure, or pixel count changed. Wait for a fresh buffer of covered frames.")
                return
            bias_counts = self.runtime.calibration_manager.capture_bias_from_frames([frame.adc_counts for frame in selected])
            dialog.set_error("")
            show_counts(bias_counts, range(len(bias_counts)), averaged=True)
            dialog.set_progress(len(selected), frame_count, item="frames")
            dialog.body.remove_widget(capture_button)
            dialog.show_review(f"Averaged {len(selected)} covered frames. Choose Complete to save the bias reference.")

        def complete_calibration(*_args) -> None:
            if not bias_counts:
                return
            config = self.runtime.state_manager.get_calibration_config()
            config.bias_capture_frame_count = frame_count
            config.bias_counts = bias_counts
            config.bias_timing_profile_id = selected[-1].timing_profile_id
            config.bias_integration_us = selected[-1].integration_us
            if not self._save_guided_calibration(
                dialog, config, "bias_capture_frame_count", "bias_counts", "bias_timing_profile_id", "bias_integration_us",
            ):
                return
            self.bias_vector_input.text = self._format_float_vector(bias_counts)
            self.set_notice("Bias calibration complete and saved.")
            dialog.dismiss()

        def cancel_calibration(*_args) -> None:
            self.set_notice("Bias calibration cancelled.")
            dialog.dismiss()

        capture_button.bind(on_release=capture_frames)
        dialog.primary.bind(on_release=complete_calibration)
        dialog.cancel.bind(on_release=cancel_calibration)
        dialog.open()

    def start_guided_pixel_mapping(self, *_args) -> None:
        """Open the wavelength list before asking for peaks."""
        if self._guided_mapping_popup is not None:
            return
        assert self.pixel_mapping_input is not None
        activity = self.guided_mapping_status_label
        assert activity is not None
        activity.color = TEXT_TERTIARY_RGBA

        try:
            current_points = self._parse_mapping_points(self.pixel_mapping_input.text)
        except ValueError:
            activity.text = "Fix the existing pixel and wavelength pairs before adding guided references."
            return

        popup = CalibrationDialog("Guided Wavelength Mapping", height=440, body_min_height=150)
        popup.set_step(
            "Build your wavelength list",
            "Enter each known laser wavelength in nanometers. You'll capture the peaks in this order.",
            stage="Setup",
        )
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(8), scroll_type=["bars", "content"])
        rows_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        rows_box.bind(minimum_height=rows_box.setter("height"))
        scroll.add_widget(rows_box)
        popup.body.add_widget(scroll)
        add_button = Button(text="Add Wavelength", size_hint_y=None, height=BUTTON_HEIGHT)
        popup.body.add_widget(add_button)
        popup.primary.text = "Continue to Capture"
        rows: list[tuple[BoxLayout, Label, TextInput]] = []

        def update_rows() -> None:
            for index, (_, label, _) in enumerate(rows, start=1):
                label.text = f"Wavelength {index}"
            popup.primary.disabled = not rows
            popup.set_error("")

        def add_row(value: str = "") -> BoxLayout:
            row = BoxLayout(size_hint_y=None, height=CONTROL_HEIGHT, spacing=dp(8))
            label = Label(size_hint_x=None, width=dp(110))
            field = TextInput(text=value, hint_text="nm", multiline=False, write_tab=False)
            remove = Button(text="Remove", size_hint_x=None, width=dp(78))

            def remove_row(*_args) -> None:
                rows.remove((row, label, field))
                rows_box.remove_widget(row)
                update_rows()

            remove.bind(on_release=remove_row)
            row.add_widget(label)
            row.add_widget(field)
            row.add_widget(remove)
            rows_box.add_widget(row)
            rows.append((row, label, field))
            update_rows()
            return row

        def append_row(*_args) -> None:
            row = add_row()
            Clock.schedule_once(lambda _: scroll.scroll_to(row, animate=False) if row.parent else None)

        def begin_capture(*_args) -> None:
            wavelengths = []
            for index, (_, _, field) in enumerate(rows, start=1):
                try:
                    wavelength = self._parse_finite_float(field.text.strip())
                    if wavelength <= 0:
                        raise ValueError
                except ValueError:
                    popup.set_error(f"Enter a positive nanometer value for Wavelength {index}.")
                    field.focus = True
                    return
                if any(abs(wavelength - previous) <= 1e-9 for previous in wavelengths):
                    popup.set_error(f"Wavelength {index} duplicates an earlier entry.")
                    field.focus = True
                    return
                wavelengths.append(wavelength)
            if wavelengths:
                self._guided_wavelengths = wavelengths
                for _, _, field in rows:
                    field.focus = False
                popup.primary.unbind(on_release=begin_capture)
                self._show_guided_wavelength_capture(popup, wavelengths, current_points)

        for value in [str(wavelength) for wavelength in self._guided_wavelengths] or ["", ""]:
            add_row(value)
        add_button.bind(on_release=append_row)
        popup.primary.bind(on_release=begin_capture)
        popup.cancel.bind(on_release=popup.dismiss)

        def dismiss_setup(*_args) -> None:
            self._guided_mapping_popup = None
            if popup.primary.text == "Continue to Capture":
                activity.text = "Guided mapping cancelled."

        popup.bind(on_dismiss=dismiss_setup)
        self._guided_mapping_popup = popup
        activity.text = ""
        popup.open()

    def _show_guided_wavelength_capture(
        self, popup: CalibrationDialog, wavelengths: list[float], current_points: list[PixelMappingPoint],
    ) -> None:
        activity = self.guided_mapping_status_label
        assert activity is not None and self.pixel_mapping_input is not None
        popup.body.clear_widgets()
        popup.set_size(height=610, body_min_height=230)
        popup.set_error("")
        popup.primary.text = "Complete"
        popup.primary.disabled = True

        ui_config = self.runtime.state_manager.get_user_config().ui
        plot = CalibrationSpectrumPlot(
            cursor_settings=ui_config.cursor,
            reverse_horizontal_axis=ui_config.reverse_horizontal_axis,
            performance_monitor=self.runtime.performance_monitor,
            performance_metric_name="ui.calibration_plot_redraw",
        )
        plot.set_adc_range(0, 1)
        plot.set_grid_counts(x_count=self._plot_x_tick_count, y_count=Y_AXIS_TICK_COUNT)
        popup.body.add_widget(plot)
        axis = XAxisLabels(font_sp=AXIS_FONT_SP, text_color=BUTTON_TEXT_RGBA, size_hint_y=None, height=dp(20))
        axis.set_plot_widget(plot)
        popup.body.add_widget(axis)
        self.calibration_plot = plot
        self.calibration_plot_x_axis = axis
        self._last_calibration_plot_signature = None

        selection = Label(halign="center", valign="middle", size_hint_y=None, height=dp(36))
        selection.bind(size=lambda label, size: setattr(label, "text_size", size))
        popup.body.add_widget(selection)
        peak_controls = BoxLayout(size_hint_y=None, height=BUTTON_HEIGHT, spacing=dp(8))
        previous_peak = Button(text="Prev Peak")
        next_peak = Button(text="Next Peak")
        capture_button = Button(disabled=True, size_hint_x=1.5)
        peak_controls.add_widget(previous_peak)
        peak_controls.add_widget(next_peak)
        peak_controls.add_widget(capture_button)
        popup.body.add_widget(peak_controls)

        captured: list[PixelMappingPoint] = []
        total = len(wavelengths)
        selection_issue = ""
        accepted = False

        def show_selection(*_args) -> None:
            if len(captured) == total:
                return
            selected = plot.current_cursor_value()
            capture_button.disabled = selected is None
            if selection_issue:
                selection.text = selection_issue
            elif selected is not None:
                selection.text = f"Selected pixel {selected[0]:,} · intensity {selected[1]:.4f}"
            elif plot.has_data:
                selection.text = "Select the peak that corresponds to this laser."
            else:
                selection.text = "Waiting for a spectrum from the device."
            previous_peak.disabled = next_peak.disabled = not plot.has_data

        def show_step() -> None:
            step = len(captured)
            target = wavelengths[step]
            capture_button.text = f"Capture {target:g} nm Peak"
            popup.set_step(
                f"Calibrating {target:g} nm",
                "Shine this laser into the spectrometer. "
                "Click its peak or use Prev Peak and Next Peak. Use the arrow keys to move one pixel, then capture.",
                stage=f"Reference {step + 1} of {total}",
            )
            popup.set_progress(step, total, item="references")
            show_selection()

        def refresh_preview(_dt: float) -> None:
            self._refresh_calibration_plot(self.runtime.state_manager.latest_spectrum())
            show_selection()

        def on_pick(*_args) -> None:
            nonlocal selection_issue
            selection_issue = ""
            show_selection()

        def select_peak(direction: int) -> None:
            nonlocal selection_issue
            if plot.search_peak(direction):
                Clock.schedule_once(lambda _: setattr(plot, "focus", self.calibration_plot is plot))
            else:
                side = "left" if direction < 0 else "right"
                selection_issue = f"No qualifying peak to the {side}. Click a peak on the plot to select it."
                show_selection()

        def capture_peak(*_args) -> None:
            nonlocal selection_issue
            selected = plot.current_cursor_value()
            if len(captured) == total or selected is None:
                return
            pixel = selected[0]
            if any(point.pixel_index == pixel for point in captured):
                selection_issue = f"Pixel {pixel:,} was already captured. Select a different peak."
                show_selection()
                return
            captured.append(PixelMappingPoint(pixel_index=pixel, wavelength_nm=wavelengths[len(captured)]))
            selection_issue = ""
            plot.clear_cursor()
            if len(captured) < total:
                show_step()
                return

            preview_event.cancel()
            popup.show_review("Choose Complete to fit and save the captured wavelength references.")
            selection.text = f"Captured pixel {pixel:,} for {wavelengths[-1]:g} nm."
            popup.set_progress(total, total, item="references")
            capture_button.disabled = previous_peak.disabled = next_peak.disabled = True

        def complete_calibration(*_args) -> None:
            nonlocal accepted
            if len(captured) != total or accepted:
                return
            points = [
                point for point in current_points
                if all(abs(point.wavelength_nm - new.wavelength_nm) > 1e-9 for new in captured)
            ]
            try:
                config = self._fit_wavelength_config(points + captured)
            except ValueError as exc:
                popup.set_error(str(exc))
                return

            if not self._save_guided_calibration(
                popup, config, "pixel_mapping_points", "wavelength_fit_order", "wavelength_coefficients",
                "apply_wavelength_mapping",
            ):
                return

            self.pixel_mapping_input.text = self._format_mapping_points(config.pixel_mapping_points)
            activity.color = (0.13, 0.40, 0.22, 1)
            activity.text = "Wavelength calibration complete and saved."
            self.set_notice(activity.text)
            accepted = True
            popup.dismiss()

        def dismiss(*_args) -> None:
            preview_event.cancel()
            plot.focus = False
            plot.set_cursor_callback(None)
            self.calibration_plot = None
            self.calibration_plot_x_axis = None
            if not accepted:
                activity.text = "Guided mapping cancelled."

        previous_peak.bind(on_release=lambda *_: select_peak(-1))
        next_peak.bind(on_release=lambda *_: select_peak(1))
        capture_button.bind(on_release=capture_peak)
        popup.primary.bind(on_release=complete_calibration)
        popup.bind(on_dismiss=dismiss)
        plot.set_cursor_callback(on_pick)
        activity.text = ""
        preview_event = Clock.schedule_interval(refresh_preview, 1 / 15)
        refresh_preview(0)
        show_step()

    def reset_guided_pixel_mapping(self, *_args) -> None:
        """Purpose: clear the guided wavelength-mapping calibration state. Rationale: resetting the guided workflow should also remove the captured mapping table and restore the graph x-axis to raw pixel indices."""
        self._guided_wavelengths.clear()
        if self.pixel_mapping_input is not None:
            self.pixel_mapping_input.text = ""
        if self.guided_mapping_status_label is not None:
            self.guided_mapping_status_label.text = ""
        config = self.runtime.state_manager.get_calibration_config()
        config.pixel_mapping_points = []
        config.wavelength_coefficients = list(DEFAULT_WAVELENGTH_COEFFICIENTS)
        self._apply_calibration_changes(config)
        self.set_notice("Guided pixel mapping reset and wavelength axis returned to pixels.")

    def fit_wavelength_coefficients_from_points(self, *_args) -> CommandResult:
        def report(message: str, *, ok: bool = False) -> CommandResult:
            self.set_notice(message)
            return CommandResult(ok=ok, message=message)

        assert self.pixel_mapping_input is not None
        try:
            points = self._parse_mapping_points(self.pixel_mapping_input.text)
        except ValueError:
            return report("Check the wavelength reference points and enter a whole-number fit order.")
        try:
            config = self._fit_wavelength_config(points)
        except ValueError as exc:
            return report(str(exc))
        self._apply_calibration_changes(config)
        return report(f"Fit wavelength map from {len(points)} reference point(s). Save calibration to retain it.", ok=True)

    def _fit_wavelength_config(self, points: list[PixelMappingPoint]) -> CalibrationConfig:
        assert self.wavelength_fit_order_input is not None
        try:
            fit_order = max(int(self.wavelength_fit_order_input.text.strip() or "0"), 0)
        except ValueError as exc:
            raise ValueError("Enter a whole-number wavelength fit order.") from exc
        if len(points) < 2:
            raise ValueError("Enter at least two pixel mapping points before fitting the wavelength map.")

        try:
            coefficients = self.runtime.calibration_manager.fit_wavelength_coefficients(
                points, fit_order=fit_order, device_config=self.runtime.state_manager.get_user_config().device,
            )
        except np.linalg.LinAlgError as exc:
            raise ValueError("Could not fit the wavelength map. Check the reference points.") from exc

        config = self.runtime.state_manager.get_calibration_config()
        config.pixel_mapping_points = points
        config.wavelength_fit_order = fit_order
        config.wavelength_coefficients = coefficients
        return config

    def _read_calibration_form(self) -> CalibrationConfig | None:
        """Validate draft calibration entries before committing them."""
        assert self.wavelength_fit_order_input is not None and self.pixel_mapping_input is not None
        assert self.bias_capture_count_input is not None and self.flat_field_input is not None
        assert self.qe_points_input is not None and self.qe_normalization_input is not None
        assert self.bias_vector_input is not None
        config = self.runtime.state_manager.get_calibration_config()
        try:
            config.wavelength_fit_order = max(int(self.wavelength_fit_order_input.text.strip() or "0"), 0)
            config.bias_capture_frame_count = max(int(self.bias_capture_count_input.text.strip() or "1"), 1)
            bias_counts = self._parse_float_vector(self.bias_vector_input.text)
            config.intensity_correction = self._parse_float_vector(self.flat_field_input.text)
            config.quantum_efficiency_points = self._parse_response_points(self.qe_points_input.text)
            normalization_text = self.qe_normalization_input.text.strip()
            config.quantum_efficiency_normalization_wavelength_nm = (
                self._parse_finite_float(normalization_text) if normalization_text else None
            )
            mapping_points = self._parse_mapping_points(self.pixel_mapping_input.text)
        except (ValueError, InvalidOperation):
            self.set_notice("Check the calibration numbers, vectors, and point tables before saving.")
            return None

        if mapping_points and mapping_points != config.pixel_mapping_points:
            self.set_notice("Fit the changed wavelength reference points before saving calibration.")
            return None
        if bias_counts != config.bias_counts:
            config.bias_timing_profile_id = None
            config.bias_integration_us = None
        config.bias_counts = bias_counts
        config.pixel_mapping_points = mapping_points
        return ensure_pixel_mode_without_mapping(config)

    def export_session(self, *_args) -> None:
        if self._export_worker is not None:
            return

        recording = self.runtime.state_manager.snapshot(include_spectrum=False).recording
        if not recording.last_path or recording.active or recording.failed or not recording.frame_count:
            return
        suggested = Path(recording.last_path).with_suffix(".zip")
        try:
            destination = choose_session_zip_path(suggested.name) if sys.platform == "win32" else suggested
        except OSError as exc:
            self.set_notice(str(exc))
            return
        if destination is None:
            return

        def finish(message: str) -> None:
            self._export_worker = None
            self.set_notice(message)
            self.refresh_status()

        def export() -> None:
            result = self.runtime.command_service.export_session(destination)
            Clock.schedule_once(lambda _dt: finish(result.message))

        self._export_worker = Thread(target=export, name="session-export")
        self.set_notice("Exporting session… 0%")
        self.refresh_status()
        self._export_worker.start()

    def toggle_binary_recording(self, *_args) -> None:
        recording = self.runtime.state_manager.snapshot(include_spectrum=False).recording
        if recording.exporting or self._export_worker is not None:
            return
        service = self.runtime.command_service
        result = service.stop_binary_recording() if recording.active else service.start_binary_recording()
        self.set_notice(result.message)
        self.refresh_view()

    def step_integration(self, direction: int) -> None:
        try:
            us = Decimal(self.integration_input.text) * UNIT_US[self.integration_unit.text]
            if not us.is_finite():
                raise ValueError("Enter a finite integration time.")
            neighbors = adjacent_settings(us)
            selected = neighbors[0 if direction < 0 else 1]
            if selected is not None:
                self.integration_input.text = str(Decimal(selected) / UNIT_US[self.integration_unit.text])
        except (ValueError, InvalidOperation):
            self.set_notice("Enter a numeric integration time before stepping.")

    def apply_integration(self, *_args) -> None:
        if self.runtime.command_service.saturation_capture.active:
            self.set_notice("Finish saturation calibration before changing integration.")
            return
        unit = self.integration_unit.text
        try:
            us = parse_duration(self.integration_input.text, unit)
        except (ValueError, InvalidOperation) as exc:
            self.set_notice(str(exc))
            return

        def remember_applied(applied_us: int) -> None:
            Clock.schedule_once(lambda _dt: self._remember_integration_preference(applied_us, unit))

        result = self.runtime.command_service.integration.request(us, on_applied=remember_applied)
        self.set_notice(result.message)

    def _remember_integration_preference(self, us: int, unit: str) -> None:
        self.runtime.state_manager.set_integration_preference(us, unit)
        try:
            self.runtime.config_store.save_integration_preference(us, unit)
        except (OSError, ValueError):
            self.runtime.logger.exception("Could not save the integration preference")
            self.set_notice("Integration applied. The setting could not be saved for the next launch.")

    @staticmethod
    def _normalize_spectrogram_time_window_s(window_s: float) -> float:
        """Purpose: clamp one spectrogram time-window value to the supported range. Rationale: saved config and UI choices should never exceed the app's current supported time span."""
        return min(max(float(window_s), MIN_SPECTROGRAM_TIME_WINDOW_S), MAX_SPECTROGRAM_TIME_WINDOW_S)

    @classmethod
    def _spectrogram_time_window_display_text(cls, window_s: float) -> str:
        """Purpose: turn one spectrogram time-window value into menu text. Rationale: the display menu should show a compact human-readable duration instead of raw floats."""
        normalized_value = cls._normalize_spectrogram_time_window_s(window_s)
        if abs(normalized_value - round(normalized_value)) < 1e-9:
            return f"{int(round(normalized_value))} s"
        return f"{normalized_value:g} s"

    def _current_live_graph_mode(self) -> str:
        """Purpose: return the active live-graph mode. Rationale: one helper avoids repeating fallback logic across menu actions and refresh paths."""
        mode = self.runtime.state_manager.get_user_config().ui.live_graph_mode
        if mode in {LIVE_GRAPH_MODE_SPECTRUM, LIVE_GRAPH_MODE_SPECTROGRAM}:
            return mode
        return LIVE_GRAPH_MODE_SPECTRUM

    def _current_spectrogram_time_window_s(self) -> float:
        """Purpose: return the active spectrogram time window. Rationale: recent-frame selection and time-axis labels should share the same validated duration."""
        configured_value = self.runtime.state_manager.get_user_config().ui.spectrogram_time_window_s
        return self._normalize_spectrogram_time_window_s(configured_value)

    def _set_live_graph_mode(self, mode: str) -> None:
        """Purpose: switch the active live graph mode. Rationale: display settings should flow through one path that updates state, layout, and the visible plot."""
        normalized_mode = mode if mode in {LIVE_GRAPH_MODE_SPECTRUM, LIVE_GRAPH_MODE_SPECTROGRAM} else LIVE_GRAPH_MODE_SPECTRUM
        config = self.runtime.state_manager.get_user_config()
        if config.ui.live_graph_mode == normalized_mode:
            self._apply_live_graph_mode()
            self.refresh_plot()
            return

        config.ui.live_graph_mode = normalized_mode
        self.runtime.state_manager.set_user_config(config)
        if self._graph_mode_choices is not None:
            self._graph_mode_choices.set_selected(normalized_mode)
        self._last_spectrogram_signature = None
        self._last_spectrogram_refresh_s = 0.0
        self._apply_live_graph_mode()
        self.refresh_plot()
        if normalized_mode == LIVE_GRAPH_MODE_SPECTROGRAM:
            self.set_notice("Live graph switched to the rolling spectrogram view.")
        else:
            self.set_notice("Live graph switched to the line spectrum view.")

    def _set_spectrogram_time_window(self, window_s: float) -> None:
        """Purpose: update the visible spectrogram time span. Rationale: users should be able to trade time coverage against temporal detail from the display manager."""
        normalized_window_s = self._normalize_spectrogram_time_window_s(window_s)
        config = self.runtime.state_manager.get_user_config()
        if abs(config.ui.spectrogram_time_window_s - normalized_window_s) < 1e-9:
            self.refresh_plot()
            return

        config.ui.spectrogram_time_window_s = normalized_window_s
        self.runtime.state_manager.set_user_config(config)
        if self._time_window_choices is not None:
            self._time_window_choices.set_selected(normalized_window_s)
        self._last_spectrogram_signature = None
        self._last_spectrogram_refresh_s = 0.0
        self.refresh_plot()
        self.set_notice(f"Spectrogram time window set to {self._spectrogram_time_window_display_text(normalized_window_s)}.")

    def _set_raw_view(self, enabled: bool) -> None:
        config = self.runtime.state_manager.get_user_config()
        config.ui.raw_adc_view = enabled
        self.runtime.state_manager.set_user_config(config)
        self.raw_adc_view = enabled
        self._last_plot_signature = None
        self._apply_live_graph_mode()
        self.refresh_plot()

    def _set_horizontal_axis_reversed(self, enabled: bool) -> None:
        config = self.runtime.state_manager.get_user_config()
        config.ui.reverse_horizontal_axis = enabled
        self.runtime.state_manager.set_user_config(config)
        for plot in (self.plot, self.spectrogram_plot, self.calibration_plot):
            if plot is not None:
                plot.reverse_horizontal_axis = enabled

        try:
            saved_config = self.runtime.config_store.load()
            saved_config.ui.reverse_horizontal_axis = enabled
            self.runtime.config_store.save(saved_config)
        except (OSError, ValueError):
            self.runtime.logger.exception("Could not save horizontal axis orientation")
            self.set_notice("Could not save horizontal axis orientation.")

    def _live_plot_y_axis_labels(self) -> list[str]:
        """Purpose: return the current y-axis labels for the live plot area. Rationale: the line plot and spectrogram need different y-axis semantics."""
        if self._current_live_graph_mode() == LIVE_GRAPH_MODE_SPECTROGRAM:
            return self._spectrogram_time_axis_labels()
        if self.raw_adc_view:
            return [f"{tick_index * 4095 / (Y_AXIS_TICK_COUNT - 1):.0f}" for tick_index in range(Y_AXIS_TICK_COUNT)]
        return [f"{tick_index * Y_AXIS_TICK_INTERVAL:.1f}" for tick_index in range(Y_AXIS_TICK_COUNT)]

    def _spectrogram_source_frames(self) -> list[SpectrogramHistoryFrame]:
        """Purpose: return buffered frames inside the selected spectrogram time window. Rationale: the heatmap should track recent elapsed time instead of a hard-coded frame count."""
        monitor = self.runtime.performance_monitor
        with monitor.measure("ui.spectrogram_source_frames"):
            frames = self.runtime.session_manager.spectrogram_frames()
            if not frames:
                return []

            time_window_s = self._current_spectrogram_time_window_s()
            latest_timestamp = frames[-1].timestamp
            cutoff_timestamp = latest_timestamp - timedelta(seconds=time_window_s)
            visible_frames = [frame for frame in frames if frame.timestamp >= cutoff_timestamp]
            return visible_frames or [frames[-1]]

    def _spectrogram_time_axis_labels(self, frames: Sequence[SpectrogramHistoryFrame] | None = None) -> list[str]:
        """Purpose: build human-readable time labels for the spectrogram y-axis. Rationale: the rolling heatmap is easier to interpret when the vertical axis reads as elapsed time instead of generic oldest/newest markers."""
        active_frames = list(frames) if frames is not None else self._spectrogram_source_frames()
        if len(active_frames) < 2:
            return ["Recent", "", "", "", "Now"]

        visible_span_s = max((active_frames[-1].timestamp - active_frames[0].timestamp).total_seconds(), 0.0)
        if visible_span_s <= 0.0:
            return ["Recent", "", "", "", "Now"]

        labels: list[str] = []
        for tick_index in range(SPECTROGRAM_Y_GRID_COUNT):
            if tick_index == SPECTROGRAM_Y_GRID_COUNT - 1:
                labels.append("Now")
                continue
            seconds_ago = visible_span_s * (1.0 - (tick_index / (SPECTROGRAM_Y_GRID_COUNT - 1)))
            labels.append(f"-{self._format_elapsed_time_label(seconds_ago)}")
        return labels

    @staticmethod
    def _format_elapsed_time_label(seconds_value: float) -> str:
        """Purpose: format one elapsed-time value for axis labels. Rationale: the spectrogram time scale should stay compact while still reading cleanly across short and long windows."""
        normalized_value = max(float(seconds_value), 0.0)
        if normalized_value >= 60.0:
            minutes = normalized_value / 60.0
            if abs(minutes - round(minutes)) < 0.05:
                return f"{int(round(minutes))}m"
            return f"{minutes:.1f}m"
        if normalized_value >= 10.0:
            return f"{normalized_value:.0f}s"
        if normalized_value >= 1.0:
            if abs(normalized_value - round(normalized_value)) < 0.05:
                return f"{int(round(normalized_value))}s"
            return f"{normalized_value:.1f}s"
        return f"{normalized_value * 1000.0:.0f}ms"

    def _apply_live_graph_mode(self) -> None:
        """Purpose: swap the active live graph widget and labels. Rationale: the main plot shell should be able to switch views without rebuilding the whole page."""
        if self._plot_host is None or self.plot_y_axis is None or self.plot_x_axis is None:
            return

        mode = self._current_live_graph_mode()
        active_plot: Widget | None = self.plot if mode == LIVE_GRAPH_MODE_SPECTRUM else self.spectrogram_plot
        if active_plot is None:
            return

        current_child = self._plot_host.children[0] if self._plot_host.children else None
        if current_child is not active_plot:
            self._plot_host.clear_widgets()
            self._plot_host.add_widget(active_plot)

        self.plot_y_axis.set_plot_widget(active_plot)
        self.plot_x_axis.set_plot_widget(active_plot)
        self.plot_y_axis.set_labels(self._live_plot_y_axis_labels())
        if self._plot_title_label is not None:
            if mode == LIVE_GRAPH_MODE_SPECTROGRAM:
                plot_title = SPECTROGRAM_CARD_TITLE_TEXT
            else:
                plot_title = "Raw ADC" if self.raw_adc_view else SPECTRUM_CARD_TITLE_TEXT
            self._plot_title_label.text = f"[b]{plot_title}[/b]"
        marker_host = self._marker_toolbar_host
        if self._marker_toolbar is not None and marker_host is not None:
            if mode == LIVE_GRAPH_MODE_SPECTRUM:
                if self._marker_toolbar.parent is None:
                    marker_host.add_widget(self._marker_toolbar)
                marker_host.parent.height = self._marker_toolbar.height
            elif self._marker_toolbar.parent is marker_host:
                self._marker_toolbar.menu.dismiss()
                self._marker_toolbar.marker_menu.dismiss()
                marker_host.remove_widget(self._marker_toolbar)
                marker_host.parent.height = dp(32)

    def _has_visible_frame_data(self) -> bool:
        """Purpose: report whether any frame-data rows are enabled. Rationale: the side panel should hide the whole Frame Data card when every row inside it is turned off."""
        ui_config = self.runtime.state_manager.get_user_config().ui
        return any(
            (
                ui_config.show_frame_data_frame,
                ui_config.show_frame_data_layout,
                ui_config.show_frame_data_edge,
                ui_config.show_frame_data_refresh,
                ui_config.show_frame_data_session,
            )
        )

    def _visible_side_panel_cards(self) -> list[Card]:
        """Purpose: return the cards that should currently appear in the side panel. Rationale: display settings can hide selected panels without removing their underlying widgets from the app."""
        ui_config = self.runtime.state_manager.get_user_config().ui
        cards: list[Card] = []
        if self._connection_card is not None:
            cards.append(self._connection_card)
        if self._workspace_card is not None:
            cards.append(self._workspace_card)
        if ui_config.show_command_card and self._command_card is not None:
            cards.append(self._command_card)
        if self._has_visible_frame_data() and self._metadata_card is not None:
            cards.append(self._metadata_card)
        if ui_config.show_performance_card and self._performance_card is not None:
            cards.append(self._performance_card)
        if ui_config.show_diagnostics_card and self._diagnostics_card is not None:
            cards.append(self._diagnostics_card)
        return cards

    def _apply_frame_data_label_visibility(self, info_height: float | None = None) -> None:
        """Purpose: resize each frame-data row to match the current visibility choices. Rationale: hidden rows should stop consuming card height instead of only fading visually."""
        if info_height is not None:
            self._current_info_label_height = info_height

        ui_config = self.runtime.state_manager.get_user_config().ui
        label_visibility_pairs = (
            (self.frame_label, ui_config.show_frame_data_frame),
            (self.layout_label, ui_config.show_frame_data_layout),
            (self.edge_label, ui_config.show_frame_data_edge),
            (self.refresh_rate_label, ui_config.show_frame_data_refresh),
            (self.session_label, ui_config.show_frame_data_session),
        )
        for label, is_visible in label_visibility_pairs:
            if label is None:
                continue
            label.opacity = 1.0 if is_visible else 0.0
            label.height = self._current_info_label_height if is_visible else 0

    def _set_frame_data_visibility(self, field_name: str, is_visible: bool) -> None:
        """Purpose: toggle one frame-data row from the display menu. Rationale: the frame-data card should be configurable without hard-coded row visibility."""
        config = self.runtime.state_manager.get_user_config()
        if not hasattr(config.ui, field_name):
            return

        had_visible_rows = any(
            (
                config.ui.show_frame_data_frame,
                config.ui.show_frame_data_layout,
                config.ui.show_frame_data_edge,
                config.ui.show_frame_data_refresh,
                config.ui.show_frame_data_session,
            )
        )
        setattr(config.ui, field_name, bool(is_visible))
        self.runtime.state_manager.set_user_config(config)
        self._apply_frame_data_label_visibility()
        if had_visible_rows != self._has_visible_frame_data():
            self._refresh_side_panel_cards()

    def _set_command_card_visibility(self, is_visible: bool) -> None:
        """Purpose: show or hide the Session And Commands card. Rationale: the display menu should control whether debugging and export tools stay in the side panel."""
        config = self.runtime.state_manager.get_user_config()
        config.ui.show_command_card = bool(is_visible)
        self.runtime.state_manager.set_user_config(config)
        self._refresh_side_panel_cards()

    def _set_diagnostics_card_visibility(self, is_visible: bool) -> None:
        """Purpose: show or hide the Diagnostics card. Rationale: the display menu should let users reclaim side-panel space when logs are not needed."""
        config = self.runtime.state_manager.get_user_config()
        config.ui.show_diagnostics_card = bool(is_visible)
        self.runtime.state_manager.set_user_config(config)
        self._refresh_side_panel_cards()

    def _set_performance_card_visibility(self, is_visible: bool) -> None:
        """Purpose: show or hide the Performance card. Rationale: timing instrumentation should be easy to inspect without always taking space in the side panel."""
        config = self.runtime.state_manager.get_user_config()
        config.ui.show_performance_card = bool(is_visible)
        self.runtime.state_manager.set_user_config(config)
        self._apply_performance_monitor_state(reset_metrics=bool(is_visible))
        self._refresh_side_panel_cards()

    def _performance_card_enabled(self) -> bool:
        """Purpose: report whether performance sampling should run at all. Rationale: hidden performance tooling should not keep perturbing the data path."""
        return bool(self.runtime.state_manager.get_user_config().ui.show_performance_card)

    def _performance_card_visible(self) -> bool:
        """Purpose: report whether the performance readout is currently visible. Rationale: expensive report formatting should only happen when the user can actually see the card."""
        return self._performance_card_enabled() and self._side_panel_visible

    def _apply_performance_monitor_state(self, *, reset_metrics: bool) -> None:
        """Purpose: synchronize the performance monitor with the Performance card toggle. Rationale: disabling the card should also pause metric collection so diagnostics stop affecting throughput."""
        monitor = self.runtime.performance_monitor
        if reset_metrics:
            monitor.reset()
            self._last_performance_report_refresh_s = 0.0
        monitor.set_enabled(self._performance_card_enabled())
        if self.performance_area is None:
            return
        self.performance_area.text = (
            PERFORMANCE_CARD_COLLECTING_TEXT
            if self._performance_card_enabled()
            else PERFORMANCE_CARD_PAUSED_TEXT
        )
        self.performance_area.texture_update()
        self._update_report_label_geometry(self.performance_area)

    @staticmethod
    def _build_fallback_spectrogram_row(display_values: Sequence[float]) -> list[float]:
        """Purpose: build one emergency spectrogram row from the current live display values. Rationale: the heatmap should still have something to draw if older frames predate the new backend row cache."""
        if not display_values:
            return []
        return SpectrogramPlot._fit_row_width(display_values, target_width=SPECTROGRAM_MAX_COLUMNS)

    def _build_spectrogram_rows(
        self,
        spectrogram_frames: Sequence[SpectrogramHistoryFrame | SpectrumFrame],
        display_values: Sequence[float],
        expected_samples: int,
    ) -> tuple[list[list[float]], list[int]]:
        """Purpose: gather prepared spectrogram rows for the visible history. Rationale: the main thread should mostly collect backend-prepared rows instead of recomputing and downsampling entire frames."""
        monitor = self.runtime.performance_monitor
        with monitor.measure("ui.build_spectrogram_rows"):
            rows: list[list[float]] = []
            frame_ids: list[int] = []
            for frame in spectrogram_frames:
                if frame.spectrogram_row:
                    rows.append(list(frame.spectrogram_row))
                    frame_ids.append(int(frame.frame_id))
                    continue

                # Compatibility fallback for frames captured before the new
                # backend-prepared spectrogram rows existed.
                plot_source = getattr(frame, "live_display_counts", None) or getattr(frame, "adc_counts", None)
                if not plot_source:
                    continue

                total_samples = len(plot_source)
                if total_samples >= expected_samples:
                    start = getattr(frame, "effective_start_index", 0)
                    end = min(start + getattr(frame, "effective_sample_count", total_samples), total_samples)
                    raw_values = plot_source[start:end]
                else:
                    raw_values = plot_source

                if not raw_values:
                    continue

                if getattr(frame, "live_display_counts", None):
                    normalized_row = self._build_fallback_spectrogram_row(raw_values)
                else:
                    row_peak = max((float(value) for value in raw_values), default=1.0)
                    denominator = max(row_peak, 1.0)
                    normalized_row = self._build_fallback_spectrogram_row(
                        [min(max(float(value) / denominator, 0.0), 1.0) for value in raw_values]
                    )
                rows.append(normalized_row)
                frame_ids.append(int(frame.frame_id))

            if not rows and display_values:
                rows.append(self._build_fallback_spectrogram_row(display_values))
                if spectrogram_frames:
                    frame_ids.append(int(spectrogram_frames[-1].frame_id))
            return rows, frame_ids

    def _spectrogram_refresh_due(self) -> bool:
        """Purpose: decide whether the rolling spectrogram should redraw now. Rationale: the heatmap should update at a lower fixed rate than the rest of the UI while still consuming every captured frame from history."""
        if self._last_spectrogram_signature is None:
            return True
        elapsed_s = perf_counter() - self._last_spectrogram_refresh_s
        return elapsed_s >= (1.0 / MAX_SPECTROGRAM_REFRESH_HZ)

    def _refresh_exposure_warnings(self, device: DeviceStatus, calibration: CalibrationConfig) -> None:
        warnings = self._spectrum_warnings
        if warnings is None:
            return
        active_us = device.integration_us
        bias_us = calibration.bias_integration_us
        dark_us = calibration.dark_integration_us
        bias_warning = None
        dark_warning = None
        if (
            device.connection_state == ConnectionState.connected
            and calibration.bias_counts
            and active_us is not None
            and bias_us is not None
            and active_us != bias_us
        ):
            bias_warning = (
                "[b]Bias reference exposure mismatch[/b]\n"
                f"Bias captured at {bias_us:,} µs. Active integration is {active_us:,} µs. "
                "This mismatch can affect readings.\n"
                f"Set integration to {bias_us:,} µs or cover the detector and capture a new bias reference at the active exposure."
            )
        if (
            device.connection_state == ConnectionState.connected
            and calibration.apply_dark_subtraction
            and calibration.dark_offset_counts
            and active_us is not None
            and dark_us is not None
            and active_us != dark_us
        ):
            dark_warning = (
                "[b]Dark calibration exposure mismatch[/b]\n"
                f"Dark calibration was captured at {dark_us:,} µs. Active integration is {active_us:,} µs. "
                "Stored dark offsets are bypassed.\n"
                f"Set integration to {dark_us:,} µs or load dark offsets measured at the active exposure."
            )
        warnings.set_warning("bias_exposure", bias_warning, DARK_INTEGRATION_WARNING_RGBA)
        warnings.set_warning("dark_exposure", dark_warning, DARK_INTEGRATION_WARNING_RGBA)

    def refresh_status(self, *_args) -> None:
        """Purpose: refresh slower-changing text fields. Rationale: status labels and logs do not need the same rate as the plot."""
        monitor = self.runtime.performance_monitor
        with monitor.measure("ui.refresh_status"):
            monitor.increment("ui.refresh_status_calls")
            snapshot = self.runtime.state_manager.snapshot(include_spectrum=False)
            calibration = self.runtime.state_manager.get_calibration_config()
            self._refresh_saturation_summary(snapshot.device, calibration)
            self._refresh_exposure_warnings(snapshot.device, calibration)
            if self._spectrum_warnings is not None:
                overload = (
                    "[b]Signal overload detected[/b]\n"
                    "The detector waveform is distorted. Reduce the light input and wait for the signal to stabilize."
                    if snapshot.device.connection_state == ConnectionState.connected and snapshot.device.signal_overload
                    else None
                )
                self._spectrum_warnings.set_warning("overload", overload, SATURATION_WARNING_RGBA)
            recording = snapshot.recording
            exporting = recording.exporting or self._export_worker is not None
            if self._recording_button is not None:
                self._recording_button.text = (
                    COMMAND_CARD_STOP_BINARY_BUTTON_TEXT if recording.active else COMMAND_CARD_START_BINARY_BUTTON_TEXT
                )
                self._recording_button.background_color = (
                    STOP_RECORDING_BUTTON_BACKGROUND_RGBA if recording.active else BUTTON_BACKGROUND_RGBA
                )
                self._recording_button.disabled = exporting
            if self._export_session_button is not None:
                self._export_session_button.disabled = (
                    recording.active or recording.failed or recording.frame_count == 0 or exporting
                )
            if recording.export_percent is not None:
                self.set_notice(f"Exporting session… {recording.export_percent}%")
            if self.integration_status is not None:
                us = snapshot.device.integration_us
                rate = f"{1_000_000 / frame_interval_us(us):.6g} Hz" if us else "unknown rate"
                self.integration_status.text = (
                    f"{snapshot.device.integration_state}: {us if us is not None else 'unknown'} µs, {rate}\n"
                    f"{snapshot.device.integration_message}")

            # Connection and firmware banner fields summarize the device state.
            if self.status_label is not None:
                port_text = snapshot.device.port or ""
                self.status_label.text = f"Status: {snapshot.device.connection_state.value} {port_text}".strip()

            if self.banner_label is not None:
                banner_text = (
                    snapshot.device.firmware_messages[-1]
                    if snapshot.device.firmware_messages
                    else "waiting for banner"
                )
                self.banner_label.text = f"Firmware: {banner_text}"

            if self.frame_label is not None:
                self.frame_label.text = (
                    f"Frame: {snapshot.device.frame_counter} | samples={snapshot.device.sample_count} "
                    f"| missed={snapshot.device.missed_frames} | flags=0x{snapshot.device.last_frame_flags:04X}"
                )

            if self.session_label is not None:
                recording_text = "recording=off"
                if snapshot.recording.active:
                    recording_text = (
                        f"recording=on frames={snapshot.recording.frame_count} "
                        f"queue={snapshot.recording.queue_depth}"
                    )
                elif snapshot.recording.failed:
                    recording_text = f"recording=failed {snapshot.recording.error or ''}".strip()
                self.session_label.text = (
                    f"Session {snapshot.session.session_id} | buffered={snapshot.session.frames_buffered} "
                    f"| dropped={snapshot.session.dropped_frames} | {recording_text}"
                )

            if self.edge_label is not None:
                self.edge_label.text = f"Edge samples: {snapshot.device.sample_preview or 'n/a'}"

            if self.log_area is not None:
                recent_logs = "\n".join(snapshot.logs[-DIAGNOSTICS_LOG_HISTORY_LINES:])
                spectrum = self.runtime.state_manager.latest_spectrum()
                reference = f"{spectrum.reference_status}\n\n" if spectrum is not None else ""
                self.log_area.text = reference + (recent_logs or "No recent log messages.")

            if self.performance_area is not None and self._performance_card_visible():
                now_s = perf_counter()
                if (
                    self._last_performance_report_refresh_s <= 0.0
                    or (now_s - self._last_performance_report_refresh_s) >= PERFORMANCE_REPORT_REFRESH_S
                ):
                    self._last_performance_report_refresh_s = now_s
                    self.performance_area.text = monitor.format_report(
                        max_metrics=PERFORMANCE_REPORT_MAX_METRICS,
                        max_values=PERFORMANCE_REPORT_MAX_VALUES,
                        max_counters=PERFORMANCE_REPORT_MAX_COUNTERS,
                    )
                    self.performance_area.texture_update()
                    self._update_report_label_geometry(self.performance_area)
            elif (
                self.performance_area is not None
                and not self._performance_card_enabled()
                and self.performance_area.text != PERFORMANCE_CARD_PAUSED_TEXT
            ):
                self.performance_area.text = PERFORMANCE_CARD_PAUSED_TEXT
                self.performance_area.texture_update()
                self._update_report_label_geometry(self.performance_area)

    def refresh_plot(self, *_args) -> None:
        """Purpose: refresh the live spectrum graph and its labels. Rationale: the plot is the fastest-changing part of the UI."""
        monitor = self.runtime.performance_monitor
        with monitor.measure("ui.refresh_plot"):
            refresh_start_s = perf_counter()
            monitor.increment("ui.refresh_plot_calls")
            if self._last_refresh_plot_call_s > 0.0:
                monitor.record_value(
                    "ui.refresh_plot_interval_ms",
                    (refresh_start_s - self._last_refresh_plot_call_s) * 1000.0,
                )
            self._last_refresh_plot_call_s = refresh_start_s
            if not self._live_display_running:
                if self._spectrum_warnings is not None:
                    self._spectrum_warnings.set_warning("saturation", None, SATURATION_WARNING_RGBA)
                if self.layout_label is not None:
                    self.layout_label.text = SPECTRUM_CARD_LAYOUT_PAUSED_TEXT
                if self.refresh_rate_label is not None:
                    self.refresh_rate_label.text = SPECTRUM_CARD_REFRESH_PAUSED_TEXT
                monitor.increment("ui.refresh_plot_paused_skips")
                return

            spectrum = self.runtime.state_manager.latest_spectrum()
            device_config = self.runtime.state_manager.get_user_config().device
            if self._spectrum_warnings is not None:
                warning = None
                if spectrum is not None:
                    start = max(0, spectrum.effective_start_index)
                    stop = start + spectrum.effective_sample_count
                    active_counts = spectrum.adc_counts[start:stop]
                    adc_max = (1 << device_config.adc_resolution_bits) - 1
                    if 0 in active_counts or adc_max in active_counts:
                        warning = (
                            "[b]Detector saturated[/b]\n"
                            "ADC clipping detected.\n"
                            "Adjust integration time or light input until clipping clears."
                        )
                    elif spectrum.near_saturation:
                        warning = (
                            "[b]Potential saturation[/b]\n"
                            "Signal is approaching the calibrated limit\n"
                            "Please reduce integration time or light input."
                        )
                self._spectrum_warnings.set_warning("saturation", warning, SATURATION_WARNING_RGBA)
            calibration_config = self.runtime.state_manager.get_calibration_config()
            expected_samples = device_config.sample_count
            raw_view = self.raw_adc_view and self._current_live_graph_mode() == LIVE_GRAPH_MODE_SPECTRUM
            normalized_max = 4095.0 if raw_view else 1.0
            effective_start_default = device_config.effective_start_index
            effective_end_default = max(
                effective_start_default + device_config.effective_sample_count - 1,
                effective_start_default,
            )

            display_indices: list[int] = []
            display_values: list[float] = []
            layout_text = SPECTRUM_CARD_STREAM_WAITING_TEXT

            if spectrum is not None:
                monitor.record_value(
                    "ui.latest_frame_age_ms",
                    max((datetime.now(timezone.utc) - spectrum.timestamp).total_seconds() * 1000.0, 0.0),
                )
                plot_source = spectrum.adc_counts if raw_view else (spectrum.live_display_counts or spectrum.adc_counts)
                total_samples = len(plot_source)
                full_frame_ready = total_samples >= expected_samples

                if full_frame_ready:
                    # Only the effective CCD pixels are plotted for full frames, so
                    # dummy leading/trailing clocks do not dominate the display.
                    start = 0 if raw_view else spectrum.effective_start_index
                    end = total_samples if raw_view else min(
                        start + spectrum.effective_sample_count,
                        total_samples,
                    )
                    display_indices = range(start, end)
                    display_values = plot_source[start:end]
                    layout_text = SPECTRUM_CARD_LAYOUT_FULL_TEMPLATE.format(
                        total=total_samples,
                        effective=len(display_values),
                        leading=start,
                        trailing=max(total_samples - end, 0),
                    )
                else:
                    # Plot the exact short frame the device sent so the UI does not
                    # invent missing data when a frame arrives incomplete.
                    display_indices = range(total_samples)
                    display_values = plot_source
                    layout_text = SPECTRUM_CARD_LAYOUT_INCOMPLETE_TEMPLATE.format(total=total_samples)
                layout_text += " | Pixel alignment nominal; sensor-pin phase unverified"
            else:
                monitor.increment("ui.refresh_plot_no_frame")

            if self.layout_label is not None:
                self.layout_label.text = layout_text
            if display_indices:
                x_tick_indices = self._build_axis_tick_indices(
                    display_indices[0],
                    display_indices[-1],
                    self._plot_x_tick_count,
                )
            else:
                x_tick_indices = self._build_axis_tick_indices(
                    effective_start_default,
                    effective_end_default,
                    self._plot_x_tick_count,
                )
            axis_tick_texts = [
                self._format_plot_axis_label(sample_index, calibration_config)
                for sample_index in x_tick_indices
            ]
            monitor.record_value("ui.frontend_plotted_sample_count", len(display_values))
            live_graph_mode = self._current_live_graph_mode()
            spectrogram_update_due = (
                live_graph_mode == LIVE_GRAPH_MODE_SPECTROGRAM
                and self._spectrogram_refresh_due()
            )
            if live_graph_mode == LIVE_GRAPH_MODE_SPECTROGRAM and not spectrogram_update_due:
                monitor.increment("ui.spectrogram_refresh_skips")
            spectrogram_frames: list[SpectrogramHistoryFrame] = (
                self._spectrogram_source_frames()
                if spectrogram_update_due
                else []
            )
            if spectrogram_frames:
                monitor.record_value("ui.spectrogram_frame_count", len(spectrogram_frames))
                if len(spectrogram_frames) >= 2:
                    monitor.record_value(
                        "ui.spectrogram_frame_span_ms",
                        max(
                            (spectrogram_frames[-1].timestamp - spectrogram_frames[0].timestamp).total_seconds() * 1000.0,
                            0.0,
                        ),
                    )
            if self.plot_x_axis is not None:
                self.plot_x_axis.set_labels(axis_tick_texts)
            if self.plot_y_axis is not None:
                if live_graph_mode == LIVE_GRAPH_MODE_SPECTROGRAM:
                    if spectrogram_update_due:
                        self.plot_y_axis.set_labels(self._spectrogram_time_axis_labels(spectrogram_frames))
                else:
                    self.plot_y_axis.set_labels(self._live_plot_y_axis_labels())
            if self.plot is not None and live_graph_mode == LIVE_GRAPH_MODE_SPECTRUM:
                self.plot.set_adc_range(0.0, normalized_max)
                coefficients = calibration_config.wavelength_coefficients if self._show_wavelength_axis(calibration_config) else ()
                self.plot.set_measurement_context(coefficients, raw=raw_view)
                # This signature prevents redrawing the same spectrum repeatedly when
                # the timer fires faster than new frames arrive.
                plot_signature = (
                    spectrum.frame_id if spectrum is not None else None,
                    len(display_values),
                    display_indices[0] if display_indices else None,
                    display_indices[-1] if display_indices else None,
                    round(float(display_values[0]), 6) if display_values else None,
                    round(float(display_values[len(display_values) // 2]), 6) if display_values else None,
                    round(float(display_values[-1]), 6) if display_values else None,
                )
                if plot_signature != self._last_plot_signature:
                    self.plot.set_series(display_indices, display_values)
                    self._last_plot_signature = plot_signature
                    monitor.record_value("ui.frontend_line_plotted_points", len(display_values))
                    monitor.increment("ui.live_spectrum_updates")
                    self._record_plot_update()
                else:
                    monitor.increment("ui.live_spectrum_unchanged")
            if (
                self.spectrogram_plot is not None
                and live_graph_mode == LIVE_GRAPH_MODE_SPECTROGRAM
                and spectrogram_update_due
            ):
                spectrogram_rows, spectrogram_frame_ids = self._build_spectrogram_rows(
                    spectrogram_frames,
                    display_values,
                    expected_samples,
                )
                monitor.record_value("ui.spectrogram_visible_rows", len(spectrogram_rows))
                latest_row = spectrogram_rows[-1] if spectrogram_rows else []
                if latest_row:
                    monitor.record_value("ui.spectrogram_visible_columns", len(latest_row))
                    monitor.record_value("ui.frontend_spectrogram_plotted_cells", len(spectrogram_rows) * len(latest_row))
                first_row = spectrogram_rows[0] if spectrogram_rows else []
                spectrogram_signature = (
                    round(self._current_spectrogram_time_window_s(), 3),
                    len(spectrogram_frame_ids),
                    spectrogram_frame_ids[0] if spectrogram_frame_ids else None,
                    spectrogram_frame_ids[-1] if spectrogram_frame_ids else None,
                    len(latest_row),
                    round(float(first_row[0]), 6) if first_row else None,
                    round(float(latest_row[0]), 6) if latest_row else None,
                    round(float(latest_row[len(latest_row) // 2]), 6) if latest_row else None,
                    round(float(latest_row[-1]), 6) if latest_row else None,
                )
                self._last_spectrogram_refresh_s = perf_counter()
                if spectrogram_signature != self._last_spectrogram_signature:
                    self.spectrogram_plot.set_frame_history(spectrogram_rows, frame_ids=spectrogram_frame_ids)
                    self._last_spectrogram_signature = spectrogram_signature
                    monitor.increment("ui.live_spectrogram_updates")
                    self._record_plot_update()
                else:
                    monitor.increment("ui.live_spectrogram_unchanged")
            if self.refresh_rate_label is not None:
                refresh_hz = self._current_plot_refresh_hz()
                monitor.record_value("ui.plot_refresh_hz_estimate", refresh_hz)
                self.refresh_rate_label.text = (
                    f"Graph Refresh: {refresh_hz:.1f} Hz"
                    if refresh_hz > 0.0
                    else SPECTRUM_CARD_REFRESH_LABEL_TEXT
                )

    def refresh_view(self, *_args) -> None:
        """Purpose: refresh both status and plot sections together. Rationale: some UI actions need an immediate full refresh."""
        self.refresh_status()
        self.refresh_plot()

    def _refresh_calibration_plot(self, spectrum: SpectrumFrame | None) -> None:
        plot = self.calibration_plot
        if plot is None:
            return
        start, stop = 0, 0
        if spectrum is not None:
            start = max(spectrum.effective_start_index, 0)
            stop = min(start + spectrum.effective_sample_count, len(spectrum.live_display_counts))
        signature = (id(spectrum), spectrum.timestamp if spectrum is not None else None, start, stop, self._plot_x_tick_count)
        if signature == self._last_calibration_plot_signature:
            return
        self._last_calibration_plot_signature = signature
        values = spectrum.live_display_counts[start:stop] if spectrum is not None else []
        plot.set_series(range(start, stop), values)
        if self.calibration_plot_x_axis is not None:
            ticks = self._build_axis_tick_indices(start, max(start, stop - 1), self._plot_x_tick_count) if values else []
            self.calibration_plot_x_axis.set_labels([str(tick) for tick in ticks])

    def _refresh_main_content(self) -> None:
        """Purpose: swap the main content view. Rationale: the app should show either the live spectrum or the calibration manager, not both."""
        if self._main_content_container is None:
            return

        if self._main_content_mode != "display":
            for group in self._live_graph_choices:
                group.focus = False
        for switch in self._setting_switches:
            switch.focus = False
        if self.calibration_plot is not None and self._main_content_mode != "calibration":
            self.calibration_plot.focus = False
        self._tooltips.dismiss()
        self._main_content_container.clear_widgets()
        if self._main_content_mode == "calibration" and self._calibration_manager_card is not None:
            self._main_content_container.add_widget(self._calibration_manager_card)
        elif self._main_content_mode == "display" and self._display_manager_card is not None:
            self._main_content_container.add_widget(self._display_manager_card)
        elif self._plot_card is not None:
            self._main_content_container.add_widget(self._plot_card)

    def open_calibration_manager(self, *_args) -> None:
        """Purpose: toggle the calibration manager in the main content area. Rationale: the side-panel entry button should also work as a quick return to the live plot."""
        if self._main_content_mode == "calibration":
            self.show_spectrum_view()
            return
        self._main_content_mode = "calibration"
        self._refresh_main_content()
        self.set_notice("Calibration manager opened.")

    def _focus_choices_on_tab(self, _window, key, _scan, _text, modifiers) -> bool:
        # SDL dispatches on_keyboard only when the focused control did not handle the key.
        if key != 9 or not set(modifiers or ()) <= {"shift"}:
            return False
        if self._main_content_mode == "display":
            choices = self._live_graph_choices
        elif self._main_content_mode == "calibration":
            choices = self._setting_switches
        else:
            choices = (self.port_spinner, self.integration_unit)
        candidates = reversed(choices) if modifiers else choices
        for control in candidates:
            if control is not None and not control.disabled and control.get_parent_window() is not None:
                control.focus = True
                return True
        return False

    def open_display_manager(self, *_args) -> None:
        """Purpose: toggle the display and layout manager in the main content area. Rationale: graph and panel choices should live in a full-size workspace instead of the side panel."""
        if self._main_content_mode == "display":
            self.show_spectrum_view()
            return
        self._main_content_mode = "display"
        self._refresh_main_content()
        self.set_notice("Display and layout manager opened.")

    def show_spectrum_view(self, *_args) -> None:
        """Purpose: return to the live spectrum view. Rationale: users need a quick way back to the main measurement screen."""
        self._main_content_mode = "spectrum"
        self._refresh_main_content()
        self.set_notice("Returned to the live display view.")

    def _refresh_side_panel_cards(self) -> None:
        """Purpose: rebuild the scrollable side panel. Rationale: the side panel should always contain the full card set when visible."""
        if self._left_column is None:
            return

        self._tooltips.dismiss()
        self._left_column.clear_widgets()
        for card in self._visible_side_panel_cards():
            self._left_column.add_widget(card)

    def toggle_side_panel(self, *_args) -> None:
        """Purpose: show or hide the side panel. Rationale: one header control should let the graph expand to full width on demand."""
        self._side_panel_visible = not self._side_panel_visible
        self._apply_responsive_layout()

    def _record_plot_update(self) -> None:
        """Purpose: record when the plot changed. Rationale: measured refresh speed should reflect real redraw activity."""
        update_time_s = perf_counter()
        self._plot_update_times.append(update_time_s)
        monitor = self.runtime.performance_monitor
        monitor.increment("ui.plot_updates")
        if self._last_plot_update_s > 0.0:
            monitor.record_value("ui.plot_update_interval_ms", (update_time_s - self._last_plot_update_s) * 1000.0)
        self._last_plot_update_s = update_time_s

    def _current_plot_refresh_hz(self) -> float:
        """Purpose: estimate the plot refresh rate. Rationale: users need feedback on how quickly new frames are reaching the graph."""
        if len(self._plot_update_times) < 2:
            return 0.0

        newest = self._plot_update_times[-1]
        oldest = self._plot_update_times[0]
        if perf_counter() - newest > PLOT_REFRESH_STALE_S:
            return 0.0

        elapsed_s = newest - oldest
        if elapsed_s <= 0.0:
            return 0.0

        return (len(self._plot_update_times) - 1) / elapsed_s

    def set_notice(self, message: str) -> None:
        """Purpose: update the header notice text. Rationale: one central status message keeps user feedback easy to find."""
        if self.notice_label is not None:
            self.notice_label.text = message

    def _format_plot_axis_label(self, sample_index: int, calibration_config: CalibrationConfig) -> str:
        """Purpose: choose pixel or wavelength labels for the plot x-axis. Rationale: once wavelength calibration exists, the graph should read in physical units instead of raw CCD indices."""
        if not self._show_wavelength_axis(calibration_config):
            return str(sample_index)

        wavelength = float(indices_to_wavelengths([sample_index], calibration_config.wavelength_coefficients)[0])
        return self._format_wavelength_nm(wavelength)

    def _format_wavelength_nm(self, wavelength_nm: float) -> str:
        """Purpose: format wavelength values for UI readouts. Rationale: whole-number nanometers are easier to scan quickly than long decimals."""
        return str(int(round(wavelength_nm)))

    def _build_axis_tick_indices(self, start_index: int, end_index: int, tick_count: int) -> list[int]:
        """Purpose: spread x-axis tick positions across the visible range. Rationale: denser tick marks make the plot easier to read than only start, middle, and end labels."""
        count = max(tick_count, 2)
        if end_index <= start_index:
            return [start_index] * count

        span = end_index - start_index
        return [
            int(round(start_index + (span * tick_index / (count - 1))))
            for tick_index in range(count)
        ]

    def _show_wavelength_axis(self, calibration_config: CalibrationConfig) -> bool:
        """Purpose: decide when the x-axis should display wavelength values. Rationale: uncalibrated plots are easier to interpret in pixels, while calibrated plots should show wavelength."""
        return calibration_config.apply_wavelength_mapping and has_saved_wavelength_mapping(calibration_config)

    def _update_fill_background(self, widget) -> None:
        """Purpose: keep a solid widget background rectangle aligned to its layout box. Rationale: canvas rectangles do not resize automatically with widgets."""
        widget._background.pos = widget.pos  # type: ignore[attr-defined]
        widget._background.size = widget.size  # type: ignore[attr-defined]

    def _current_display_work_width(self) -> float:
        """Purpose: estimate the active monitor width for responsive layout decisions. Rationale: large displays should switch to stacked mode sooner than a fixed pixel breakpoint would suggest."""
        try:
            import ctypes
            from ctypes import wintypes

            class POINT(ctypes.Structure):
                _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

            class RECT(ctypes.Structure):
                _fields_ = [
                    ("left", wintypes.LONG),
                    ("top", wintypes.LONG),
                    ("right", wintypes.LONG),
                    ("bottom", wintypes.LONG),
                ]

            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("rcMonitor", RECT),
                    ("rcWork", RECT),
                    ("dwFlags", wintypes.DWORD),
                ]

            user32 = ctypes.windll.user32
            monitor_default_to_nearest = 2
            window_left = float(getattr(Window, "left", 0.0))
            window_top = float(getattr(Window, "top", 0.0))
            center_point = POINT(
                int(window_left + (Window.width / 2.0)),
                int(window_top + (Window.height / 2.0)),
            )
            monitor_handle = user32.MonitorFromPoint(center_point, monitor_default_to_nearest)
            if monitor_handle:
                monitor_info = MONITORINFO()
                monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
                if user32.GetMonitorInfoW(monitor_handle, ctypes.byref(monitor_info)):
                    work_width = float(monitor_info.rcWork.right - monitor_info.rcWork.left)
                    if work_width > 0:
                        return work_width
        except Exception:
            pass

        return float(Window.width)

    def _current_display_work_height(self) -> float:
        """Purpose: estimate the active monitor work-area height. Rationale: maximized plot mode should compare the window against the real display height, not only its width."""
        try:
            import ctypes
            from ctypes import wintypes

            class POINT(ctypes.Structure):
                _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

            class RECT(ctypes.Structure):
                _fields_ = [
                    ("left", wintypes.LONG),
                    ("top", wintypes.LONG),
                    ("right", wintypes.LONG),
                    ("bottom", wintypes.LONG),
                ]

            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("rcMonitor", RECT),
                    ("rcWork", RECT),
                    ("dwFlags", wintypes.DWORD),
                ]

            user32 = ctypes.windll.user32
            monitor_default_to_nearest = 2
            window_left = float(getattr(Window, "left", 0.0))
            window_top = float(getattr(Window, "top", 0.0))
            center_point = POINT(
                int(window_left + (Window.width / 2.0)),
                int(window_top + (Window.height / 2.0)),
            )
            monitor_handle = user32.MonitorFromPoint(center_point, monitor_default_to_nearest)
            if monitor_handle:
                monitor_info = MONITORINFO()
                monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
                if user32.GetMonitorInfoW(monitor_handle, ctypes.byref(monitor_info)):
                    work_height = float(monitor_info.rcWork.bottom - monitor_info.rcWork.top)
                    if work_height > 0:
                        return work_height
        except Exception:
            pass

        return float(Window.height)

    def _current_plot_display_mode(self) -> str:
        """Purpose: choose between maximized and windowed plot behavior. Rationale: the chart needs a stable large-window mode instead of inferring everything from one continuous resize curve."""
        if self._window_is_maximized:
            return PLOT_DISPLAY_MODE_MAXIMIZED
        display_width = max(self._current_display_work_width(), 1.0)
        display_height = max(self._current_display_work_height(), 1.0)
        width_ratio = float(Window.width) / display_width
        height_ratio = float(Window.height) / display_height
        if width_ratio >= MAXIMIZED_WINDOW_WIDTH_RATIO and height_ratio >= MAXIMIZED_WINDOW_HEIGHT_RATIO:
            return PLOT_DISPLAY_MODE_MAXIMIZED
        return PLOT_DISPLAY_MODE_WINDOWED

    def _handle_window_maximize(self, *_args) -> None:
        """Purpose: remember that the app window is maximized. Rationale: maximize mode should follow the real SDL window state instead of only size heuristics."""
        self._window_is_maximized = True
        self._apply_responsive_layout()

    def _handle_window_restore(self, *_args) -> None:
        """Purpose: remember that the app window left maximize mode. Rationale: the chart should return to the windowed profile as soon as the window is restored."""
        self._window_is_maximized = False
        self._apply_responsive_layout()

    def _apply_plot_display_mode(self, *, axis_font_sp: float) -> None:
        """Purpose: apply one of the two explicit plot display modes. Rationale: maximized and windowed plots should have separate sizing rules instead of sharing one fragile axis layout."""
        mode = self._current_plot_display_mode()
        axis_column_width = MAXIMIZED_AXIS_COLUMN_WIDTH if mode == PLOT_DISPLAY_MODE_MAXIMIZED else AXIS_COLUMN_WIDTH
        x_axis_height = MAXIMIZED_X_AXIS_HEIGHT if mode == PLOT_DISPLAY_MODE_MAXIMIZED else X_AXIS_HEIGHT
        plot_shell_spacing = MAXIMIZED_PLOT_AXIS_SPACING if mode == PLOT_DISPLAY_MODE_MAXIMIZED else WINDOWED_PLOT_AXIS_SPACING
        x_tick_count = X_AXIS_TICK_COUNT

        if self._plot_shell is not None:
            self._plot_shell.spacing = plot_shell_spacing
        if self._plot_x_axis_shell is not None:
            self._plot_x_axis_shell.height = x_axis_height
        if self._plot_x_axis_spacer is not None:
            self._plot_x_axis_spacer.width = axis_column_width
        if self.plot_y_axis is not None:
            self.plot_y_axis.width = axis_column_width
            self.plot_y_axis.set_font_sp(axis_font_sp)
        if self.plot_x_axis is not None:
            self.plot_x_axis.set_font_sp(axis_font_sp)
        if self.calibration_plot_x_axis is not None:
            self.calibration_plot_x_axis.set_font_sp(axis_font_sp)
        if self.plot is not None:
            self.plot.set_grid_counts(x_count=x_tick_count, y_count=Y_AXIS_TICK_COUNT)
        if self.spectrogram_plot is not None:
            self.spectrogram_plot.set_grid_counts(x_count=x_tick_count, y_count=SPECTROGRAM_Y_GRID_COUNT)
        if self.calibration_plot is not None:
            self.calibration_plot.set_grid_counts(x_count=x_tick_count, y_count=Y_AXIS_TICK_COUNT)

        mode_changed = mode != self._plot_display_mode or x_tick_count != self._plot_x_tick_count
        self._plot_display_mode = mode
        self._plot_x_tick_count = x_tick_count
        if mode_changed:
            self.refresh_plot()

    def _responsive_width_breakpoint(self) -> float:
        """Purpose: compute the layout breakpoint for the current display. Rationale: high-resolution monitors should stack the UI at wider window sizes than 1080p displays."""
        display_width = self._current_display_work_width()
        scaled_breakpoint = display_width * LARGE_DISPLAY_RESPONSIVE_WIDTH_RATIO
        return max(float(RESPONSIVE_BREAKPOINT), scaled_breakpoint)

    def _update_header_text_wrapping(self) -> None:
        """Purpose: keep the header title and notice vertically aligned inside their current rows. Rationale: the compact header needs explicit text boxes so the title and notice do not clip against the card border."""
        if self._header_title_label is not None:
            self._header_title_label.text_size = (
                max(self._header_title_label.width - dp(8), dp(40)),
                max(self._header_title_label.height, dp(20)),
            )
        if self.notice_label is not None:
            self.notice_label.text_size = (
                max(self.notice_label.width - dp(8), HEADER_NOTICE_MIN_TEXT_WIDTH),
                max(self.notice_label.height, dp(20)),
            )

    def _apply_header_layout(
        self,
        *,
        compact_layout: bool,
        short_layout: bool,
        side_panel_active: bool,
        title_font_sp: float,
        body_font_sp: float,
        button_height: float,
        notice_height: float,
    ) -> None:
        """Purpose: resize the header for the current window class. Rationale: the title, notice text, and side-panel button need their own compact rules instead of squeezing into one fixed-height row."""
        header_spacing = (
            HEADER_CARD_SPACING_SHORT
            if short_layout
            else (HEADER_CARD_SPACING_COMPACT if compact_layout else CARD_GAP)
        )
        header_padding = (
            HEADER_CARD_PADDING_SHORT
            if short_layout
            else (HEADER_CARD_PADDING_COMPACT if compact_layout else CARD_PAD)
        )
        title_height = (
            HEADER_TITLE_HEIGHT_SHORT
            if short_layout
            else (HEADER_TITLE_HEIGHT_COMPACT if compact_layout else HEADER_TITLE_HEIGHT)
        )
        effective_notice_height = (
            HEADER_NOTICE_HEIGHT_SHORT
            if short_layout
            else notice_height
        )
        button_width = HEADER_SIDE_PANEL_BUTTON_WIDTH_COMPACT if compact_layout else HEADER_SIDE_PANEL_BUTTON_WIDTH
        top_row_height = max(title_height, button_height)

        if self._header_card is not None:
            self._header_card.spacing = header_spacing
            self._header_card.padding = header_padding
        if self._header_top_row is not None:
            self._header_top_row.orientation = "horizontal"
            self._header_top_row.spacing = header_spacing
            self._header_top_row.height = top_row_height
        if self._header_title_label is not None:
            self._header_title_label.font_size = f"{title_font_sp}sp"
            self._header_title_label.size_hint_y = None
            self._header_title_label.size_hint_x = 1.0
            self._header_title_label.height = title_height
        if self.notice_label is not None:
            self.notice_label.height = effective_notice_height
            self.notice_label.font_size = f"{body_font_sp}sp"
        if self._side_panel_button is not None:
            self._side_panel_button.text = (
                HEADER_SIDE_PANEL_BUTTON_TEXT if side_panel_active else HEADER_SIDE_PANEL_BUTTON_TEXT_HIDDEN
            )
            self._side_panel_button.size_hint_y = None
            self._side_panel_button.height = button_height
            self._side_panel_button.font_size = f"{body_font_sp}sp"
            self._side_panel_button.size_hint_x = None
            self._side_panel_button.width = button_width
        self._update_header_text_wrapping()

    def _apply_responsive_layout(self, *_args) -> None:
        """Purpose: switch between wide and narrow layouts. Rationale: the UI should remain usable on both large and smaller windows."""
        if (
            self._body is None
            or self._left_column is None
            or self._right_column is None
            or self._left_scroll is None
        ):
            return

        self._tooltips.dismiss()
        # Wide mode uses side-by-side columns; narrow mode stacks everything and
        # keeps the side panel optional so the plot can use the full width.
        responsive_width_breakpoint = self._responsive_width_breakpoint()
        narrow_layout = Window.width < responsive_width_breakpoint
        short_layout = Window.height < SHORT_HEIGHT_BREAKPOINT
        compact_layout = Window.width < COMPACT_BREAKPOINT or short_layout
        stack_connection_buttons = Window.width < BUTTON_STACK_BREAKPOINT
        stacked_side_panel_height = min(dp(320), max(dp(180), Window.height * 0.30))
        self._body.orientation = "vertical" if narrow_layout else "horizontal"
        for header, view, scroll_content in (
            (self._calibration_header_card, self._calibration_manager_card, self._calibration_scroll_content),
            (self._display_header_card, self._display_manager_card, self._display_scroll_content),
        ):
            header_parent = scroll_content if narrow_layout else view
            if header is not None and header_parent is not None and header.parent is not header_parent:
                header.parent.remove_widget(header)
                # BoxLayout stores children in reverse display order.
                header_parent.add_widget(header, index=len(header_parent.children))
        self._body.spacing = APP_GAP if self._side_panel_visible else 0
        side_panel_active = self._side_panel_visible
        self._left_scroll.size_hint_x = (1.0 if narrow_layout else SIDEBAR_RATIO_WIDE) if side_panel_active else None
        self._left_scroll.width = 0 if side_panel_active else 0
        self._left_scroll.size_hint_y = None if narrow_layout else (1.0 if side_panel_active else None)
        self._left_scroll.height = stacked_side_panel_height if (narrow_layout and side_panel_active) else 0
        self._left_scroll.opacity = 1.0 if side_panel_active else 0.0
        self._left_scroll.disabled = not side_panel_active
        self._right_column.size_hint_x = 1.0 if (narrow_layout or not side_panel_active) else DETAIL_RATIO_WIDE
        self._right_column.size_hint_y = 1.0
        if self._connection_buttons is not None:
            self._connection_buttons.orientation = "vertical" if stack_connection_buttons else "horizontal"
            self._connection_buttons.height = (
                (NARROW_BUTTON_HEIGHT * len(self._connection_buttons.children)) + (CARD_GAP * (len(self._connection_buttons.children) - 1))
                if stack_connection_buttons
                else BUTTON_HEIGHT
            )
        title_font_sp = COMPACT_TITLE_FONT_SP if compact_layout else TITLE_FONT_SP
        section_font_sp = COMPACT_SECTION_TITLE_FONT_SP if compact_layout else SECTION_TITLE_FONT_SP
        body_font_sp = COMPACT_BODY_FONT_SP if compact_layout else BODY_FONT_SP
        small_font_sp = COMPACT_SMALL_FONT_SP if compact_layout else SMALL_FONT_SP
        axis_font_sp = COMPACT_AXIS_FONT_SP if compact_layout else AXIS_FONT_SP
        control_height = NARROW_CONTROL_HEIGHT if compact_layout else CONTROL_HEIGHT
        button_height = NARROW_BUTTON_HEIGHT if compact_layout else BUTTON_HEIGHT
        info_height = NARROW_INFO_LABEL_HEIGHT if compact_layout else INFO_LABEL_HEIGHT
        switch_height = NARROW_SWITCH_ROW_HEIGHT if compact_layout else SWITCH_ROW_HEIGHT
        notice_height = HEADER_NOTICE_HEIGHT_COMPACT if compact_layout else HEADER_NOTICE_HEIGHT
        for card in self._side_panel_cards:
            card.spacing = dp(6) if compact_layout else CARD_GAP
            card.padding = dp(10) if compact_layout else CARD_PAD
        self._apply_header_layout(
            compact_layout=compact_layout,
            short_layout=short_layout,
            side_panel_active=side_panel_active,
            title_font_sp=title_font_sp,
            body_font_sp=body_font_sp,
            button_height=button_height,
            notice_height=notice_height,
        )
        if self.log_area is not None:
            self.log_area.height = DIAGNOSTICS_CARD_TEXT_HEIGHT_COMPACT if compact_layout else DIAGNOSTICS_CARD_TEXT_HEIGHT
        if self.performance_area is not None:
            self.performance_area.font_size = f"{small_font_sp}sp"
            self.performance_area._min_report_height = (  # type: ignore[attr-defined]
                PERFORMANCE_CARD_TEXT_HEIGHT_COMPACT if compact_layout else PERFORMANCE_CARD_TEXT_HEIGHT
            )
            self._update_report_label_geometry(self.performance_area)

        if self.port_spinner is not None:
            self.port_spinner.height = control_height
            self.port_spinner.font_size = f"{body_font_sp}sp"
        for group in self._live_graph_choices:
            group.row_height = control_height
            group.font_size = sp(body_font_sp)
        for text_input in self._text_inputs:
            if text_input.readonly and text_input.multiline:
                text_input.font_size = f"{small_font_sp}sp"
                continue
            if text_input.multiline:
                text_input.font_size = f"{small_font_sp}sp"
                continue
            text_input.height = control_height
            text_input.font_size = f"{body_font_sp}sp"
        for editor in self._multiline_editors:
            editor.height = CALIBRATION_EDITOR_HEIGHT_COMPACT if compact_layout else CALIBRATION_EDITOR_HEIGHT
        for button in self._buttons:
            button.height = button_height
            button.font_size = f"{body_font_sp}sp"
            button.text_size = (
                max(button.width - BUTTON_TEXT_PAD_X, dp(40)),
                max(button.height - BUTTON_TEXT_PAD_Y, dp(20)),
            )
            button.halign = "center"
            button.valign = "middle"
        for label in self._section_titles:
            label.font_size = f"{section_font_sp}sp"
            label.height = notice_height
        for label in self._info_labels:
            label.font_size = f"{body_font_sp}sp"
            label.height = info_height
        for label in self._small_labels:
            label.font_size = f"{small_font_sp}sp"
        if self.integration_status is not None:
            self.integration_status.height = NARROW_SMALL_LABEL_HEIGHT if compact_layout else SMALL_LABEL_HEIGHT
        self._apply_plot_display_mode(axis_font_sp=axis_font_sp)
        for switch in self._setting_switches:
            switch.height = switch_height
            switch.font_size = sp(body_font_sp)
        for label in self._labels_for_wrapping:
            label.text_size = (max(label.width - dp(8), dp(40)), None)
        self._apply_frame_data_label_visibility(info_height)
        self._apply_live_graph_mode()
        self._update_header_text_wrapping()

    def _section_title(self, text: str) -> Label:
        """Purpose: create a styled section heading. Rationale: shared formatting avoids repeating label style settings everywhere."""
        label = Label(
            text=f"[b]{text}[/b]",
            markup=True,
            font_size=f"{SECTION_TITLE_FONT_SP}sp",
            color=TEXT_PRIMARY_RGBA,
            size_hint_y=None,
            height=HEADER_NOTICE_HEIGHT,
            halign="left",
            valign="middle",
        )
        return self._register_section_title(label)

    def _info_label(self, text: str) -> Label:
        """Purpose: create a standard info label. Rationale: repeated UI label styling should come from one helper."""
        label = Label(
            text=text,
            color=TEXT_SECONDARY_RGBA,
            size_hint_y=None,
            height=INFO_LABEL_HEIGHT,
            halign="left",
            valign="middle",
            font_size=f"{BODY_FONT_SP}sp",
        )
        return self._register_info_label(label)

    def _small_label(self, text: str, *, fit_content: bool = True) -> Label:
        """Purpose: create smaller explanatory text. Rationale: helper text should be visually distinct from live status labels."""
        label = Label(
            text=text,
            color=TEXT_TERTIARY_RGBA,
            font_size=f"{SMALL_FONT_SP}sp",
            size_hint_y=None,
            height=0 if fit_content else SMALL_LABEL_HEIGHT,
            halign="left",
            valign="top",
        )
        self._configure_label_wrapping(label)
        if fit_content:
            label.bind(texture_size=lambda instance, size: setattr(instance, "height", size[1]))
        self._small_labels.append(label)
        return label

    def _button(
        self, text: str, handler, *, tooltip: str | None = None,
        background_color=BUTTON_BACKGROUND_RGBA, **kwargs,
    ) -> Button:
        """Purpose: create a styled button bound to a handler. Rationale: button look-and-feel should stay consistent across the UI."""
        button = Button(
            text=text,
            background_normal="",
            background_color=background_color,
            color=BUTTON_TEXT_RGBA,
            font_size=f"{BODY_FONT_SP}sp",
            halign="center",
            valign="middle",
            **kwargs,
        )
        button.bind(
            size=lambda instance, _value: setattr(
                instance,
                "text_size",
                (
                    max(instance.width - BUTTON_TEXT_PAD_X, dp(40)),
                    max(instance.height - BUTTON_TEXT_PAD_Y, dp(20)),
                ),
            )
        )
        button.bind(on_release=handler)
        if tooltip:
            self._tooltips.register(button, tooltip)
        self._buttons.append(button)
        return button

    def _setting_switch(
        self, text: str, active: bool, on_change, *, tooltip: str | None = None,
    ) -> SettingSwitch:
        switch = SettingSwitch(text=text, active=active, height=SWITCH_ROW_HEIGHT, font_size=sp(BODY_FONT_SP))
        switch.bind(active=lambda _switch, value: on_change(value))
        if tooltip:
            self._tooltips.register(switch, tooltip)
        self._setting_switches.append(switch)
        return switch

    def _calibration_action_row(self, title: str, description: str, action_key: str) -> Card:
        """Purpose: create one calibration routine entry. Rationale: the manager should present guided calibrations as a readable action list."""
        row_card = Card(size_hint_y=None)
        row_card.bind(minimum_height=row_card.setter("height"))
        row_card.add_widget(self._section_title(title))
        row_card.add_widget(self._small_label(description))
        row_card.add_widget(
            self._button(
                f"Start {title}",
                lambda *_args, key=action_key, display=title: self.run_calibration_task(key, display),
                size_hint_y=None,
                height=BUTTON_HEIGHT,
            )
        )
        return row_card

    def run_calibration_task(self, action_key: str, display_name: str) -> None:
        """Purpose: acknowledge a requested calibration routine. Rationale: the manager should expose task slots even before each routine is fully automated."""
        notices = {
            "pixel_mapping": (
                "Pixel mapping selected. Next step: capture several known light sources and match their peaks to CCD pixels."
            ),
            "dark_reference": "Dark reference capture selected. Cover the sensor and acquire a baseline frame set.",
            "intensity_reference": "Intensity reference selected. Use an even illumination source and record a correction frame.",
            "wavelength_review": "Wavelength review selected. Compare the fitted map to known peaks.",
        }
        self.set_notice(notices.get(action_key, f"{display_name} selected."))

    @staticmethod
    def _bias_summary_text(config: CalibrationConfig) -> str:
        summary = CALIBRATION_BIAS_SUMMARY_TEMPLATE.format(count=len(config.bias_counts))
        if not config.bias_counts:
            return summary
        if config.bias_integration_us is None:
            return f"{summary}. Capture Bias Reference again to record its integration time."
        return f"{summary}. Captured at {config.bias_integration_us:,} µs."

    def _refresh_calibration_summaries(self, config: CalibrationConfig) -> None:
        """Purpose: refresh the summary labels for the editable calibration data blocks. Rationale: the manager should show what is currently loaded without forcing the user to inspect each large text field."""
        if self.bias_summary_label is not None:
            self.bias_summary_label.text = self._bias_summary_text(config)
        if self.flat_field_summary_label is not None:
            self.flat_field_summary_label.text = CALIBRATION_FLAT_FIELD_SUMMARY_TEMPLATE.format(
                count=len(config.intensity_correction)
            )
        if self.pixel_mapping_summary_label is not None:
            self.pixel_mapping_summary_label.text = self._wavelength_fit_status(config)
        if self.qe_summary_label is not None:
            self.qe_summary_label.text = CALIBRATION_QE_SUMMARY_TEMPLATE.format(
                count=len(config.quantum_efficiency_points)
            )

    @staticmethod
    def _wavelength_fit_status(config: CalibrationConfig) -> str:
        if not has_saved_wavelength_mapping(config):
            return "Pixel mode (no active wavelength fit)"
        degree = len(config.wavelength_coefficients) - 1
        count = len(config.pixel_mapping_points)
        status = "active" if config.apply_wavelength_mapping else "disabled"
        return f"Wavelength fit {status} (degree {degree}, {count} reference points)"

    def _format_float_vector(self, values: Sequence[float], *, per_line: int = 8) -> str:
        """Purpose: format vector-style calibration data into a readable multiline string. Rationale: long correction arrays are easier to inspect when wrapped across lines."""
        if not values:
            return ""

        lines: list[str] = []
        for start in range(0, len(values), per_line):
            chunk = values[start : start + per_line]
            lines.append(", ".join(repr(float(value)) for value in chunk))
        return "\n".join(lines)

    def _format_mapping_points(self, points: Sequence[PixelMappingPoint]) -> str:
        """Purpose: format pixel mapping references for the editor. Rationale: saved wavelength references should round-trip cleanly through the text form."""
        return "\n".join(
            f"{point.pixel_index!r}, {point.wavelength_nm!r}"
            for point in points
        )

    def _format_response_points(self, points: Sequence[SpectralResponsePoint]) -> str:
        """Purpose: format QE/response points for the editor. Rationale: wavelength/value pairs should be easy to paste in and edit line-by-line."""
        return "\n".join(
            f"{point.wavelength_nm!r}, {point.relative_value!r}"
            for point in points
        )

    def _parse_float_vector(self, text: str) -> list[float]:
        """Purpose: parse a vector from comma-, newline-, or whitespace-separated text. Rationale: calibration arrays are often pasted from spreadsheets in different plain-text layouts."""
        cleaned = text.replace(",", " ").replace("\n", " ").replace("\t", " ")
        return [self._parse_finite_float(part) for part in cleaned.split()]

    @staticmethod
    def _parse_finite_float(text: str) -> float:
        value = float(text)
        if not isfinite(value):
            raise ValueError("non-finite calibration value")
        return value

    def _parse_mapping_points(self, text: str) -> list[PixelMappingPoint]:
        """Purpose: parse pixel-to-wavelength reference pairs from the text editor. Rationale: wavelength calibration should accept simple copied tables from external notes or spreadsheets."""
        points: list[PixelMappingPoint] = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            parts = self._split_pair_line(line)
            if len(parts) != 2:
                raise ValueError("invalid mapping row")
            points.append(
                PixelMappingPoint(
                    pixel_index=self._parse_finite_float(parts[0]),
                    wavelength_nm=self._parse_finite_float(parts[1]),
                )
            )
        return points

    def _parse_response_points(self, text: str) -> list[SpectralResponsePoint]:
        """Purpose: parse QE / response reference pairs from the text editor. Rationale: response-curve calibration data is naturally stored as wavelength/value rows."""
        points: list[SpectralResponsePoint] = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            parts = self._split_pair_line(line)
            if len(parts) != 2:
                raise ValueError("invalid response row")
            points.append(
                SpectralResponsePoint(
                    wavelength_nm=self._parse_finite_float(parts[0]),
                    relative_value=self._parse_finite_float(parts[1]),
                )
            )
        return points

    def _split_pair_line(self, line: str) -> list[str]:
        """Purpose: split a two-column calibration line from comma-, tab-, or whitespace-separated text. Rationale: copied calibration tables come from a mix of spreadsheet and plain-text formats."""
        if "," in line:
            return [part for part in line.split(",") if part.strip()]
        return [part for part in line.replace("\t", " ").split() if part.strip()]

    def _configure_label_wrapping(self, label: Label) -> None:
        """Purpose: make labels wrap within their current width. Rationale: narrow layouts need labels to resize instead of clipping."""
        label.bind(
            size=lambda instance, _value: setattr(
                instance,
                "text_size",
                (max(instance.width - dp(8), dp(40)), None),
            )
        )
        self._labels_for_wrapping.append(label)

    def _configure_text_input(self, widget: TextInput, *, tooltip: str | None = None) -> None:
        """Purpose: register text inputs for responsive scaling. Rationale: controls should share one resize path instead of per-widget tweaks."""
        widget.font_size = f"{BODY_FONT_SP}sp"
        if tooltip:
            self._tooltips.register(widget, tooltip)
        self._text_inputs.append(widget)

    def _configure_report_label(self, label: Label, *, min_height: float) -> None:
        """Purpose: configure a multiline report label that expands with its content. Rationale: long diagnostics output should grow the card instead of being trapped in a short fixed-height editor."""
        label._min_report_height = float(min_height)  # type: ignore[attr-defined]
        label.bind(
            width=lambda instance, _value: self._update_report_label_geometry(instance),
            texture_size=lambda instance, _value: self._update_report_label_geometry(instance),
        )
        self._update_report_label_geometry(label)

    def _update_report_label_geometry(self, label: Label) -> None:
        """Purpose: keep one expanding report label sized to its wrapped text. Rationale: the side-panel scroll view should handle overflow instead of an inner fixed-height box."""
        label.text_size = (max(label.width - dp(8), dp(40)), None)
        min_height = float(getattr(label, "_min_report_height", 0.0))
        texture_height = float(label.texture_size[1]) if label.texture_size else 0.0
        label.height = max(texture_height + dp(8), min_height)

    def _register_multiline_editor(self, widget: TextInput) -> None:
        """Purpose: remember editable multiline calibration boxes. Rationale: large calibration tables need their own responsive height handling instead of being squeezed to single-line control size."""
        self._multiline_editors.append(widget)

    def _register_section_title(self, label: Label) -> Label:
        """Purpose: remember section headers for responsive scaling. Rationale: title sizing should stay synchronized across cards."""
        self._configure_label_wrapping(label)
        self._section_titles.append(label)
        return label

    def _register_info_label(self, label: Label) -> Label:
        """Purpose: remember standard labels for responsive scaling. Rationale: status lines need shared height and font adjustments."""
        self._configure_label_wrapping(label)
        self._info_labels.append(label)
        return label


def run_desktop_app(runtime: AppRuntime) -> None:
    """Purpose: launch the Kivy desktop app. Rationale: the entrypoint should only need one simple call to start the UI."""
    DesktopSpectrometerApp(runtime).run()
