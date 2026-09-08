# Copyright (c) 2026 Zhambyl Yermagambet
"""Service support for automatic naming tests."""

from __future__ import annotations

import typing

from harness.models import interrupts as interrupt_models, session as session_models
from harness.services import control_contract, controls as control_services
from naming import renamer as naming_renamer, service as naming_service
from tests import fake_terminal

if typing.TYPE_CHECKING:
    from audit.recorder import AuditRecorder
    from repository.contract.session_data import SessionDataRepository
    from repository.contract.sessions import SessionRepository
    from terminal import adapter as terminal_adapter

from tests import (
    automatic_naming_models_one,
    automatic_naming_models_two,
)


def control_service(
    stored_session: session_models.Session,
    automatic_namer: automatic_naming_models_two.RecordingNamer,
    effects: automatic_naming_models_two.Effects,
    title_adapter: automatic_naming_models_two.RecordingTitleAdapter | None = None,
) -> control_services.HarnessControlService:
    """Build the control service for naming tests.

    Returns:
        The service with recording adapters and the supplied session.

    """
    titles = naming_renamer.SessionRenamer(
        typing.cast(
            "terminal_adapter.TerminalAdapter", title_adapter or automatic_naming_models_two.RecordingTitleAdapter(),
        ),
    )
    return control_services.HarnessControlService(
        control_services.ControlServiceDependencies(
            session_repository=typing.cast("SessionRepository", automatic_naming_models_one.Sessions(stored_session)),
            terminal_adapter=typing.cast("terminal_adapter.TerminalAdapter", automatic_naming_models_one.Adapter()),
            terminal_plugin=fake_terminal.FakeTerminal().plugin(),
            session_data_repository=typing.cast(
                "SessionDataRepository", automatic_naming_models_two.ControlReadModel(),
            ),
            audit_recorder=typing.cast("AuditRecorder", automatic_naming_models_one.Audit()),
            interrupt_registry=interrupt_models.InterruptRegistry(),
            control_effect_recorder=typing.cast("control_contract.ControlEffects", effects),
            automatic_session_naming=typing.cast("naming_service.AutomaticSessionNamer", automatic_namer),
            session_renaming=titles,
        ),
    )
