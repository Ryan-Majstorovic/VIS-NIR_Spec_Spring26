from __future__ import annotations

from collections.abc import Callable, Sequence

from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.widget import Widget


TEXT_COLOR = (0.13, 0.19, 0.24, 1)
ACCENT_COLOR = (0.06, 0.46, 0.43, 1)
EDGE_COLOR = (0.38, 0.43, 0.46, 1)
SURFACE_COLOR = (0.99, 0.99, 0.98, 1)
PRESSED_COLOR = (0.74, 0.89, 0.85, 1)
MENU_COLOR = (0.84, 0.91, 0.89, 1)
SELECTED_COLOR = (0.89, 0.95, 0.93, 1)
GROUP_EDGE = dp(1)
INDICATOR_SPACE = dp(32)
LABEL_PAD = dp(8)
NEXT_KEYS = {"right", "down"}
PREVIOUS_KEYS = {"left", "up"}
ACTIVATE_KEYS = {"enter", "numpadenter", "spacebar"}
ChoiceValue = str | bool | float


def _add_outline(widget, color, *, inset: float) -> Color:
    with widget.canvas.after:
        tint = Color(*color)
        outline = Line(width=dp(1))

    def update(*_args):
        outline.rectangle = (
            widget.x + inset, widget.y + inset,
            max(0, widget.width - 2 * inset), max(0, widget.height - 2 * inset),
        )

    widget.bind(pos=update, size=update)
    update()
    return tint


def _reveal_focused(widget) -> None:
    parent = widget.parent
    while isinstance(parent, Widget):
        if isinstance(parent, ScrollView):
            parent.scroll_to(widget, padding=0, animate=False)
            return
        parent = parent.parent


class _ChoiceRow(SpinnerOption):
    """Clickable label with separate selection and focus indicators."""

    checked = BooleanProperty(False)
    highlighted = BooleanProperty(False)

    def __init__(self, *, radio: bool = False, **kwargs) -> None:
        self._radio = radio
        super().__init__(
            background_normal="",
            background_down="",
            background_color=SURFACE_COLOR,
            color=TEXT_COLOR,
            padding=(INDICATOR_SPACE, 0, LABEL_PAD, 0),
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
            **kwargs,
        )
        self._focus_tint = _add_outline(self, (*TEXT_COLOR[:3], 0), inset=dp(2))
        with self.canvas.after:
            self._indicator_tint = Color(*ACCENT_COLOR)
            self._indicator = Line(width=dp(1))
            self._dot_tint = Color(*ACCENT_COLOR[:3], 0)
            self._dot = Ellipse(size=(dp(8), dp(8)))
        self.bind(pos=self._update_geometry, size=self._update_geometry)
        self.bind(state=self._update_state, checked=self._update_state, highlighted=self._update_state)
        self._update_geometry()
        self._update_state()

    def _update_geometry(self, *_args) -> None:
        self.text_size = self.size
        x, y = self.x + INDICATOR_SPACE / 2, self.center_y
        if self._radio:
            self._indicator.circle = (x, y, dp(8))
            self._dot.pos = (x - dp(4), y - dp(4))
        else:
            self._indicator.points = (x - dp(6), y, x - dp(2), y - dp(4), x + dp(6), y + dp(5))

    def _update_state(self, *_args) -> None:
        fill = SELECTED_COLOR if self._radio and self.checked else SURFACE_COLOR
        self.background_color = PRESSED_COLOR if self.state == "down" else fill
        self._focus_tint.a = int(self.highlighted)
        self._indicator_tint.a = int(self._radio or self.checked)
        self._dot_tint.a = int(self._radio and self.checked)


