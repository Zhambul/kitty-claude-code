# Copyright (c) 2026 Zhambyl Yermagambet
"""Read Codex plan limits through the Codex app server."""

from __future__ import annotations

import os
import time

from domain.ids import HarnessName
from harness.impl.codex import usage_cache, usage_normalization, usage_process
from harness.impl.codex.usage_models import (
    CacheEntry as CacheEntry,
    NormalizedRateLimits as NormalizedRateLimits,
    NormalizedRateLimitWindow as NormalizedRateLimitWindow,
    ProbeFailure as ProbeFailure,
    ProbeResult as ProbeResult,
    RateLimitsCollection as RateLimitsCollection,
)
from harness.runtime import HarnessRuntimeConfig, default_harness_runtime_configs

REQUEST_TIMEOUT_SECONDS = 6.0
RATE_LIMIT_RESPONSE_ID = 2

rate_limit_cache_store = usage_cache.RateLimitCacheStore()


def _default_runtime_config() -> HarnessRuntimeConfig:
    return default_harness_runtime_configs().for_harness(HarnessName.CODEX)


def subprocess_environment(
    harness_runtime_config: HarnessRuntimeConfig,
) -> dict[str, str]:
    """Return the subprocess environment.

    Returns:
        Subprocess environment.

    """
    environment = os.environ.copy()
    environment["CODEX_HOME"] = str(
        harness_runtime_config.configuration_directory,
    )
    return environment


def request_rate_limits(harness_runtime_config: HarnessRuntimeConfig) -> ProbeResult:
    """Return the request rate limits.

    Returns:
        Request rate limits.

    """
    process = usage_process.start(
        harness_runtime_config,
        subprocess_environment(harness_runtime_config),
    )
    if isinstance(process, ProbeResult):
        return process
    with usage_process.ManagedAppServerProcess(process) as managed_process:
        return usage_process.send_rate_limit_request(
            managed_process,
            REQUEST_TIMEOUT_SECONDS,
            RATE_LIMIT_RESPONSE_ID,
        )


normalize_rate_limits = usage_normalization.normalize_rate_limits


def collect_rate_limits(
    harness_runtime_config: HarnessRuntimeConfig | None = None,
) -> RateLimitsCollection:
    """Return fresh limits, or the last good result during a recoverable retry.

    Returns:
        Fresh limits, or the last good result during a recoverable retry.

    """
    runtime_config = harness_runtime_config or _default_runtime_config()
    return rate_limit_cache_store.collect(runtime_config, request_rate_limits, time.time())
