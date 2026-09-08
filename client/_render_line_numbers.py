# Copyright (c) 2026 Zhambyl Yermagambet
"""Format numbered terminal rows."""

from __future__ import annotations

import _render_styles as styles


def _number_prefix(number: int, number_width: int) -> tuple[styles.Span, ...]:
    number_text = str(number).rjust(number_width)
    return (styles.Span(f" {number_text} ", styles.DIM),)