class RadioChoices(FocusBehavior, BoxLayout):
    """One tab stop for a group of visible, mutually exclusive choices."""

    row_height = NumericProperty(dp(38))
    font_size = NumericProperty("14sp")

    def __init__(
        self,
        options: Sequence[tuple[str, ChoiceValue]],
        selected: ChoiceValue,
        on_change: Callable[[ChoiceValue], None],
    ) -> None:
        super().__init__(size_hint_y=None, padding=GROUP_EDGE, spacing=GROUP_EDGE)
        self._rows = []
        self._on_change = on_change
        self.selected = selected
        self._frame_width = 0
        with self.canvas.before:
            Color(*EDGE_COLOR)
            self._frame = Rectangle()
        self._trigger_reveal = Clock.create_trigger(self._reveal_selection)
        for label, value in options:
            row = _ChoiceRow(text=label, radio=True)
            row.bind(on_release=lambda _, choice=value: self._select(choice))
            self.add_widget(row)
            self._rows.append((value, row))
        self.bind(width=self._update_layout, font_size=self._update_layout, row_height=self._update_layout)
        self.bind(pos=self._update_frame, height=self._update_frame)
        self.bind(focus=self._update_selection)
        self._update_layout()
        self._update_selection()

    def set_selected(self, value: ChoiceValue) -> None:
        """Reflect an externally applied value without invoking the callback."""
        self.selected = value
        self._update_selection()

    def _select(self, value: ChoiceValue) -> None:
        self.focus = True
        if value != self.selected:
            self.set_selected(value)
            self._on_change(value)

    def _update_selection(self, *_args) -> None:
        for value, row in self._rows:
            row.checked = value == self.selected
            row.highlighted = self.focus and row.checked
        if self.focus:
            self._trigger_reveal()

    def _reveal_selection(self, _dt) -> None:
        if self.focus:
            for _, row in self._rows:
                if row.checked:
                    _reveal_focused(row)
                    return

    def _update_layout(self, *_args) -> None:
        count = len(self._rows)
        measure = CoreLabel(font_size=self.font_size).get_extents
        widths = [measure(row.text)[0] + INDICATOR_SPACE + LABEL_PAD + dp(8) for _, row in self._rows]
        required_width = sum(widths) + (count - 1) * self.spacing + 2 * GROUP_EDGE
        horizontal = self.width >= required_width
        self.orientation = "horizontal" if horizontal else "vertical"
        self._frame_width = required_width if horizontal else self.width
        rows_height = self.row_height if horizontal else count * self.row_height + (count - 1) * self.spacing
        self.height = rows_height + 2 * GROUP_EDGE
        self._update_frame()
        for (_, row), width in zip(self._rows, widths):
            row.size_hint_x = None if horizontal else 1
            if horizontal:
                row.width = width
            row.height = self.row_height
            row.font_size = self.font_size
        if self.focus:
            self._trigger_reveal()

    def _update_frame(self, *_args) -> None:
        self._frame.pos = self.pos
        self._frame.size = (self._frame_width, self.height)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key = keycode[1]
        if key in NEXT_KEYS | PREVIOUS_KEYS and not modifiers:
            values = [value for value, _ in self._rows]
            step = 1 if key in NEXT_KEYS else -1
            index = (values.index(self.selected) + step) % len(values)
            self._select(values[index])
            return True
        if key in ACTIVATE_KEYS and not modifiers:
            return True
        return super().keyboard_on_key_down(window, keycode, text, modifiers)


class SettingSwitch(FocusBehavior, Button):
    """Toggle an immediate setting by clicking its row or pressing Space."""

    active = BooleanProperty(False)

    def __init__(self, **kwargs) -> None:
        super().__init__(
            size_hint_y=None,
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=TEXT_COLOR,
            padding=(dp(92), 0, LABEL_PAD, 0),
            halign="left",
            valign="middle",
            **kwargs,
        )
        with self.canvas.before:
            self._track_color = Color(*EDGE_COLOR)
            self._track = RoundedRectangle(size=(dp(42), dp(22)), radius=[dp(11)])
            Color(*SURFACE_COLOR)
            self._thumb = Ellipse(size=(dp(16), dp(16)))
        self._status = Label(color=TEXT_COLOR, bold=True, size_hint=(None, None))
        self.add_widget(self._status)
        self._focus_tint = _add_outline(self, (*TEXT_COLOR[:3], 0), inset=dp(1))
        self.bind(pos=self._update_geometry, size=self._update_geometry, active=self._update_geometry)
        self.bind(font_size=self._update_geometry, focus=self._update_focus)
        self._update_geometry()

    def _update_geometry(self, *_args) -> None:
        self.text_size = self.size
        track_x = self.x + dp(5)
        self._track.pos = (track_x, self.center_y - dp(11))
        self._track_color.rgba = ACCENT_COLOR if self.active else EDGE_COLOR
        self._thumb.pos = (track_x + dp(23 if self.active else 3), self.center_y - dp(8))
        self._status.text = "ON" if self.active else "OFF"
        self._status.font_size = self.font_size
        self._status.pos = (self.x + dp(50), self.y)
        self._status.size = (dp(36), self.height)

    def _update_focus(self, *_args) -> None:
        self._focus_tint.a = int(self.focus)
        if self.focus:
            _reveal_focused(self)

    def on_release(self) -> None:
        self.active = not self.active

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] in ACTIVATE_KEYS and not modifiers:
            self.dispatch("on_release")
            return True
        return super().keyboard_on_key_down(window, keycode, text, modifiers)


