# Copyright (c) 2026 Zhambyl Yermagambet
"""Polling checks for global harness usage."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.common.models.values.usage_row import UsageRowResponse, UsageWindowResponse
    from sdk.client import BaqylauClient

MAXIMUM_USED_PERCENT = 100


def rows_with_windows(
    client: BaqylauClient,
    harness: str,
    count: int,
) -> list[UsageRowResponse] | None:
    """Return usage rows that have the required window count.

    Returns:
        The matching rows, or None when no row matches.

    """
    rows = [
        row
        for row in client.usage.state().usage_rows
        if row.harness == harness
        and len(row.windows) >= count
    ]
    return rows or None


def windows_with_positive_duration(
    client: BaqylauClient,
    harness: str,
) -> list[UsageWindowResponse] | None:
    """Return usage windows when each duration is positive.

    Returns:
        The windows, or None when a duration is not positive.

    """
    windows = [
        window
        for row in client.usage.state().usage_rows
        if row.harness == harness
        for window in row.windows
    ]
    positive = windows and all(
        window.duration_minutes is not None
        and window.duration_minutes > 0
        for window in windows
    )
    return windows if positive else None


def windows_with_valid_percentage(
    client: BaqylauClient,
    harness: str,
) -> list[UsageWindowResponse] | None:
    """Return usage windows when each percentage is valid.

    Returns:
        The windows, or None when a percentage is not valid.

    """
    windows = [
        window
        for row in client.usage.state().usage_rows
        if row.harness == harness
        for window in row.windows
    ]
    valid = windows and all(
        0 <= window.used_percent <= MAXIMUM_USED_PERCENT
        for window in windows
    )
    return windows if valid else None


def rows_with_unique_window_keys(
    client: BaqylauClient,
    harness: str,
) -> list[UsageRowResponse] | None:
    """Return usage rows when each account has unique window keys.

    Returns:
        The rows, or None when there are no rows.

    Raises:
        AssertionError: If one account has duplicate window keys.

    """
    rows = [
        row
        for row in client.usage.state().usage_rows
        if row.harness == harness
    ]
    if not rows:
        return None
    failures = [
        row.display_name
        for row in rows
        if len({window.key for window in row.windows}) != len(row.windows)
    ]
    if failures:
        message = f"global usage for {harness!r} has duplicate window keys in {failures}"
        raise AssertionError(message)
    return rows
