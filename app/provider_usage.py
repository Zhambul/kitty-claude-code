# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide cross-harness usage state."""

from typing import Annotated

from fastapi import Depends

from app import provider_harness_registry as registry_providers, provider_notifications as notification_providers
from app.injection import singleton
from harness.services import usage


@singleton
def usage_state(
    harnesses: registry_providers.Registry,
    updates: notification_providers.ApplicationUpdates,
) -> usage.ApplicationUsageState:
    """Return shared cross-harness usage state.

    Returns:
        Shared cross-harness usage state.

    """
    return usage.ApplicationUsageState.configured(
        usage.HarnessUsageService(harnesses),
        updates.publish,
    )


UsageState = Annotated[usage.ApplicationUsageState, Depends(usage_state)]
