# Copyright (c) 2026 Zhambyl Yermagambet
"""Selectors for rows in resumable-session lists."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.application.models.resume.resumable_session_response import ResumableSessionResponse
    from tests.e2e.testkit.references import ResumableLists, Sessions


def session_row(
    resumable_lists: ResumableLists,
    sessions: Sessions,
    list_name: str,
    session_name: str,
) -> ResumableSessionResponse:
    """Return the one resumable row for a named session.

    Returns:
        The matching resumable session row.

    """
    session_id = sessions.get(session_name).session_id
    found = [row for row in resumable_lists.get(list_name) if row.session_id == session_id]
    assert len(found) == 1, f"resumable list {list_name!r} has {len(found)} rows for session {session_name!r}"
    return found[0]
