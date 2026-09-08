# Copyright (c) 2026 Zhambyl Yermagambet
"""Group dependencies for the harness control service."""

from dataclasses import dataclass

from app import (
    provider_audit_storage as audit_providers,
    provider_control_support as support_providers,
    provider_harness_sessions as session_providers,
    provider_naming as naming_providers,
    provider_runtime as runtime_providers,
    provider_session_storage as session_data_providers,
    provider_terminal as terminal_providers,
)


@dataclass(frozen=True)
class ControlRuntimeResources:
    """Hold session, terminal, and audit control dependencies."""

    session_storage: session_providers.Sessions
    terminal_adapter: terminal_providers.Terminal
    terminal_plugin: runtime_providers.InstalledTerminal
    session_data_repository: session_data_providers.SessionDataStore
    audit_recorder: audit_providers.Recorder


@dataclass(frozen=True)
class ControlFeatureResources:
    """Hold optional control feature dependencies."""

    interrupt_registry: support_providers.InterruptTracking
    effect_recorder: support_providers.ControlEffects
    automatic_namer: naming_providers.AutomaticNamer
    session_renamer: terminal_providers.SessionTitles
    terminal_gate: support_providers.TerminalGate
