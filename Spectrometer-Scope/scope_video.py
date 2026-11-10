"""Local optical features; these are observations, not certified pixel indices."""
import numpy as np


def video_features(capture):
    m = capture.metadata
    t, a = capture.adc_hold_time_us, capture.adc.astype(float)
    pixel = capture.pixel_period_us
    rise = m['tim4_ccr']*(m['tim4_psc']+1)/m['cpu_hz']*1e6

    def median(first, last):
        values = a[(t >= rise+first*pixel) & (t < rise+last*pixel)]
        return float(np.median(values)) if len(values) >= 3 else None

    regions = {'leading_dummy': median(2, 15), 'shielded': median(17, 28),
               'early_active': median(36, 90), 'late_active': median(3550, 3650),
               'trailing': median(3682, 3692)}
    result = dict(icg_rise_us=rise, pixel_period_us=pixel, regions=regions,
                  leading_half_drop_us=None, trailing_half_return_us=None,
                  leading_contrast_counts=None, pixel_alignment='UNVERIFIED')
    black, active = regions['shielded'], regions['early_active']
    if black is not None and active is not None:
        contrast = black-active
        result['leading_contrast_counts'] = contrast
        if contrast > 20:
            indices = np.flatnonzero((t > rise+20*pixel) & (t < rise+45*pixel) & (a < black-contrast/2))
            if len(indices): result['leading_half_drop_us'] = float(t[indices[0]])
    tail, late = regions['trailing'], regions['late_active']
    if tail is not None and late is not None and tail-late > 20:
        indices = np.flatnonzero((t > rise+3660*pixel) & (t < rise+3695*pixel) & (a > late+(tail-late)/2))
        if len(indices): result['trailing_half_return_us'] = float(t[indices[0]])
    return result
