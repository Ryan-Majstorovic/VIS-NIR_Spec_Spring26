"""Timing checks against Toshiba Rev 1.5 pp. 5-8; never promote a model to a measurement."""
import numpy as np
from scope_protocol import ADC_TRIGGER_INTERNAL
from scope_video import video_features

DATASHEET = "https://toshiba.semicon-storage.com/info/docget.jsp?did=13709&prodName=TCD1304DG"


def edge_indices(values, rising=True):
    return np.flatnonzero(np.diff(values.astype(np.int8)) == (1 if rising else -1)) + 1


def validate(capture):
    m, t = capture.metadata, capture.time_us
    signals = capture.signals(inferred_detector=True)
    checks = []
    dt = np.diff(t)
    uncertainty = float(np.max(dt)) + 4e6 / m["cpu_hz"] if len(dt) else float("inf")

    def add(name, status, value, basis, scope="MCU measurement / inferred board polarity"):
        checks.append(dict(name=name, status=status, value=value, basis=basis, scope=scope))

    def interval(name, values, lower, upper, basis):
        values = np.asarray(values, dtype=float)
        if not len(values):
            add(name, "UNVERIFIED", "No complete interval in this window", basis)
            return
        # Timestamps mark the right endpoint of each observation interval.
        # Subtracting two such endpoints has at most one maximum sample-gap
        # error in either direction, plus the inter-port read-skew allowance.
        error = uncertainty
        if np.any(values + error < lower) or (upper is not None and np.any(values - error > upper)):
            status = "FAIL"
        elif np.all(values - error >= lower) and (upper is None or np.all(values + error <= upper)):
            status = "PASS"
        else:
            status = "UNVERIFIED"
        add(name, status, f"{values.min():.4f}..{values.max():.4f} us; uncertainty ±{error:.4f} us", basis)

    def widths(name):
        s = signals[name]
        rises, falls = edge_indices(s), edge_indices(s, False)
        out = []
        for r in rises:
            after = falls[falls > r]
            if len(after):
                out.append(t[after[0]] - t[r])
        return out

    def edge_interval(name, pairs, lower, upper, basis):
        if not pairs:
            interval(name, [], lower, upper, basis)
            return
        # Each edge lies between its preceding observation and its timestamp.
        # Use those two local brackets, not unrelated ISR/DMA gaps elsewhere.
        values = np.array([t[b]-t[a] for a, b in pairs])
        skew = 4e6/m['cpu_hz']
        lo = np.array([t[b-1]-t[a]-skew for a, b in pairs])
        hi = np.array([t[b]-t[a-1]+skew for a, b in pairs])
        if np.any(hi < lower) or (upper is not None and np.any(lo > upper)):
            status = 'FAIL'
        elif np.all(lo >= lower-1e-9) and (upper is None or np.all(hi <= upper+1e-9)):
            status = 'PASS'
        else:
            status = 'UNVERIFIED'
        add(name, status, f'{values.min():.4f}..{values.max():.4f} us; edge bounds {lo.min():.4f}..{hi.max():.4f} us', basis)

    target_count = m.get("adc_target_count", 4000)
    add("Capture integrity", "PASS", "Header, payload length, CRC32 and increasing timestamps verified", f"CSCP v{m.get('protocol_version', 1)} protocol", "USB capture")
    add("ADC DMA", "PASS" if m["flags"] & 1 and m["adc_dma_remaining"] == 0 and m["adc_errors"] == 0 and m.get("dma_errors", 0) == 0 and not m.get("adc_sr", 0) & 32 and len(capture.adc) == target_count else "FAIL",
        f"{len(capture.adc)}/{target_count} samples; remaining={m['adc_dma_remaining']}; ADC errors=0x{m['adc_errors']:x}; DMA errors=0x{m.get('dma_errors', 0):x}; SR=0x{m.get('adc_sr', 0):x}", "Production frame acquisition" if m.get('mode', 1) >= 10 else "Extended diagnostic acquisition", "DMA status")
    add("ADC range", "PASS" if len(capture.adc) and np.max(capture.adc) <= 4095 else "FAIL",
        f"{int(capture.adc.min())}..{int(capture.adc.max())} counts" if len(capture.adc) else "No ADC samples", "12-bit ADC bounds", "Raw ADC payload")
    add("Logic time resolution", "INFO", f"median {np.median(dt)*1000:.1f} ns; maximum gap {np.max(dt)*1000:.1f} ns",
        "Actual DWT timestamp differences; sequential GPIO reads add uncertainty", "MCU GPIO sampling")
    # A segmented timer DMA burst can cause an isolated GPIO sampling gap.
    # Measure only the longest contiguous interval with every gap <250 ns;
    # never count edges across an unresolved interval.
    breaks = np.r_[0, np.flatnonzero(dt >= 0.25)+1, len(t)]
    begin, end = max(zip(breaks[:-1], breaks[1:]), key=lambda pair: pair[1]-pair[0])
    resolved_clock = end-begin > 4 and t[end-1]-t[begin] >= 100
    phi_rises = edge_indices(signals["phiM"][begin:end]) + begin
    if resolved_clock and len(phi_rises) > 100:
        # A median of quantized single periods is biased (e.g. a 500 ns clock
        # sampled every 198 ns alternates 396/594 ns observations). Fit the
        # timestamps over many cycles instead of rounding to a sample interval.
        phi_period = float(np.polyfit(np.arange(len(phi_rises)), t[phi_rises], 1)[0])
        frequency = 1 / phi_period
        add("Master clock target", "PASS" if 1.998 <= frequency <= 2.002 else "FAIL", f"{frequency:.4f} MHz over {t[end-1]-t[begin]:.1f} us without unresolved gaps",
            "Project target 2 MHz; Toshiba p.5 gives supply-dependent clock limits")
    else:
        phi_period = None
        add("Master clock target", "FAIL" if resolved_clock and t[-1]-t[0] > 5 else "UNVERIFIED",
            "No repeated master-clock edges observed" if resolved_clock else "Sampling cannot resolve the 2 MHz clock; use Zoom",
            "Observed clock activity; do not infer a clock from programmed timer values")
    interval("t3 SH high width", widths("SH"), 1.0, None, "Toshiba p.8: SH high at least 1 us")
    sh_widths = widths("SH")
    if len(sh_widths) > 1:
        spread = float(np.ptp(sh_widths))
        add("SH width consistency", "PASS" if spread <= 2*uncertainty else "FAIL",
            f"Observed width spread {spread:.4f} us", "Toshiba p.8: keep SH pulse width constant")
    sh_rises = edge_indices(signals["SH"])
    interval("Electronic shutter period", np.diff(t[sh_rises]), 10, None, "Toshiba p.8: integration at least 10 us")
    icg_falls = edge_indices(signals["ICG"], False)
    sh_falls = edge_indices(signals["SH"], False)
    icg_rises = edge_indices(signals["ICG"])
    t2 = []
    t2_pairs = []
    for fall in icg_falls:
        # Coarsely sampled ICG and SH edges can fall in the same observation.
        # Treat this as a zero-width uncertain interval, not the next SH cycle.
        following = sh_rises[sh_rises >= fall]
        if len(following):
            t2.append(t[following[0]] - t[fall])
            t2_pairs.append((fall, following[0]))
    edge_interval("t2 ICG fall to SH rise", t2_pairs, 0.1, 1.0, "Toshiba p.8: 100..1000 ns")
    t1 = []
    t1_pairs = []
    overlap = False
    overlap_delays = []
    ambiguous_overlap = False
    for rise in icg_rises:
        previous = sh_falls[sh_falls < rise]
        if signals["SH"][rise]:
            previous_rises = sh_rises[sh_rises <= rise]
            next_falls = sh_falls[sh_falls > rise]
            if len(previous_rises) and len(next_falls) and t[rise]-t[previous_rises[-1]] > uncertainty and t[next_falls[0]]-t[rise] > uncertainty:
                overlap = True
                overlap_delays.append(t[next_falls[0]]-t[rise])
            else:
                ambiguous_overlap = True
        if len(previous):
            t1.append(t[rise] - t[previous[-1]])
            t1_pairs.append((previous[-1], rise))
    if overlap:
        add("t1 ICG rise after SH fall", "FAIL", f"ICG rises {min(overlap_delays):.4f}..{max(overlap_delays):.4f} us before SH falls (SH still high)",
            "Toshiba p.8: ICG rise follows SH fall by at least 1 us")
    elif ambiguous_overlap:
        add("t1 ICG rise after SH fall", "UNVERIFIED", "SH/ICG overlap cannot be resolved at this sampling interval; use Zoom",
            "Toshiba p.8: ICG rise follows SH fall by at least 1 us")
    else:
        edge_interval("t1 ICG rise after SH fall", t1_pairs, 1.0, None, "Toshiba p.8: at least 1 us; typical 5 us")
    add("t4 master phase at ICG rise", "UNVERIFIED", "Sensor-pin phase and driver propagation require a probe/loopback with adequate resolution",
        "Toshiba p.8: phiM must remain high at the specified ICG transition", "Sensor pins")
    period_adc = (m["tim2_psc"] + 1) * (m["tim2_arr"] + 1) / m["cpu_hz"] * 1e6
    pixel_period = capture.pixel_period_us
    samples_per_pixel = pixel_period / period_adc
    add("ADC sampling", "INFO", f"{1/period_adc:.6f} MS/s; {period_adc:.3f} us/sample; {samples_per_pixel:.3f} ADC samples/CCD pixel",
        "CCD pixels remain four master cycles; ADC samples are not pixel indices", "Register projection")
    if "adc_clock_hz" in m:
        minimum_period = (m["adc_sample_cycles"] + 12 + 2) / m["adc_clock_hz"] * 1e6 + 1e6/m["cpu_hz"]
        add("ADC conversion budget", "PASS" if period_adc >= minimum_period else "FAIL",
            f"{period_adc:.4f} us trigger spacing; at least {minimum_period:.4f} us conversion/trigger budget; {m['adc_sample_cycles']} sample cycles",
            "ST DS10314 Rev 8 table 65: sampling + 12-bit conversion + trigger latency; 1/PCLK2 included", "ADC register projection")
        add("ADC aperture", "UNVERIFIED", f"{m['adc_sample_cycles']/m['adc_clock_hz']*1e6:.3f} us acquisition; estimated hold instant {capture.adc_hold_time_us[0]:.3f} us for first sample" if len(capture.adc) else "No samples",
            "Shorter sampling needs a sufficiently low-impedance analog source; input settling is not measured", "Analog input")
        if m["flags"] & 1 and len(capture.adc):
            measured_completion = m["adc_complete_cycles"] / m["cpu_hz"]*1e6 + float(capture.frame_time_us[0] - t[0])
            predicted_completion = float(capture.adc_hold_time_us[-1] + 12/m["adc_clock_hz"]*1e6)
            completion_error = measured_completion - predicted_completion
            add("ADC capture duration", "PASS" if -uncertainty <= completion_error <= 3 + uncertainty else "FAIL",
                f"DMA complete {measured_completion:.3f} us; expected {predicted_completion:.3f} us; difference {completion_error:.3f} us",
                "DWT timestamp in DMA completion ISR versus N timer triggers; 3 us ISR allowance, gross missed triggers detected, not an individual aperture measurement", "DMA timing + register projection")
    adc_rises = edge_indices(signals["ADC clock"])
    if m["flags"] & ADC_TRIGGER_INTERNAL:
        measured_period_adc = None
        add("ADC clock output", "PASS" if not np.any(signals["ADC clock"]) else "FAIL",
            "PA5 configured as analog with TIM2 CH1 disabled; ADC trigger is internal",
            "Production firmware configuration and captured GPIO state", "MCU registers / GPIO")
    elif len(adc_rises) > 4 and uncertainty < period_adc/2:
        measured_period_adc = float(np.polyfit(np.arange(len(adc_rises)), t[adc_rises], 1)[0])
        add("ADC clock output", "PASS" if abs(measured_period_adc-period_adc) < 0.02 else "FAIL",
            f"{1/measured_period_adc:.4f} MHz; {measured_period_adc:.4f} us period",
            "Observed PA5 timer output compared with TIM2 register readback", "MCU GPIO measurement")
        if m.get("mode", 1) >= 3:
            observed_start = float(capture.frame_time_us[adc_rises[0]])
            add("ADC trigger start" if m.get("mode", 1) >= 10 else "ADC start before frame", "PASS" if abs(observed_start-float(capture.adc_time_us[0])) <= uncertainty+0.15 else "FAIL",
                f"First PA5 rise {observed_start:.4f} us; programmed {capture.adc_time_us[0]:.4f} us",
                "Measured start edge against projected lead-in; internal trigger propagation included in tolerance", "MCU GPIO measurement")
        elif len(icg_rises):
            start = adc_rises[adc_rises >= icg_rises[0]]
            if len(start):
                add("ADC clock start after ICG rise", "INFO", f"{t[start[0]]-t[icg_rises[0]]:.4f} us; uncertainty ±{uncertainty:.4f} us",
                    "Measured GPIO edges; ADC aperture and analog settling remain unobserved", "MCU GPIO measurement")
    else:
        measured_period_adc = None
        add("ADC clock output", "UNVERIFIED", "Use Zoom to resolve the ADC trigger clock", "PA5 output sampling")
    if phi_period is not None:
        ratio = (measured_period_adc or period_adc) / phi_period
        expected_ratio = period_adc / ((m["tim1_psc"]+1)*(m["tim1_arr"]+1)/m["cpu_hz"]*1e6)
        add("ADC / master clock ratio", "PASS" if abs(ratio - expected_ratio) < 0.2 else "FAIL", f"{ratio:.4f} master cycles / ADC sample; {4/ratio:.3f} samples/pixel",
            "Compare measured clocks to selected ADC rate; CCD data rate remains master / 4", "Measured GPIO clocks" if measured_period_adc else "Measured clock + register projection")
    else:
        add("ADC / master clock ratio", "UNVERIFIED", "Use a resolved Zoom capture", "Toshiba p.5: data rate = master / 4")
    interval("ICG readout high window", widths("ICG"), 3694 * pixel_period, None,
             "Project readout window must cover all 3694 sample periods; Toshiba pp.6-7 gives line geometry")
    candidate = None
    if len(capture.adc) > 64:
        a = capture.adc.astype(float)
        window = max(4, round(16 * samples_per_pixel))
        cs = np.r_[0, np.cumsum(a)]
        means = (cs[window:] - cs[:-window]) / window
        differences = means[window:] - means[:-window]
        i = int(np.argmax(np.abs(differences))) + window
        strength = float(differences[i-window])
        if abs(strength) > 64:
            icg_rise_us = m["tim4_ccr"]*(m["tim4_psc"]+1)/m["cpu_hz"]*1e6
            candidate_time = float(capture.adc_hold_time_us[i])
            candidate = {"sample": i, "window_delta_counts": strength, "offset_from_declared_start": i-32 if m.get("mode", 1) < 3 else None,
                         "estimated_hold_time_us": candidate_time,
                         "pixel_periods_from_icg_rise": (candidate_time-icg_rise_us)/pixel_period,
                         "evidence": "Largest baseline change over approximately 16 CCD pixel periods; not proof of first photosite"}
            add("Raw video transition", "WARN", f"ADC sample {i}, estimated hold {candidate_time:.3f} us; {strength:.1f} count change",
                "Heuristic only; verify under controlled uniform illumination", "Raw ADC payload")
        else:
            add("Raw video transition", "INFO", "No large baseline transition detected", "No optical boundary can be certified from a flat trace", "Raw ADC payload")
    video = video_features(capture)
    contrast = video['leading_contrast_counts']
    if contrast is not None:
        add("Leading optical contrast", "INFO", f"Shielded-window median {video['regions']['shielded']:.1f}; early-active median {video['regions']['early_active']:.1f}; difference {contrast:.1f} counts",
            "Windows referenced to ICG rise and nominal geometry; compare covered/dim/bright traces", "Raw ADC / nominal windows")
    for name, key in (("Leading video half-drop", "leading_half_drop_us"), ("Trailing video half-return", "trailing_half_return_us")):
        when = video[key]
        add(name, "INFO" if when is not None else "UNVERIFIED",
            f"{when:.3f} us from ICG fall; {when-video['icg_rise_us']:.3f} us after ICG rise" if when is not None else "No sufficiently strong local optical boundary",
            "Local 50% contrast crossing; not the identity of a particular photosite; ADC time estimated", "Raw ADC feature")
    add("Physical pixel alignment", "UNVERIFIED", "Declared 32 + 3648 + 14 geometry is an overlay, not an observed pixel map",
        "Toshiba pp.6-7; controlled optical stimulus and verified trigger reference required", "Sensor / optics")
    add("Detector electrical timing", "UNVERIFIED", "GPIO pads measured before board; detector polarity inferred from inversion mask",
        "Driver propagation, output voltage, rise/fall times and analog settling are not measured", "Sensor pins")
    return {"datasheet_url": DATASHEET, "datasheet_revision": "1.5 (2026-05-20)",
            "sensor_validation": "UNVERIFIED", "has_failures": any(c["status"] == "FAIL" for c in checks),
            "uncertainty_us": uncertainty, "checks": checks, "transition_candidate": candidate,
            "video_features": video}
