from __future__ import annotations

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget


class TooltipController:
    """Show one delayed description for the visible control under the pointer."""

    def __init__(self) -> None:
        self._targets: dict[Widget, str] = {}
        self._target: Widget | None = None
        self._label = Label(
            size_hint=(None, None), font_size=sp(13), padding=(dp(10), dp(7)),
            halign="left", valign="middle",
        )
        with self._label.canvas.before:
            Color(0.11, 0.16, 0.20, 1)
            self._background = RoundedRectangle(radius=[dp(5)])
        self._label.bind(pos=self._update_background, size=self._update_background)
        self._show_event = Clock.create_trigger(self._show, 0.5)

    def register(self, widget: Widget, description: str) -> None:
        self._targets[widget] = description

    def start(self) -> None:
        Window.bind(
            mouse_pos=self._on_mouse_pos,
            on_cursor_leave=self.dismiss,
            on_touch_down=self.dismiss,
        )

    def stop(self) -> None:
        Window.unbind(
            mouse_pos=self._on_mouse_pos,
            on_cursor_leave=self.dismiss,
            on_touch_down=self.dismiss,
        )
        self.dismiss()

    def dismiss(self, *_args) -> None:
        self._show_event.cancel()
        self._target = None
        if self._label.parent is Window:
            Window.remove_widget(self._label)

    def _on_mouse_pos(self, _window, pos: tuple[float, float]) -> None:
        target = self._target_at(pos)
        if target is self._target:
            return
        self.dismiss()
        if target is not None:
            self._target = target
            self._show_event()

    def _target_at(self, pos: tuple[float, float]) -> Widget | None:
        for widget in reversed(self._targets):
            if widget.get_root_window() is not Window:
                continue
            if not widget.collide_point(*widget.parent.to_widget(*pos)):
                continue

            # ScrollView clips its content to the viewport, even where a
            # child's transformed bounds extend beyond that viewport.
            ancestor = widget
            root = widget
            while isinstance(ancestor, Widget):
                if ancestor.opacity == 0:
                    break
                if isinstance(ancestor, ScrollView) and not ancestor.collide_point(*ancestor.parent.to_widget(*pos)):
                    break
                root = ancestor
                ancestor = ancestor.parent
            else:
                # A dropdown or modal can be above the app's root widget.
                if next((child for child in Window.children if child is not self._label), None) is root:
                    return widget
        return None

    def _show(self, _elapsed: float) -> None:
        target = self._target
        pos = Window.mouse_pos
        if target is None or self._target_at(pos) is not target:
            self.dismiss()
            return

        label = self._label
        margin = dp(8)
        label.text = self._targets[target]
        label.text_size = (None, None)
        label.texture_update()
        max_width = max(dp(1), min(dp(280), Window.width - 2 * margin))
        if label.texture_size[0] > max_width:
            label.text_size = (max_width, None)
            label.texture_update()
        label.size = label.texture_size

        x, y = pos
        offset = dp(14)
        below = y - label.height - offset
        label.pos = (
            max(margin, min(x + offset, Window.width - label.width - margin)),
            max(margin, min(below if below >= margin else y + offset, Window.height - label.height - margin)),
        )
        Window.add_widget(label, canvas="after")

    def _update_background(self, label: Label, _value) -> None:
        self._background.pos = label.pos
        self._background.size = label.size
