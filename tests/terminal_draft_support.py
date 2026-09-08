# Copyright (c) 2026 Zhambyl Yermagambet
"""Fake repositories for terminal-draft tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import (
    composer,
    ids as domain_ids,
    preferences as domain_preferences,
    session_state,
    workspace as workspace_models,
)
from harness.models.probe import TerminalInputState, TerminalSessionState

if TYPE_CHECKING:
    from types import SimpleNamespace

    from audit.records import ApplicationError


class TerminalStates:
    """Represent terminal states."""

    def __init__(self, text: str) -> None:
        """Set terminal text."""
        self.text = text

    def state(self, _session_id: domain_ids.SessionId) -> TerminalSessionState:
        """Return one terminal state.

        Returns:
            The terminal state.

        """
        return TerminalSessionState(
            domain_ids.WindowId("window-one"),
            TerminalInputState(self.text, None),
        )


class Workspaces:
    """Represent workspaces."""

    def __init__(self) -> None:
        """Create the workspace store."""
        self.rows: dict[domain_ids.SessionId, workspace_models.SessionWorkspace] = {}

    def find(self, session_id: domain_ids.SessionId) -> workspace_models.SessionWorkspace | None:
        """Return one workspace.

        Returns:
            The workspace, if it exists.

        """
        return self.rows.get(session_id)

    def save_composer_draft(
        self,
        session_id: domain_ids.SessionId,
        draft: composer.ComposerDraft,
    ) -> bool:
        """Save one composer draft.

        Returns:
            True if the draft is saved.

        """
        current = self.rows.get(session_id)
        if (
            current is not None
            and current.draft is not None
            and draft.sequence < current.draft.sequence
        ):
            return False
        saved_draft = draft if draft.text.strip() else None
        self.rows[session_id] = workspace_models.SessionWorkspace(session_id, saved_draft)
        return True


class ReadModel:
    """Represent read model."""

    def __init__(self) -> None:
        """Create the read model."""
        self.attention: tuple[SimpleNamespace, ...] = ()
        self.session_data: session_state.SessionData | None = None

    def read(self, _session_id: domain_ids.SessionId) -> session_state.SessionData | None:
        """Return session data.

        Returns:
            The session data, if it exists.

        """
        return self.session_data

    def pending_attention(self, _session_id: domain_ids.SessionId) -> tuple[SimpleNamespace, ...]:
        """Return pending attention.

        Returns:
            The pending attention records.

        """
        return self.attention


class AuditReads:
    """Represent audit reads."""

    def __init__(self) -> None:
        """Create the audit reader."""
        self.errors: tuple[ApplicationError, ...] = ()

    def errors_for_session(self, _session_id: domain_ids.SessionId) -> tuple[ApplicationError, ...]:
        """Return audit errors.

        Returns:
            The audit errors.

        """
        return self.errors


class ViewModes:
    """Represent view modes."""

    def __init__(self) -> None:
        """Create the view-mode reader."""
        self.current: domain_preferences.ViewMode | None = None

    def view_mode(self, _session_id: domain_ids.SessionId) -> domain_preferences.ViewMode | None:
        """Return the view mode.

        Returns:
            The view mode, if it exists.

        """
        return self.current


class NotificationSettings:
    """Represent notification settings."""

    def __init__(self) -> None:
        """Create the notification reader."""
        self.muted: frozenset[domain_ids.SessionId] = frozenset()

    def muted_session_ids(self) -> frozenset[domain_ids.SessionId]:
        """Return muted sessions.

        Returns:
            The muted session IDs.

        """
        return self.muted


class TaskDismissals:
    """Represent task dismissals."""

    def __init__(self) -> None:
        """Create the task reader."""
        self.dismissed: frozenset[domain_ids.TaskId] = frozenset()

    def dismissed_task_ids(self, _session_id: domain_ids.SessionId) -> frozenset[domain_ids.TaskId]:
        """Return dismissed tasks.

        Returns:
            The dismissed task IDs.

        """
        return self.dismissed
