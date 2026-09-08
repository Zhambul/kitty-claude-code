# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the complete harness control service."""

from typing import Annotated

from fastapi import Depends

from app import (
    control_resources,
    provider_audit_storage as audit_providers,
    provider_control_support as support_providers,
    provider_harness_sessions as session_providers,
    provider_naming as naming_providers,
    provider_runtime as runtime_providers,
    provider_session_storage as session_data_providers,
    provider_terminal as terminal_providers,
)
from app.injection import singleton
from harness.services import controls as control_service


@singleton
def control_runtime_resources(
    session_storage: session_providers.Sessions,
    adapter: terminal_providers.Terminal,
    plugin: runtime_providers.InstalledTerminal,
    read_model: session_data_providers.SessionDataStore,
    audit: audit_providers.Recorder,
) -> control_resources.ControlRuntimeResources:
    """Return runtime resources for harness controls.

    Returns:
        Runtime resources for harness controls.

    """
    return control_resources.ControlRuntimeResources(
        session_storage,
        adapter,
        plugin,
        read_model,
        audit,
    )


ControlRuntime = Annotated[
    control_resources.ControlRuntimeResources,
    Depends(control_runtime_resources),
]


@singleton
def control_feature_resources(
    interrupts: support_providers.InterruptTracking,
    effects: support_providers.ControlEffects,
    namer: naming_providers.AutomaticNamer,
    titles: terminal_providers.SessionTitles,
    terminal_gate: support_providers.TerminalGate,
) -> control_resources.ControlFeatureResources:
    """Return feature resources for harness controls.

    Returns:
        Feature resources for harness controls.

    """
    return control_resources.ControlFeatureResources(
        interrupts,
        effects,
        namer,
        titles,
        terminal_gate,
    )


ControlFeatures = Annotated[
    control_resources.ControlFeatureResources,
    Depends(control_feature_resources),
]


@singleton
def controls(
    runtime: ControlRuntime,
    features: ControlFeatures,
) -> control_service.HarnessControlService:
    """Return the complete harness control service.

    Returns:
        Complete harness control service.

    """
    return control_service.HarnessControlService(
        control_service.ControlServiceDependencies(
            session_repository=runtime.session_storage,
            terminal_adapter=runtime.terminal_adapter,
            terminal_plugin=runtime.terminal_plugin,
            session_data_repository=runtime.session_data_repository,
            audit_recorder=runtime.audit_recorder,
            interrupt_registry=features.interrupt_registry,
            control_effect_recorder=features.effect_recorder,
            automatic_session_naming=features.automatic_namer,
            session_renaming=features.session_renamer,
        ),
        features.terminal_gate,
    )


Controls = Annotated[control_service.HarnessControlService, Depends(controls)]
