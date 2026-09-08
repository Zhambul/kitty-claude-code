# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

from _render_styles import (
    MILLION_COUNT,
    SECONDS_PER_HOUR,
    THOUSAND_COUNT,
)


def duration(seconds: float) -> str:
    whole = max(0, int(seconds))
    hours, remainder = divmod(whole, SECONDS_PER_HOUR)
    minutes, rest = divmod(remainder, 60)
    if hours:
        return _hour_duration(hours, minutes)
    if minutes:
        return _minute_duration(minutes, rest)
    return f"{int(rest)}s"


def _hour_duration(hours: int, minutes: int) -> str:
    hour_text = str(int(hours))
    minute_text = str(int(minutes)).zfill(2)
    return f"{hour_text}h{minute_text}m"


def _minute_duration(minutes: int, seconds: int) -> str:
    minute_text = str(int(minutes))
    second_text = str(int(seconds)).zfill(2)
    return f"{minute_text}m{second_text}s"


def count(token_count: int) -> str:
    if token_count < THOUSAND_COUNT:
        return str(token_count)
    if token_count < MILLION_COUNT:
        scaled_count = round(token_count / THOUSAND_COUNT)
        return f"{scaled_count}k"
    scaled_count = round(token_count / MILLION_COUNT)
    return f"{scaled_count}M"
