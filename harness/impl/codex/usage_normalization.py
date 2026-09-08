# Copyright (c) 2026 Zhambyl Yermagambet
"""Normalize Codex app-server rate limits."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.impl.codex.usage_models import NormalizedRateLimits, NormalizedRateLimitWindow

if TYPE_CHECKING:
    from harness.impl.codex import usage_rate_limit_documents as rate_limit_documents


def normalize_rate_limits(
    account_rate_limits_response: rate_limit_documents.AccountRateLimitsResponse | None,
) -> NormalizedRateLimits | None:
    """Return normalized rate limits, or nothing when they are incomplete.

    Returns:
        Normalized rate limits, or nothing when they are incomplete.

    """
    rate_limits = None if account_rate_limits_response is None else account_rate_limits_response.rate_limits
    if rate_limits is None:
        return None
    windows = tuple(
        normalized
        for window in (rate_limits.primary, rate_limits.secondary)
        if (normalized := _window(window)) is not None
    )
    if not windows:
        return None
    return NormalizedRateLimits(plan=rate_limits.plan_type or "", windows=windows)


def _window(
    window: rate_limit_documents.RateLimitWindowResult | None,
) -> NormalizedRateLimitWindow | None:
    if window is None or window.used_percent is None or window.window_duration_mins is None:
        return None
    return NormalizedRateLimitWindow(
        used_percent=window.used_percent,
        duration_minutes=int(window.window_duration_mins),
        resets_at=window.resets_at,
    )
