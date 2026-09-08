# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert Claude rate limits into canonical usage windows."""

from harness.impl.claude_code.usage import live_documents, window_values
from harness.models.usage import UsageWindowSample

ACCOUNT_WINDOWS = ("five_hour", "seven_day")
MAX_MODEL_WINDOWS = 6


def windows(
    live_rate_limits: live_documents.LiveRateLimits | None,
) -> tuple[UsageWindowSample, ...]:
    """Convert all valid limits into canonical samples.

    Returns:
        The canonical usage samples.

    """
    if live_rate_limits is None:
        return ()
    samples: dict[str, UsageWindowSample] = {}
    _add_account_windows(samples, live_rate_limits)
    _add_model_buckets(samples, live_rate_limits)
    _add_weekly_limits(samples, live_rate_limits)
    return tuple(samples.values())


def _add_account_windows(
    samples: dict[str, UsageWindowSample],
    live_rate_limits: live_documents.LiveRateLimits,
) -> None:
    for key, window in (
        ("five_hour", live_rate_limits.five_hour),
        ("seven_day", live_rate_limits.seven_day),
    ):
        if window is None:
            continue
        used_percent = window_values.percent(window.utilization)
        if used_percent is None:
            continue
        samples[key] = UsageWindowSample(
            key,
            used_percent,
            window_values.epoch_seconds(window.resets_at),
        )


def _add_model_buckets(
    samples: dict[str, UsageWindowSample],
    live_rate_limits: live_documents.LiveRateLimits,
) -> None:
    for bucket in live_rate_limits.model_scoped or ():
        if len(samples) >= len(ACCOUNT_WINDOWS) + MAX_MODEL_WINDOWS:
            break
        model_key = window_values.model_key(bucket.display_name)
        used_percent = window_values.percent(bucket.utilization)
        if model_key is None or used_percent is None:
            continue
        samples[model_key] = UsageWindowSample(
            model_key,
            used_percent,
            window_values.epoch_seconds(bucket.resets_at),
        )


def _add_weekly_limits(
    samples: dict[str, UsageWindowSample],
    live_rate_limits: live_documents.LiveRateLimits,
) -> None:
    for limit in live_rate_limits.limits:
        if len(samples) >= len(ACCOUNT_WINDOWS) + MAX_MODEL_WINDOWS:
            break
        sample = _weekly_sample(limit)
        if sample is not None:
            samples[sample.key] = sample


def _weekly_sample(
    limit: live_documents.LiveLimit,
) -> UsageWindowSample | None:
    model = None if limit.scope is None else limit.scope.model
    if model is None or "weekly" not in limit.kind.lower():
        return None
    model_key = window_values.model_key(model.display_name)
    used_percent = window_values.percent(limit.percent)
    if model_key is None or used_percent is None:
        return None
    return UsageWindowSample(
        model_key,
        used_percent,
        window_values.epoch_seconds(limit.resets_at),
    )
