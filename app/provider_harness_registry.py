# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the installed harness registry."""

from typing import Annotated

from fastapi import Depends

from app import (
    harness_environment,
    provider_audit_storage as audit_providers,
    provider_harness_launch as launch_providers,
    provider_runtime as runtime_providers,
)
from app.injection import singleton
from harness.impl.discovery import installed
from harness.registry import HarnessRegistry


@singleton
def registry(
    runtime_configs: runtime_providers.RuntimeConfigs,
    terminal: runtime_providers.InstalledTerminal,
    effects: launch_providers.LaunchEffects,
    audit: audit_providers.Recorder,
) -> HarnessRegistry:
    """Return the validated registry of installed harnesses.

    Returns:
        Validated registry of installed harnesses.

    """
    harnesses = HarnessRegistry()
    for plugin in installed(
        runtime_configs,
        terminal,
        effects,
        audit,
        harness_environment.launch_environment(),
    ):
        harnesses.register(plugin)
    harnesses.validate()
    return harnesses


Registry = Annotated[HarnessRegistry, Depends(registry)]
