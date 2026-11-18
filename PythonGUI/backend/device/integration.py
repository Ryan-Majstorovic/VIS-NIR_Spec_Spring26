"""Exact integration settings shared by numeric controls and command validation."""
from bisect import bisect_left, bisect_right
from decimal import Decimal

MIN_US = 10
BASE_FRAME_US = 8000
MAX_US = 5_000_000
SHORT_SETTINGS = tuple(us for us in range(MIN_US, BASE_FRAME_US + 1) if BASE_FRAME_US % us == 0)
UNIT_US = {"µs": Decimal(1), "ms": Decimal(1000), "s": Decimal(1_000_000)}


def valid_integration(us: int | Decimal) -> bool:
    return MIN_US <= us <= MAX_US and us == int(us) and (us > BASE_FRAME_US or BASE_FRAME_US % int(us) == 0)


def adjacent_settings(us: Decimal | int) -> tuple[int | None, int | None]:
    """Return strict neighbors without enumerating five million long settings."""
    if us > BASE_FRAME_US:
        lower = min(int(us) if us != int(us) else int(us) - 1, MAX_US)
        upper = max(int(us) + 1, BASE_FRAME_US + 1)
        return (lower if lower >= MIN_US else None, upper if upper <= MAX_US else None)
    left, right = bisect_left(SHORT_SETTINGS, us), bisect_right(SHORT_SETTINGS, us)
    return (SHORT_SETTINGS[left - 1] if left else None,
            SHORT_SETTINGS[right] if right < len(SHORT_SETTINGS) else BASE_FRAME_US + 1)


def parse_duration(text: str, unit: str) -> int:
    us = Decimal(text.strip()) * UNIT_US[unit]
    if not us.is_finite():
        raise ValueError("Enter a finite integration time.")
    if not valid_integration(us):
        lower, upper = adjacent_settings(us)
        raise ValueError(f"Unsupported duration. Adjacent settings: {lower or 'none'} µs and {upper or 'none'} µs.")
    return int(us)


def frame_interval_us(integration_us: int) -> int:
    return max(BASE_FRAME_US, integration_us)
