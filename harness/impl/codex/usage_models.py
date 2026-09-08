# Copyright (c) 2026 Zhambyl Yermagambet
"""Define Codex usage probe and cache values."""

from __future__ import annotations

from dataclasses import dataclass

from harness.impl.codex.usage_rate_limit_documents import AccountRateLimitsResponse


@dataclass(frozen=True, kw_only=True)
class NormalizedRateLimitWindow:
    """Represent one normalized rate limit window."""

    used_percent: float | int
    duration_minutes: int
    resets_at: float | int | None


@dataclass(frozen=True, kw_only=True)
class NormalizedRateLimits:
    """Represent normalized rate limits."""

    plan: str
    windows: tuple[NormalizedRateLimitWindow, ...]


@dataclass(frozen=True)
class ProbeFailure:
    """Represent one usage probe failure."""

    message: str
    recoverable: bool


@dataclass(frozen=True)
class ProbeResult:
    """Represent one usage probe result."""

    response: AccountRateLimitsResponse | None
    failure: ProbeFailure | None


@dataclass(frozen=True)
class RateLimitsCollection:
    """Represent one rate limits collection."""

    usage: NormalizedRateLimits | None
    error: str | None


@dataclass(frozen=True)
class CacheEntry:
    """Represent one rate limit cache entry."""

    runtime_key: str
    expires_at: float
    collection: RateLimitsCollection
    last_good: NormalizedRateLimits | None
    last_good_at: float | None


@dataclass(frozen=True)
class ProbeResolution:
    """Represent one resolved probe and cache interval."""

    collection: RateLimitsCollection
    last_good: NormalizedRateLimits | None
    last_good_at: float | None
    cache_seconds: float
