# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check session activity statistics."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit.scoreboard import ScoreWait

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import Sessions


@then(parsers.parse('session "{name}" has added lines'))
def has_added_lines(
    client: BaqylauClient, sessions: Sessions, wait_policy: WaitPolicy, name: str,
) -> None:
    """Wait for at least one added line."""
    ScoreWait(client, sessions, wait_policy, name).until(
        f"session {name!r} to have added lines",
        lambda snapshot: sum(actor.statistics.lines_added for actor in snapshot.session_data.actors) > 0,
    )


@then(parsers.parse('session "{name}" has removed lines'))
def has_removed_lines(
    client: BaqylauClient, sessions: Sessions, wait_policy: WaitPolicy, name: str,
) -> None:
    """Wait for at least one removed line."""
    ScoreWait(client, sessions, wait_policy, name).until(
        f"session {name!r} to have removed lines",
        lambda snapshot: sum(actor.statistics.lines_removed for actor in snapshot.session_data.actors) > 0,
    )


@then(parsers.parse('session "{name}" used tool {tool}'))
def used_tool(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: WaitPolicy,
    name: str,
    tool: str,
) -> None:
    """Wait for a session tool use."""
    ScoreWait(client, sessions, wait_policy, name).until(
        f"session {name!r} to report tool {tool!r}",
        lambda snapshot: any(
            row.tool == tool and row.count > 0
            for actor in snapshot.session_data.actors
            for row in actor.statistics.tool_counts
        ),
    )


@then(parsers.parse('session "{name}" has positive active time'))
def active_time(
    client: BaqylauClient, sessions: Sessions, wait_policy: WaitPolicy, name: str,
) -> None:
    """Wait for positive active time."""
    ScoreWait(client, sessions, wait_policy, name).until(
        f"session {name!r} to have positive active time",
        lambda snapshot: max(actor.statistics.active_seconds for actor in snapshot.session_data.actors) > 0,
    )
