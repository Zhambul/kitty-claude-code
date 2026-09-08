# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide session application services."""

import time
from collections.abc import Callable

from app import session_application_resources as resources
from dashboard.services import terminal_drafts, workspace_models
from dashboard.services.workspace_operations import (
    SessionDraftOperations,
    SessionPreferenceOperations,
    SessionSnapshotOperations,
)

SessionPreferences = workspace_models.SessionPreferences
SessionApplicationSnapshot = workspace_models.SessionApplicationSnapshot


class SessionApplicationService(SessionPreferenceOperations, SessionDraftOperations, SessionSnapshotOperations):
    """Provide session application read and write operations."""

    def __init__(
        self,
        core: resources.SessionApplicationCore,
        rules: resources.SessionApplicationRules,
        clock: Callable[[], float] | None = None,
    ) -> None:
        """Initialize the object."""
        self.core = core
        self.rules = rules
        self.clock = clock or time.time
        self.terminal_drafts = terminal_drafts.TerminalDraftSync(
            core.terminal_input_service,
            core.workspace_repository,
            rules.terminal_gate,
            self.clock,
        )
