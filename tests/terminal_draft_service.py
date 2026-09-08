# Copyright (c) 2026 Zhambyl Yermagambet
"""Build the session application service for terminal-draft tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from app import session_application_resources as resources
from dashboard.services.workspace import SessionApplicationService
from harness.services.terminal_gate import SessionTerminalGate
from tests import terminal_draft_support

if TYPE_CHECKING:
    from repository.contract import (
        audit as audit_contract,
        preferences as preference_contract,
        session_data as session_data_contract,
        workspace as workspace_contract,
    )


def service(
    states: terminal_draft_support.TerminalStates,
    workspaces: terminal_draft_support.Workspaces,
    times: list[float],
    read_model: terminal_draft_support.ReadModel | None = None,
) -> SessionApplicationService:
    """Build the session application service.

    Returns:
        The session application service.

    """
    return SessionApplicationService(
        resources.SessionApplicationCore(
            cast("session_data_contract.SessionDataRepository", read_model or terminal_draft_support.ReadModel()),
            states,
            cast("audit_contract.AuditReadRepository", terminal_draft_support.AuditReads()),
            cast("workspace_contract.SessionWorkspaceRepository", workspaces),
            cast("preference_contract.ViewModeRepository", terminal_draft_support.ViewModes()),
        ),
        resources.SessionApplicationRules(
            cast(
                "preference_contract.NotificationSettingRepository",
                terminal_draft_support.NotificationSettings(),
            ),
            cast("preference_contract.TaskDismissalRepository", terminal_draft_support.TaskDismissals()),
            SessionTerminalGate(),
        ),
        clock=lambda: times.pop(0),
    )
