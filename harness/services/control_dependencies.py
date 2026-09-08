# Copyright (c) 2026 Zhambyl Yermagambet
"""Define the services that control dispatch uses."""

from __future__ import annotations

from dataclasses import dataclass

from audit.recorder import AuditRecorder
from harness.services.control_contract import ControlEffects, InterruptMarker
from harness.services.control_types import AutomaticSessionNaming, SessionFinder, SessionRenaming
from repository.contract.session_data import SessionDataRepository
from terminal.adapter import TerminalAdapter
from terminal.contract import TerminalPlugin


@dataclass(frozen=True)
class ControlServiceDependencies:
    """Contain the stores and services that control dispatch uses."""

    session_repository: SessionFinder
    terminal_adapter: TerminalAdapter
    terminal_plugin: TerminalPlugin
    session_data_repository: SessionDataRepository
    audit_recorder: AuditRecorder
    interrupt_registry: InterruptMarker
    control_effect_recorder: ControlEffects
    automatic_session_naming: AutomaticSessionNaming
    session_renaming: SessionRenaming
