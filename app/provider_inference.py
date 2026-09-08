# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide isolated small-model inference."""

from typing import Annotated

from fastapi import Depends

from app import (
    provider_audit_storage as audit_providers,
    provider_runtime as runtime_providers,
    provider_usage as usage_providers,
)
from app.injection import singleton
from inference import contract, default, options


@singleton
def model_factory(
    terminal: runtime_providers.ModelTerminal,
    usage: usage_providers.UsageState,
    audit: audit_providers.Recorder,
    runtime_configs: runtime_providers.RuntimeConfigs,
) -> contract.ModelFactory:
    """Return the default model factory.

    Returns:
        Default model factory.

    """
    return default.DefaultModelFactory(
        terminal,
        usage,
        audit,
        options.DefaultModelOptions(runtime_configs=runtime_configs),
    )


InferenceModels = Annotated[contract.ModelFactory, Depends(model_factory)]
