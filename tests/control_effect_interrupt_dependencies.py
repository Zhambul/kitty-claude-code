# Copyright (c) 2026 Zhambyl Yermagambet
"""Build control service dependencies for interrupt tests."""

from types import SimpleNamespace as SimpleNamespace
from typing import TYPE_CHECKING as TYPE_CHECKING, cast as cast

from harness.models.interrupts import InterruptRegistry as InterruptRegistry
from harness.services import control_effects, controls as _control_services
from repository.contract import session_data, sessions

control_services = _control_services


ControlEffectRecorder = control_effects.ControlEffectRecorder
SessionDataRepository = session_data.SessionDataRepository
SessionRepository = sessions.SessionRepository


if TYPE_CHECKING:
    from audit.recorder import AuditRecorder
    from terminal.adapter import TerminalAdapter
    from terminal.contract import TerminalPlugin


def interrupt_dependencies() -> control_services.ControlServiceDependencies:
    """Build empty dependencies for the interrupt coordination test.

    Returns:
        Empty dependencies for the interrupt coordination test.

    """
    return control_services.ControlServiceDependencies(
        session_repository=cast("SessionRepository", SimpleNamespace()),
        terminal_adapter=cast("TerminalAdapter", SimpleNamespace()),
        terminal_plugin=cast("TerminalPlugin", SimpleNamespace()),
        session_data_repository=cast("SessionDataRepository", SimpleNamespace()),
        audit_recorder=cast("AuditRecorder", SimpleNamespace()),
        interrupt_registry=InterruptRegistry(),
        control_effect_recorder=cast("ControlEffectRecorder", SimpleNamespace()),
        automatic_session_naming=cast("control_services.AutomaticSessionNaming", SimpleNamespace()),
        session_renaming=cast("control_services.SessionRenaming", SimpleNamespace()),
    )