class _ChoiceDropDown(DropDown):
    """Opaque panel with enough inset to distinguish the menu from its trigger."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.container.padding = dp(4)
        self.container.spacing = dp(2)
        with self.canvas.before:
            Color(*MENU_COLOR)
            self._background = Rectangle()
        _add_outline(self, ACCENT_COLOR, inset=dp(1))
        self.bind(pos=self._update_background, size=self._update_background)
        self._update_background()

    def _update_background(self, *_args) -> None:
        self._background.pos = self.pos
        self._background.size = self.size

    def on_touch_up(self, touch):
        started_inside = self._touch_started_inside
        handled = super().on_touch_up(touch)
        # Options live in a separate window overlay. Keep the spinner focused
        # until the option receives its release and commits the selection.
        if started_inside and touch not in FocusBehavior.ignored_touch:
            FocusBehavior.ignored_touch.append(touch)
        return handled

    def dismiss(self, *args) -> None:
        # A queued dismissal could close a menu reopened by the next keystroke.
        if self.attach_to is not None:
            self._real_dismiss()


class AppSpinner(FocusBehavior, Spinner):
    """A select-only dropdown with independent current value and keyboard focus."""

    def __init__(self, **kwargs) -> None:
        self._active_index = 0
        super().__init__(
            dropdown_cls=_ChoiceDropDown,
            option_cls=_ChoiceRow,
            background_normal="",
            background_down="",
            background_color=SURFACE_COLOR,
            color=TEXT_COLOR,
            padding=(LABEL_PAD, 0, INDICATOR_SPACE, 0),
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
            **kwargs,
        )
        self._edge_tint = _add_outline(self, EDGE_COLOR, inset=dp(1))
        self._focus_tint = _add_outline(self, (*TEXT_COLOR[:3], 0), inset=dp(3))
        with self.canvas.after:
            Color(*TEXT_COLOR)
            self._chevron = Line(width=dp(1))
        self._trigger_reveal = Clock.create_trigger(self._reveal_option)
        self.bind(pos=self._update_geometry, size=self._update_geometry, is_open=self._update_open)
        self.bind(focus=self._update_focus, text=self._update_options, font_size=self._update_options)
        self._update_geometry()
        self._update_options()

    def _update_geometry(self, *_args) -> None:
        self.text_size = self.size
        x, y = self.right - INDICATOR_SPACE / 2, self.center_y
        tilt = dp(3) if self.is_open else -dp(3)
        self._chevron.points = (x - dp(5), y - tilt, x, y + tilt, x + dp(5), y - tilt)

    def _update_focus(self, *_args) -> None:
        self._focus_tint.a = int(self.focus)
        if self.focus:
            _reveal_focused(self)
        elif self.is_open:
            self.is_open = False

    def _update_dropdown(self, *args) -> None:
        if self.is_open:
            self.is_open = False
        super()._update_dropdown(*args)
        self._update_options()

    def _update_options(self, *_args) -> None:
        for index, option in enumerate(reversed(self._dropdown.container.children)):
            option.checked = option.text == self.text
            option.highlighted = self.is_open and index == self._active_index
            option.font_size = self.font_size

    def _update_open(self, *_args) -> None:
        self._update_geometry()
        self._edge_tint.rgba = ACCENT_COLOR if self.is_open else EDGE_COLOR
        if self.is_open:
            initial = self.values.index(self.text) if self.text in self.values else 0
            self._focus_option(initial)
        else:
            self._update_options()

    def _focus_option(self, index: int) -> None:
        self._active_index = index
        self._update_options()
        self._trigger_reveal()

    def _reveal_option(self, _dt) -> None:
        if self.is_open:
            rows = self._dropdown.container.children
            self._dropdown.scroll_to(rows[-self._active_index - 1], padding=0, animate=False)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key = keycode[1]
        if self.is_open and key == "tab" and set(modifiers) <= {"shift"}:
            self.is_open = False
        if not modifiers:
            if key in ACTIVATE_KEYS:
                if self.is_open:
                    self._dropdown.select(self.values[self._active_index])
                elif self.values:
                    self.is_open = True
                return True
            if key in {"up", "down"} and self.values:
                if self.is_open:
                    step = 1 if key == "down" else -1
                    self._focus_option(min(max(self._active_index + step, 0), len(self.values) - 1))
                else:
                    self.is_open = True
                return True
            if key == "escape" and self.is_open:
                self.is_open = False
                return True
        return super().keyboard_on_key_down(window, keycode, text, modifiers)

    def keyboard_on_key_up(self, window, keycode):
        if keycode[1] == "escape":
            return True
        return super().keyboard_on_key_up(window, keycode)
