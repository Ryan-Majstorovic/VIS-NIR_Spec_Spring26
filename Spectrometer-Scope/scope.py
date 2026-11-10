"""CCD scope: capture, inspect, and view CSCP diagnostics independently of the production GUI."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import struct
import sys
import threading
import zlib

import numpy as np
import serial
from serial.tools import list_ports

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from scope_protocol import Capture, HEADER, FIELDS, MODES, decode, read_capture
from scope_validate import validate

MODE_LABELS = {
    "production": "Production | 500 kS/s timing zoom",
    "productionoverview": "Production | full frame overview",
    "fast": "1.33 MS/s | original ICG",
    "corrected": "1.33 MS/s | trial ICG 8 us",
    "fastoverview": "Overview | original ICG",
    "correctedoverview": "Overview | trial ICG 8 us",
    "exposed": "1.33 MS/s | trial 100 us exposure",
    "exposedoverview": "Overview | trial 100 us exposure",
    "slow": "0.50 MS/s | original ICG",
    "zoom": "Legacy 4000 | Zoom",
    "overview": "Legacy 4000 | Overview",
}

def demo_capture():
    """Clearly marked synthetic data for UI and analyzer tests; no hardware claims."""
    m = dict.fromkeys(FIELDS, 0)
    m.update(capture_id=1, cpu_hz=96_000_000, logic_count=8192, adc_count=4000,
             logic_stride=8, adc_first_delay_cycles=48, logic_stride_cycles=12,
             frame_period_cycles=768000, integration_us=10, pin_mapping=1,
             board_inversion_mask=7, flags=0x80000001, tim1_arr=47, tim1_ccr=24,
             tim2_arr=191, tim3_psc=47, tim3_arr=19, tim3_ccr=12,
             tim4_psc=47, tim4_arr=15999, tim4_ccr=1224,
             logic_start_phase_ticks=15800, mode=1, build_family=0x10000)
    cycles = np.arange(8192, dtype=np.uint32) * 12 + 12
    us = cycles / 96 + 7900
    phase = us % 8000
    phi = (np.remainder(us + 0.125, 0.5) < 0.25).astype(np.uint32)
    sh = (np.remainder(us - 0.5, 10) < 6).astype(np.uint32)
    icg = (phase >= 612).astype(np.uint32)
    adc = (np.remainder(us - 612.5, 2) < 1).astype(np.uint32)
    ports = ((1-phi) << 8) | ((1-sh) << 6) | ((1-icg) << 22) | (adc << 5)
    logic = np.column_stack((cycles, ports)).astype("<u4")
    x = np.arange(4000)
    analog = np.where(x < 315, 3527, 1902 + x / 12).astype("<u2")
    header = HEADER.pack(b"CSCP", 1, HEADER.size, *(m[k] for k in FIELDS))
    wire = header + logic.tobytes() + analog.tobytes()
    return decode(wire + struct.pack("<I", zlib.crc32(wire)))


def source_label(capture):
    if capture.metadata["flags"] & 0x80000000:
        return "SIMULATED - no hardware measurement"
    m = capture.metadata
    icg_us = m['tim4_ccr']*(m['tim4_psc']+1)/m['cpu_hz']*1e6
    return f"GPIO + ADC | ICG low {icg_us:g} us | exposure {m['integration_us']} us | detector polarity inferred"


def save_capture(capture, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    name = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + f"_{capture.metadata['capture_id']}"
    path = directory / f"{name}.cscp"
    path.write_bytes(capture.wire)
    report = validate(capture)
    report["source"] = source_label(capture)
    report["metadata"] = capture.metadata
    (directory / f"{name}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    np.savetxt(directory / f"{name}_adc.csv", np.column_stack((np.arange(len(capture.adc)), capture.adc_time_us, capture.adc_hold_time_us, capture.adc)),
               delimiter=",", header="adc_sample_index,projected_trigger_us,estimated_hold_us,raw_adc_count", comments="")
    return path, report


def make_figure(capture, *, inferred=True, window="Full", cursor=None, auto_video=False, x_limits=None):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    fig = Figure(figsize=(11.5, 6.2), dpi=110, layout="constrained")
    video = fig.add_subplot(211)
    clocks = fig.add_subplot(212, sharex=video)
    t = capture.frame_time_us
    adc_t = capture.adc_hold_time_us
    m = capture.metadata
    icg_rise = m["tim4_ccr"]*(m["tim4_psc"]+1)/m["cpu_hz"]*1e6
    report = validate(capture)
    candidate = report["transition_candidate"]
    limits = {"Frame start": (-20, 100), "ICG rise": (icg_rise-10, icg_rise+85), "Master clock": (-1, 3),
              "Leading pixels": (icg_rise+20, icg_rise+90),
              "Frame end": (icg_rise+7320, icg_rise+7400),
              "Raw step": ((adc_t[candidate['sample']]-50, adc_t[candidate['sample']]+100) if candidate else (0, 1000))}
    video.plot(adc_t, capture.adc, color="#007f8a", linewidth=0.8, marker=".", markersize=2)
    video.set_ylabel("Raw ADC count")
    video.set_ylim(0, 4095)
    if auto_video and len(capture.adc):
        bounds = x_limits or limits.get(window)
        values = capture.adc[(adc_t>=bounds[0]) & (adc_t<=bounds[1])] if bounds else capture.adc
        if not len(values): values = capture.adc
        low, high = float(values.min()), float(values.max())
        margin = max(10, (high-low)*0.08)
        video.set_ylim(max(0, low-margin), min(4095, high+margin))
    m = capture.metadata
    period = (m["tim2_psc"]+1)*(m["tim2_arr"]+1)/m["cpu_hz"]*1e6
    video.set_title(f"Raw video: {len(capture.adc):,} ADC samples | {1/period:.3f} MS/s | {capture.pixel_period_us/period:.2f} samples/pixel", loc="left", fontsize=10)
    pixel_period = capture.pixel_period_us
    icg_rise = m["tim4_ccr"]*(m["tim4_psc"]+1)/m["cpu_hz"]*1e6
    first_active = icg_rise + 32*pixel_period
    final_active = first_active + 3648*pixel_period
    video.axvspan(first_active, final_active, alpha=0.07, color="#007f8a")
    video.axvline(first_active, color="#888888", linestyle="--", linewidth=0.8)
    bottom_y, top_y = video.get_ylim()
    if window == "Full":
        video.text(0.02, 0.96, "Shading: nominal active region referenced to ICG rise; alignment unverified",
                   transform=video.transAxes, fontsize=8, va="top", color="#555555")
    else:
        video.text(first_active, top_y-(top_y-bottom_y)*0.04, " Nominal active start", fontsize=8, color="#555555", va="top", clip_on=True)
    for start, count, label, color in ((0, 16, "16 dummy", "#d7bd88"), (16, 13, "13 shielded", "#adacca"), (29, 3, "3 buffer", "#bcabab")):
        left = icg_rise + start*pixel_period
        video.axvspan(left, left+count*pixel_period, alpha=0.3, color=color)
        if window in ("ICG rise", "Frame start", "Leading pixels"):
            video.text(left, bottom_y+(top_y-bottom_y)*0.92, label, fontsize=7, rotation=90, va="top", clip_on=True)
    for edge, label in ((0, "ICG fall"), (icg_rise, "ICG rise")):
        video.axvline(edge, color="#bd7527", linewidth=0.6)
    for key, label in (("leading_half_drop_us", "Leading optical change"), ("trailing_half_return_us", "Trailing optical change")):
        when = report['video_features'][key]
        if when is not None:
            video.axvline(when, color="#476abd", linestyle="--", linewidth=0.8)
            if window != 'Full':
                video.text(when, bottom_y+(top_y-bottom_y)*0.18, label, fontsize=8, color='#476abd', clip_on=True)
    if candidate:
        when = adc_t[candidate["sample"]]
        video.axvline(when, color="#d06724", linestyle="--", linewidth=1)
        video.text(when, bottom_y+(top_y-bottom_y)*0.08, f" Raw step candidate: {candidate['sample']}", fontsize=8, color="#a64b19", clip_on=True)
    colors = ["#5269c1", "#147f6a", "#bd7527", "#9d5096"]
    signals = capture.signals(inferred_detector=inferred)
    for lane, (name, signal) in enumerate(signals.items()):
        offset = 3 - lane
        # Plot raw observations. Long empty regions are not filled with a timer model.
        clocks.step(t, signal * 0.65 + offset, where="post", color=colors[lane], linewidth=0.75)
    clocks.set_yticks([3.32, 2.32, 1.32, 0.32], ["phiM", "SH", "ICG", "ADC clock"])
    clocks.set_ylim(-0.15, 3.95)
    clocks.set_title("Detector logic INFERRED from board inversion" if inferred else "Measured MCU GPIO pads (PA8 / PA6 / PB6 / PA5)", loc="left", fontsize=10)
    clocks.set_xlabel("Time from observed ICG fall (us); ADC hold time estimated from registers")
    for ax in (video, clocks):
        ax.grid(alpha=0.18)
        ax.spines[["top", "right"]].set_visible(False)
    if window in limits:
        video.set_xlim(*limits[window])
    else:
        video.set_xlim(min(float(t[0]), float(adc_t[0]) if len(adc_t) else 0),
                       max(float(t[-1]), float(adc_t[-1]) if len(adc_t) else 0))
    if cursor is not None:
        for ax in (video, clocks):
            ax.axvline(cursor, color="#d54949", linewidth=0.7)
    if x_limits is not None:
        video.set_xlim(*x_limits)
    fig.suptitle(source_label(capture), fontsize=10, color="#a65120" if m["flags"] & 0x80000000 else "#334455")
    return fig


def launch_gui(args):
    os.environ.setdefault("KIVY_NO_ARGS", "1")
    os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")
    from kivy.config import Config
    Config.set("graphics", "width", "1440")
    Config.set("graphics", "height", "900")
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.core.window import Window
    from kivy.graphics.texture import Texture
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.image import Image
    from kivy.uix.label import Label
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.spinner import Spinner
    from kivy.uix.textinput import TextInput

    class ScopeApp(App):
        title = "CCD Scope - TCD1304DG timing and frame validation"

        def build(self):
            Window.clearcolor = (0.055, 0.075, 0.10, 1)
            self.capture = None
            self.busy = False
            self.repeat = False
            self.window_name = args.view
            self.custom_limits = None
            root = BoxLayout(orientation="vertical", padding=14, spacing=10)
            root.add_widget(Label(text="CCD SCOPE   |   TCD1304DG", font_size=23, bold=True, size_hint_y=None, height=40, halign="left"))
            toolbar = BoxLayout(size_hint_y=None, height=42, spacing=8)
            ports = [p.device for p in list_ports.comports()] or [args.port]
            self.port = Spinner(text=args.port, values=ports, size_hint_x=None, width=110)
            toolbar.add_widget(self.port)
            self.mode = Spinner(text=MODE_LABELS[args.mode], values=tuple(MODE_LABELS.values()), size_hint_x=2)
            toolbar.add_widget(self.mode)
            for title, callback in [("Capture", lambda *_: self.acquire(self.selected_mode())), ("Repeat", self.toggle_repeat), ("Save PNG", self.save_plot)]:
                button = Button(text=title)
                button.bind(on_release=callback)
                toolbar.add_widget(button)
            self.polarity = Spinner(text="Detector inferred", values=("Detector inferred", "MCU pads"))
            self.polarity.bind(text=lambda *_: self.draw())
            toolbar.add_widget(self.polarity)
            root.add_widget(toolbar)
            views = BoxLayout(size_hint_y=None, height=34, spacing=6)
            for text in ("Full", "Frame start", "ICG rise", "Leading pixels", "Master clock", "Frame end", "Raw step"):
                button = Button(text=text)
                button.bind(on_release=lambda _, key=text: self.set_window(key))
                views.add_widget(button)
            self.video_scale = Spinner(text="Auto video" if args.auto_video else "Full ADC", values=("Full ADC", "Auto video"))
            self.video_scale.bind(text=lambda *_: self.draw())
            views.add_widget(self.video_scale)
            root.add_widget(views)
            body = BoxLayout(spacing=12)
            self.plot = Image(fit_mode="contain", size_hint_x=0.70)
            self.plot.bind(on_touch_down=self.cursor)
            body.add_widget(self.plot)
            side = BoxLayout(orientation="vertical", size_hint_x=0.30, spacing=8)
            side.add_widget(Label(text="VALIDATION  |  PASS / FAIL / UNVERIFIED", font_size=14, size_hint_y=None, height=30))
            scroll = ScrollView()
            self.findings = Label(text="Capture a trace to inspect timing.", markup=True, size_hint_y=None, valign="top", halign="left", padding=(8, 8), font_size=13)
            self.findings.bind(width=lambda widget, value: setattr(widget, "text_size", (value, None)))
            self.findings.bind(texture_size=lambda widget, value: setattr(widget, "height", value[1]))
            scroll.add_widget(self.findings)
            side.add_widget(scroll)
            body.add_widget(side)
            root.add_widget(body)
            self.status = Label(text="Ready. Measured at MCU pads; sensor-pin timing requires external observation.", font_size=13, size_hint_y=None, height=34)
            root.add_widget(self.status)
            if args.demo:
                Clock.schedule_once(lambda *_: self.show_capture(demo_capture(), "SIMULATED PREVIEW"), 0.3)
            elif args.open:
                self.capture = decode(Path(args.open).read_bytes())
                Clock.schedule_once(lambda *_: self.show_capture(self.capture, str(args.open)), 0.3)
            elif args.acquire:
                Clock.schedule_once(lambda *_: self.acquire(self.selected_mode()), 0.3)
            if args.screenshot:
                Clock.schedule_once(self.screenshot, 2.5)
            return root

        def screenshot(self, *_):
            self.root.export_to_png(str(args.screenshot))
            self.stop()

        def set_window(self, name):
            self.window_name = name
            self.custom_limits = None
            self.draw()

        def selected_mode(self):
            return next(key for key, label in MODE_LABELS.items() if label == self.mode.text)

        def toggle_repeat(self, *_):
            self.repeat = not self.repeat
            if self.repeat:
                self.acquire(self.selected_mode())
            else:
                self.status.text = "Repeat stopped. Current capture retained."

        def acquire(self, mode):
            if self.busy:
                return
            self.busy = True
            self.status.text = f"Capturing {mode} on {self.port.text}..."
            port_name = self.port.text

            def worker():
                try:
                    with serial.Serial(port_name, 115200, timeout=0.15, write_timeout=1) as port:
                        capture = read_capture(port, mode)
                    path, _ = save_capture(capture, HERE / "captures")
                    Clock.schedule_once(lambda _, c=capture, p=str(path): self.show_capture(c, p))
                except Exception as exc:
                    Clock.schedule_once(lambda _, message=str(exc): self.failed(message))
            threading.Thread(target=worker, daemon=True).start()

        def failed(self, message):
            self.busy = False
            self.repeat = False
            self.status.text = message

        def show_capture(self, capture, source):
            self.busy = False
            self.capture = capture
            report = validate(capture)
            colors = {"PASS": "71d7ad", "FAIL": "ff887d", "WARN": "f2c16e", "INFO": "9cc3e7", "UNVERIFIED": "b6bac6"}
            self.findings.text = "\n\n".join(f"[b][color={colors[c['status']]}]{c['status']}[/color]  {c['name']}[/b]\n{c['value']}\n[color=929dad]{c['basis']}[/color]" for c in report["checks"])
            self.status.text = f"Capture {capture.metadata['capture_id']} saved: {source}"
            self.draw()
            if self.repeat:
                Clock.schedule_once(lambda *_: self.acquire(self.selected_mode()) if self.repeat else None, 1)

        def draw(self, cursor=None):
            if self.capture is None:
                return
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            self.figure = make_figure(self.capture, inferred=self.polarity.text == "Detector inferred", window=self.window_name, cursor=cursor,
                                      auto_video=self.video_scale.text == "Auto video", x_limits=self.custom_limits)
            self.figure.set_size_inches(max(self.plot.width, 600)/110, max(self.plot.height, 440)/110)
            canvas = FigureCanvasAgg(self.figure)
            canvas.draw()
            w, h = canvas.get_width_height()
            texture = Texture.create(size=(w, h), colorfmt="rgba")
            texture.blit_buffer(bytes(canvas.buffer_rgba()), colorfmt="rgba", bufferfmt="ubyte")
            texture.flip_vertical()
            self.plot.texture = texture

        def cursor(self, widget, touch):
            if not widget.collide_point(*touch.pos) or self.capture is None:
                return False
            # Map the rendered image through its letterbox to Matplotlib axes.
            nw, nh = widget.norm_image_size
            left = widget.center_x - nw/2
            bottom = widget.center_y - nh/2
            px = (touch.x-left)/nw * self.figure.bbox.width
            py = (touch.y-bottom)/nh * self.figure.bbox.height
            for ax in self.figure.axes:
                if ax.bbox.contains(px, py):
                    time_us, _ = ax.transData.inverted().transform((px, py))
                    if getattr(touch, "button", "") in ("scrollup", "scrolldown"):
                        factor = 0.7 if touch.button == "scrollup" else 1.4
                        lower, upper = ax.get_xlim()
                        self.custom_limits = (time_us + (lower-time_us)*factor, time_us + (upper-time_us)*factor)
                        self.draw()
                        return True
                    if not len(self.capture.adc):
                        return True
                    i = int(np.argmin(np.abs(self.capture.adc_hold_time_us-time_us)))
                    self.status.text = f"Cursor {time_us:.3f} us | ADC sample {i}: {self.capture.adc[i]} counts | {time_us/self.capture.pixel_period_us:.2f} pixel periods after ICG fall; hold time estimated"
                    self.draw(cursor=float(time_us))
                    return True
            return False

        def save_plot(self, *_):
            if self.capture is not None:
                target = HERE / "captures" / (datetime.now().strftime("scope_%Y%m%d_%H%M%S") + ".png")
                target.parent.mkdir(exist_ok=True)
                self.figure.savefig(target, dpi=160)
                self.status.text = str(target)

    ScopeApp().run()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    capture = sub.add_parser("capture")
    capture.add_argument("--port", default="COM3")
    capture.add_argument("--mode", choices=MODES, default="production")
    capture.add_argument("--output", type=Path, default=HERE / "captures")
    inspect = sub.add_parser("inspect")
    inspect.add_argument("path", type=Path)
    inspect.add_argument("--plot", type=Path)
    gui = sub.add_parser("gui")
    gui.add_argument("--port", default="COM3")
    gui.add_argument("--mode", choices=MODES, default="production")
    gui.add_argument("--open", type=Path)
    gui.add_argument("--demo", action="store_true")
    gui.add_argument("--screenshot", type=Path)
    gui.add_argument("--view", choices=("Full", "Frame start", "ICG rise", "Leading pixels", "Master clock", "Frame end", "Raw step"), default="Full")
    gui.add_argument("--auto-video", action="store_true")
    gui.add_argument("--acquire", action="store_true", help="Acquire a real fast trace when the window opens.")
    args = parser.parse_args()
    if args.command == "gui":
        launch_gui(args)
        return 0
    if args.command == "capture":
        with serial.Serial(args.port, 115200, timeout=0.15, write_timeout=1) as port:
            trace = read_capture(port, args.mode)
        path, report = save_capture(trace, args.output)
        print(f"Saved {path}")
    else:
        trace = decode(args.path.read_bytes())
        report = validate(trace)
        if args.plot:
            make_figure(trace).savefig(args.plot, dpi=150)
    print(json.dumps(report, indent=2))
    return 1 if report["has_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
