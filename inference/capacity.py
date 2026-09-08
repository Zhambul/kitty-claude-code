# Copyright (c) 2026 Zhambyl Yermagambet
"""Calculate remaining model capacity from harness usage rows."""

from decimal import Decimal

from domain.ids import HarnessName
from harness.models.usage import (
    UsageRow,
)

EMPTY_CAPACITY = Decimal(0)
FULL_CAPACITY = Decimal(100)


def remaining_capacity(
    harness: HarnessName,
    rows: tuple[UsageRow, ...],
) -> Decimal:
    """Return the most constrained capacity for one harness.

    Returns:
        Most constrained capacity for one harness.

    """
    matching_rows = tuple(row for row in rows if row.harness == harness)
    if any(row.authentication_error for row in matching_rows):
        return EMPTY_CAPACITY
    windows = tuple(window for row in matching_rows for window in row.windows)
    if not windows:
        return FULL_CAPACITY
    remaining = min(FULL_CAPACITY - window.used_percent for window in windows)
    return max(EMPTY_CAPACITY, remaining)
