"""Sample-based cursor measurements and extrema searches for the spectrum plot."""
from bisect import bisect_left
from dataclasses import dataclass, field
from math import isfinite
from typing import Sequence

import numpy as np


@dataclass
class MarkerSelection:
    pixels: dict[int, int] = field(default_factory=dict)
    selected: int | None = None
    reference: int | None = None
    adding: bool = False
    next_number: int = 1

    def place(self, pixel: int) -> int:
        if self.selected is None or self.adding:
            self.selected = self.next_number
            self.next_number += 1
            self.adding = False
        self.pixels[self.selected] = pixel
        return self.selected

    def remove_selected(self) -> int | None:
        number = self.selected
        self.adding = False
        if number is not None:
            del self.pixels[number]
            self.selected = next(reversed(self.pixels), None)
            if self.reference == number:
                self.reference = None
            if self.selected is None:
                self.next_number = 1
        return number


def search_origin(pixels: Sequence[int], pixel: int | None) -> float | None:
    if pixel is None:
        return None
    index = bisect_left(pixels, pixel)
    if index < len(pixels) and pixels[index] == pixel:
        return float(index)
    return index - 0.5


def nearest_index(pixels: Sequence[int], target: float) -> int:
    """Return the nearest index in a nonempty, sorted series of detector pixels."""
    right = bisect_left(pixels, target)
    if right == 0 or right == len(pixels):
        return min(right, len(pixels) - 1)
    left = right - 1
    return left if target - pixels[left] <= pixels[right] - target else right


def marker_value(
    pixels: Sequence[int], values: Sequence[float], pixel: int | None,
) -> tuple[int, float] | None:
    if pixel is None or not len(pixels):
        return None
    index = bisect_left(pixels, pixel)
    if index >= min(len(pixels), len(values)) or pixels[index] != pixel or not isfinite(values[index]):
        return None
    return pixel, float(values[index])


def marker_delta(a: tuple[int, float], b: tuple[int, float]) -> tuple[int, float]:
    return b[0] - a[0], b[1] - a[1]


def global_extremum(values: Sequence[float], *, maximum: bool) -> int | None:
    samples = np.asarray(values, dtype=float)
    finite = np.flatnonzero(np.isfinite(samples))
    if not finite.size:
        return None
    select = np.argmax if maximum else np.argmin
    return int(finite[select(samples[finite])])


def directional_extremum(
    values: Sequence[float],
    origin: float | None,
    *,
    direction: int,
    maximum: bool,
    prominence: float,
) -> int | None:
    """Find the next qualifying peak or valley, representing a plateau once."""
    samples = np.asarray(values, dtype=float)
    if not maximum:
        samples = -samples
    if samples.size < 3:
        return None

    changes = np.flatnonzero(samples[1:] != samples[:-1]) + 1
    starts, ends = changes[:-1], changes[1:]
    candidates = zip(starts, ends) if direction > 0 else zip(starts[::-1], ends[::-1])
    for start, end in candidates:
        center = (int(start) + int(end) - 1) // 2
        if origin is not None and (start <= origin < end or (center - origin) * direction <= 0):
            continue
        height = samples[start]
        before, after = samples[start - 1], samples[end]
        if not (isfinite(height) and isfinite(before) and isfinite(after) and height > max(before, after)):
            continue
        if prominence <= 0 or (
            _has_excursion(samples[:start][::-1], height, prominence)
            and _has_excursion(samples[end:], height, prominence)
        ):
            return center
    return None


def _has_excursion(side: np.ndarray, height: float, prominence: float) -> bool:
    """Stop at the first sufficient drop, higher sample, or data gap."""
    limit = height - prominence
    finite = np.isfinite(side)
    stops = np.flatnonzero(~finite | (side > height) | (side <= limit))
    return bool(stops.size and finite[stops[0]] and side[stops[0]] <= limit)
