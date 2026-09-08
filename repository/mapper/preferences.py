# Copyright (c) 2026 Zhambyl Yermagambet
"""Row DTOs to preference values.

With real columns and CHECK constraints there is almost nothing here: the nine
hand-written validators these replace existed only because the values arrived as
free-form JSON and every reader had to prove its own shape.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.ids import HarnessName, SessionId
from domain.preferences import (
    HiddenDirectory,
    NewSessionDraft,
    NewSessionPreferences,
    ViewMode,
)

if TYPE_CHECKING:
    from repository.model.preferences import (
        HiddenDirectoryRow,
        NewSessionDraftRow,
        NewSessionPreferenceRow,
        SessionViewModeRow,
    )


def view_mode(session_view_mode_row: SessionViewModeRow) -> ViewMode:
    # The column carries a CHECK against the same three words, so the store
    # cannot hold a fourth.
    """Return the view mode.

    Returns:
        View mode.

    """
    mode: ViewMode = session_view_mode_row.view_mode  # type: ignore[assignment]
    return mode


def hidden_directory(hidden_directory_row: HiddenDirectoryRow) -> HiddenDirectory:
    """Return the hidden directory.

    Returns:
        Hidden directory.

    """
    return HiddenDirectory(hidden_directory_row.working_directory, hidden_directory_row.hidden_at)


def new_session_preferences(
    new_session_preference_row: NewSessionPreferenceRow,
) -> NewSessionPreferences:
    """Return the new session preferences.

    Returns:
        New session preferences.

    """
    return NewSessionPreferences(
        working_directory=new_session_preference_row.working_directory or None,
        harness=(HarnessName(new_session_preference_row.harness) if new_session_preference_row.harness else None),
        model=new_session_preference_row.model or None,
        effort=new_session_preference_row.effort or None,
    )


def new_session_draft(new_session_draft_row: NewSessionDraftRow) -> NewSessionDraft:
    """Return the new session draft.

    Returns:
        New session draft.

    """
    return NewSessionDraft(
        new_session_draft_row.working_directory,
        new_session_draft_row.text,
        new_session_draft_row.sequence,
    )


def session_id(session_id_text: str) -> SessionId:
    """Return the session ID.

    Returns:
        Session ID.

    """
    return SessionId(session_id_text)
