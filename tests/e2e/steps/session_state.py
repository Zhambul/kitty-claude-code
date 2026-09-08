# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check terminal, liveness, and repository session state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit import resume

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit import policy
    from tests.e2e.testkit.references import SessionContinuations, Sessions


@then(parsers.parse('session "{name}" finishes'))
def session_finishes(client: BaqylauClient, sessions: Sessions, wait_policy: policy.WaitPolicy, name: str) -> None:
    """Wait for a finished session."""
    client.sessions.wait_until_finished(sessions.get(name), wait_policy.cleanup)


@then(parsers.parse('session "{name}" and all its actors finish'))
def session_and_all_actors_finish(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: policy.WaitPolicy,
    name: str,
) -> None:
    """Wait for a session and all its actors to finish."""
    snapshot = client.sessions.wait_until_finished(sessions.get(name), wait_policy.cleanup)
    assert snapshot.session_data.session.state == "finished"
    assert snapshot.session_data.actors
    assert all(actor.state == "finished" for actor in snapshot.session_data.actors)


@then(parsers.parse('session "{name}" is live'))
def session_is_live(client: BaqylauClient, sessions: Sessions, name: str) -> None:
    """Check that a session is live."""
    assert client.sessions.snapshot(sessions.get(name)).session_data.live


@then(parsers.parse('session "{name}" is not live'))
def session_is_not_live(client: BaqylauClient, sessions: Sessions, name: str) -> None:
    """Check that a session is not live."""
    assert not client.sessions.snapshot(sessions.get(name)).session_data.live


@then(parsers.parse('session "{name}" keeps one live terminal after revision'))
def session_keeps_one_live_terminal(
    client: BaqylauClient,
    session_continuations: SessionContinuations,
    name: str,
) -> None:
    """Check that a revised session keeps one live terminal."""
    resume.assert_one_live_session(client, session_continuations.get(name))


@then(parsers.parse('session "{name}" has repository status'))
def session_has_repository_status(client: BaqylauClient, sessions: Sessions, name: str) -> None:
    """Check that a session has repository status."""
    repository = client.sessions.snapshot(sessions.get(name)).session_data.repository
    assert repository is not None
    assert repository.branch


@then(parsers.parse("session \"{name}\" title is not '{title}'"))
def session_title_is_not(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: policy.WaitPolicy,
    name: str,
    title: str,
) -> None:
    """Wait for a session title to change."""
    client.sessions.watch(sessions.get(name)).wait(
        f"session {name!r} title to change from {title!r}",
        lambda snapshot: (
            True if snapshot.session_data.session.title and snapshot.session_data.session.title != title else None
        ),
        timeout=wait_policy.feed,
    )
