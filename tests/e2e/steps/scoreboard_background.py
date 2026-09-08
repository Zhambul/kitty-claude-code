# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check session background work."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit import selector_common

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.references import Sessions, Turns


@then(parsers.parse('turn "{turn_name}" has exactly {count:d} backgrounded command'))
def turn_backgrounded_count(
    client: BaqylauClient,
    turns: Turns,
    turn_name: str,
    count: int,
) -> None:
    """Check the background command count of one turn."""
    turn = turns.get(turn_name)
    snapshot = client.sessions.snapshot(turn.session)
    found = [
        shell
        for shell in snapshot.shells()
        if (shell.turn_id == turn.turn_id or selector_common.cursor_is_in_turn(snapshot, turn, shell.started_cursor))
        and (shell.backgrounded or shell.execution == "background")
    ]
    assert len(found) == count, f"turn {turn_name!r} has {len(found)} backgrounded commands"


@then(parsers.parse('session "{name}" has exactly {count:d} historical job'))
def historical_job_count(client: BaqylauClient, sessions: Sessions, name: str, count: int) -> None:
    """Check the completed background job count."""
    snapshot = client.sessions.snapshot(sessions.get(name))
    found = sum(actor.background.background_job_count for actor in snapshot.session_data.actors)
    assert found == count, f"session {name!r} has {found} historical jobs"


@then(parsers.parse('session "{name}" has no running work'))
def no_running_work(client: BaqylauClient, sessions: Sessions, name: str) -> None:
    """Check that a session has no running background shell."""
    snapshot = client.sessions.snapshot(sessions.get(name))
    found = {shell_id for actor in snapshot.session_data.actors for shell_id in actor.background.running_shell_ids}
    assert not found, f"session {name!r} still has running work: {sorted(found)}"
