# Copyright (c) 2026 Zhambyl Yermagambet
"""Application replacement actions and durable-state checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from tests.e2e.testkit.references import (
    ApplicationRestartRef,
    ApplicationRestarts,
    Sessions,
    Turns,
)

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.process import ApplicationProcess


@when(parsers.parse('I restart Baqylau as application restart "{name}"'))
def restart_application(
    application_process: ApplicationProcess,
    client: BaqylauClient,
    application_restarts: ApplicationRestarts,
    name: str,
) -> None:
    """Process restart application."""
    before, after = application_process.restart()
    client.application.wait_until_ready()
    application_restarts.bind(name, ApplicationRestartRef(before, after))


@then(parsers.parse('application restart "{name}" replaces the server process'))
def application_restart_replaces_process(
    client: BaqylauClient,
    application_restarts: ApplicationRestarts,
    name: str,
) -> None:
    """Process application restart replaces process."""
    restart = application_restarts.get(name)
    assert restart.after_process_id != restart.before_process_id
    assert client.application.health().process_id == restart.after_process_id


@then(parsers.parse('session "{session_name}" remains live and keeps turn "{turn_name}" after restart'))
def session_remains_live_with_turn(
    client: BaqylauClient,
    sessions: Sessions,
    turns: Turns,
    session_name: str,
    turn_name: str,
) -> None:
    """Process session remains live with turn."""
    session = sessions.get(session_name)
    turn = turns.get(turn_name)
    snapshot = client.sessions.snapshot(session)
    assert snapshot.session_data.live
    assert snapshot.session_data.session.state != "finished"
    assert any(entry.turn_id == turn.turn_id for entry in snapshot.entries)


@then(parsers.parse('session "{session_name}" has no repeated entry identity'))
def session_has_no_repeated_entry_identity(
    client: BaqylauClient,
    sessions: Sessions,
    session_name: str,
) -> None:
    """Process session has no repeated entry identity."""
    entries = client.sessions.snapshot(sessions.get(session_name)).entries
    identities = [entry.entry_id for entry in entries]
    assert len(identities) == len(set(identities))
