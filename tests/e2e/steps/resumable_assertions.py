# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check resumable-session lists."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit import resumable

if TYPE_CHECKING:
    from tests.e2e.testkit.references import ResumableLists, Sessions


@then(parsers.parse('resumable list "{list_name}" contains session "{session_name}"'))
def resumable_list_contains_session(
    resumable_lists: ResumableLists,
    sessions: Sessions,
    list_name: str,
    session_name: str,
) -> None:
    """Verify a resumable list contains the named session."""
    resumable.session_row(resumable_lists, sessions, list_name, session_name)


@then(parsers.parse('resumable list "{list_name}" contains only session "{session_name}"'))
def resumable_list_contains_only_session(
    resumable_lists: ResumableLists,
    sessions: Sessions,
    list_name: str,
    session_name: str,
) -> None:
    """Verify a resumable list contains only the named session."""
    expected_session_id = sessions.get(session_name).session_id
    actual_session_ids = tuple(row.session_id for row in resumable_lists.get(list_name))
    assert actual_session_ids == (expected_session_id,), (
        f"resumable list {list_name!r} has session IDs {actual_session_ids!r}"
    )


@then(parsers.parse('resumable list "{list_name}" shows session "{session_name}" as {state}'))
def resumable_list_shows_session_state(
    resumable_lists: ResumableLists,
    sessions: Sessions,
    list_name: str,
    session_name: str,
    state: str,
) -> None:
    """Verify a named session has the specified active state.

    Raises:
        AssertionError: If the state name is unknown.

    """
    if state not in {"active", "inactive"}:
        message = f"unknown resumable session state {state!r}"
        raise AssertionError(message)
    row = resumable.session_row(resumable_lists, sessions, list_name, session_name)
    assert row.active is (state == "active")


@then(
    parsers.parse(
        'resumable list "{list_name}" orders session "{newer_session_name}" '
        'before session "{older_session_name}" by newest activity',
    ),
)
def resumable_list_orders_sessions_by_activity(
    resumable_lists: ResumableLists,
    sessions: Sessions,
    list_name: str,
    newer_session_name: str,
    older_session_name: str,
) -> None:
    """Verify resumable sessions are in newest-first order."""
    rows = resumable_lists.get(list_name)
    activity = tuple(row.last_activity_at for row in rows)
    assert activity == tuple(sorted(activity, reverse=True)), (
        f"resumable list {list_name!r} is not in newest-first order"
    )
    newer = resumable.session_row(resumable_lists, sessions, list_name, newer_session_name)
    older = resumable.session_row(resumable_lists, sessions, list_name, older_session_name)
    assert newer.last_activity_at > older.last_activity_at
    assert rows.index(newer) < rows.index(older)
