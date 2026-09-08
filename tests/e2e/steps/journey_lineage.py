# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check and use journey lineage."""

from __future__ import annotations

import time
from http import HTTPStatus
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from tests.e2e.testkit.references import SessionContinuations, SessionJourneys, TurnRef, Turns
from tests.e2e.testkit.resume import assert_saved_metadata

if TYPE_CHECKING:
    from sdk.client import BaqylauClient


@when(parsers.parse('I send the shared draft for journey session "{session_name}" as turn "{turn_name}"'))
def send_journey_shared_draft(
    client: BaqylauClient,
    session_journeys: SessionJourneys,
    turns: Turns,
    session_name: str,
    turn_name: str,
) -> None:
    """Send a dashboard draft through its journey session.

    Raises:
        AssertionError: If no draft exists or the daemon rejects it.

    """
    journey = session_journeys.get(session_name)
    draft = client.preferences.session_state(journey.session).composer.draft
    if draft is None or not draft.text:
        message = f"journey session {session_name!r} has no shared draft"
        raise AssertionError(message)
    lead = client.sessions.snapshot(journey.session).lead()
    client.preferences.save_composer_draft(
        journey.session, text="", origin="e2e-browser", sequence=time.time() * 1000,
    )
    receipt = client.sessions.send(journey.session, draft.text)
    if receipt.status_code != HTTPStatus.OK or receipt.outcome.status not in {"sent", "queued"}:
        message = f"shared draft was not accepted: {receipt.outcome}"
        raise AssertionError(message)
    turns.bind(
        turn_name,
        TurnRef(
            journey.session,
            draft.text,
            receipt.cursor_before,
            lead.statistics.prompt_count + 1,
            actor_id=lead.actor_id,
        ),
    )


@then(parsers.parse('journey session "{new_name}" reuses the terminal from journey session "{old_name}"'))
def journey_session_reuses_terminal(session_journeys: SessionJourneys, new_name: str, old_name: str) -> None:
    """Verify a native new session reuses its terminal."""
    new = session_journeys.get(new_name)
    old = session_journeys.get(old_name)
    assert new.session != old.session
    assert new.window_id == old.window_id


@then(parsers.parse('journey session "{session_name}" uses its exact saved resume metadata'))
def journey_uses_saved_resume_metadata(
    client: BaqylauClient,
    session_continuations: SessionContinuations,
    session_name: str,
) -> None:
    """Verify saved resume metadata."""
    assert_saved_metadata(client, session_continuations.get(session_name))


@then(parsers.parse('journey session "{session_name}" has one live terminal and one logical lineage'))
def journey_has_one_terminal_and_lineage(
    client: BaqylauClient,
    session_journeys: SessionJourneys,
    session_continuations: SessionContinuations,
    session_name: str,
) -> None:
    """Verify one live terminal and its logical lineage."""
    journey = session_journeys.get(session_name)
    continuation = session_continuations.get(session_name)
    current = client.sessions.snapshot(journey.session)
    if continuation.before != continuation.after:
        assert current.session_data.session.continued_from == continuation.before.session_id
    terminal = client.preferences.session_state(journey.session).terminal
    assert terminal.window_id == journey.window_id
    live = [
        summary.session.session_id
        for summary in client.sessions.list().sessions
        if summary.live and summary.session.working_directory == current.session_data.session.working_directory
    ]
    assert live == [journey.session.session_id]
