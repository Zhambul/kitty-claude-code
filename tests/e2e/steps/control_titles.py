# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check automatic session titles."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

if TYPE_CHECKING:
    from sdk import client as sdk_client, state as sdk_state
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import Sessions

TITLE_CHARACTER_LIMIT = 80
MAXIMUM_TITLE_WORD_COUNT = 8


def has_concise_title(snapshot: sdk_state.SessionSnapshot, fallback: str) -> bool | None:
    """Return true when a generated title is concise and safe.

    Returns:
        True when the title meets all concise-title requirements, else None.

    """
    title = snapshot.session_data.session.title
    if not title or title == fallback:
        return None
    if "\n" in title or len(title) > TITLE_CHARACTER_LIMIT:
        return None
    word_count = len(title.split())
    if word_count < 1 or word_count > MAXIMUM_TITLE_WORD_COUNT:
        return None
    if "http" in title.casefold() or "<" in title or ">" in title:
        return None
    return True


@then(parsers.parse("session \"{session_name}\" has a concise title unlike '{fallback}'"))
def session_has_concise_title(
    client: sdk_client.BaqylauClient,
    sessions: Sessions,
    wait_policy: WaitPolicy,
    session_name: str,
    fallback: str,
) -> None:
    """Wait for a concise automatic title."""
    client.sessions.watch(sessions.get(session_name)).wait(
        f"session {session_name!r} to receive a concise automatic title",
        partial(has_concise_title, fallback=fallback),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('the application contains exactly session "{session_name}"'))
def application_contains_exactly_session(
    client: sdk_client.BaqylauClient,
    sessions: Sessions,
    session_name: str,
) -> None:
    """Check the application session list."""
    found = tuple(summary.session.session_id for summary in client.sessions.list().sessions)
    assert found == (sessions.get(session_name).session_id,)
