# Copyright (c) 2026 Zhambyl Yermagambet
"""Map stored session rows to session models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import ids as domain_ids
from harness.models import session as session_models
from repository.model.facts import SessionInsertRow

if TYPE_CHECKING:
    from repository.model.session_data import SessionRow


def session(session_row: SessionRow) -> session_models.Session:
    """Return the session model for a stored session row.

    Returns:
        The session model for a stored session row.

    """
    return session_models.Session(
        session_id=domain_ids.SessionId(session_row.session_id),
        lead_actor_id=domain_ids.ActorId(session_row.lead_actor_id),
        source_reference=session_row.source_reference,
        working_directory=session_row.working_directory,
        terminal_window_id=session_row.terminal_window_id,
        harness_process_id=session_row.harness_process_id,
        project_directory=session_row.project_directory,
    )


def session_insert_row(
    harness: domain_ids.HarnessName,
    session: session_models.Session,
    created_at: float,
) -> SessionInsertRow:
    """Return the storage row for a session model.

    Returns:
        The storage row for a session model.

    """
    return SessionInsertRow(
        session_id=session.session_id,
        lead_actor_id=session.lead_actor_id,
        harness=harness,
        harness_session_id=session.session_id,
        source_reference=session.source_reference,
        working_directory=session.working_directory,
        project_directory=session.project_directory,
        terminal_window_id=session.terminal_window_id,
        harness_process_id=session.harness_process_id,
        created_at=created_at,
    )
