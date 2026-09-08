# Copyright (c) 2026 Zhambyl Yermagambet
"""Cache Codex rate-limit probe results."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from harness.impl.codex import usage_normalization
from harness.impl.codex.usage_models import (
    CacheEntry,
    ProbeResolution,
    ProbeResult,
    RateLimitsCollection,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from harness.runtime import HarnessRuntimeConfig

CACHE_SECONDS = 120.0
RETRY_SECONDS = 2.0
STALE_SECONDS = 300.0
PERMANENT_FAILURE_SECONDS = 60.0


class RateLimitCacheStore:
    """Own the synchronized rate-limit cache state."""

    def __init__(self) -> None:
        """Create an empty cache."""
        self.cache_entry: CacheEntry | None = None
        self.cache_lock = threading.Lock()

    def collect(
        self,
        harness_runtime_config: HarnessRuntimeConfig,
        request_rate_limits: Callable[[HarnessRuntimeConfig], ProbeResult],
        now: float,
    ) -> RateLimitsCollection:
        """Return the cached or refreshed collection.

        Returns:
            The cached or refreshed collection.

        """
        with self.cache_lock:
            return self._collect(harness_runtime_config, request_rate_limits, now)

    def _collect(
        self,
        harness_runtime_config: HarnessRuntimeConfig,
        request_rate_limits: Callable[[HarnessRuntimeConfig], ProbeResult],
        now: float,
    ) -> RateLimitsCollection:
        runtime_key = f"{harness_runtime_config.executable}\0{harness_runtime_config.configuration_directory}"
        cached = (
            self.cache_entry if self.cache_entry is not None and self.cache_entry.runtime_key == runtime_key else None
        )
        if cached is not None and cached.expires_at > now:
            return cached.collection
        resolution = resolve_probe(request_rate_limits(harness_runtime_config), cached, now)
        self.cache_entry = CacheEntry(
            runtime_key,
            now + resolution.cache_seconds,
            resolution.collection,
            resolution.last_good,
            resolution.last_good_at,
        )
        return resolution.collection


def resolve_probe(
    probe_result: ProbeResult,
    cache_entry: CacheEntry | None,
    now: float,
) -> ProbeResolution:
    """Resolve one probe into a cache entry.

    Returns:
        The usage collection, retained successful value, and cache duration for the probe outcome.

    """
    usage = usage_normalization.normalize_rate_limits(probe_result.response)
    if usage is not None:
        return ProbeResolution(
            RateLimitsCollection(usage, None),
            usage,
            now,
            CACHE_SECONDS,
        )
    if probe_result.response is not None:
        return ProbeResolution(
            RateLimitsCollection(None, "Codex usage response contains no limit windows"),
            None,
            None,
            PERMANENT_FAILURE_SECONDS,
        )
    if probe_result.failure is not None and probe_result.failure.recoverable:
        return recoverable_resolution(cache_entry, now)
    message = "Codex usage failed" if probe_result.failure is None else probe_result.failure.message
    return ProbeResolution(
        RateLimitsCollection(None, message),
        None,
        None,
        PERMANENT_FAILURE_SECONDS,
    )


def recoverable_resolution(
    cache_entry: CacheEntry | None,
    now: float,
) -> ProbeResolution:
    """Return the retry result, with a recent successful value when available.

    Returns:
        The retry result, with a recent successful value when available.

    """
    last_good = None if cache_entry is None else cache_entry.last_good
    last_good_at = None if cache_entry is None else cache_entry.last_good_at
    if last_good_at is None or now - last_good_at > STALE_SECONDS:
        last_good = None
        last_good_at = None
    return ProbeResolution(
        RateLimitsCollection(last_good, None),
        last_good,
        last_good_at,
        RETRY_SECONDS,
    )
