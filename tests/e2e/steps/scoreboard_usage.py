# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check session token use."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit.scoreboard import ScoreWait

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import Sessions


@then(parsers.parse('session "{name}" has positive input token usage'))
def input_usage(
    client: BaqylauClient, sessions: Sessions, wait_policy: WaitPolicy, name: str,
) -> None:
    """Wait for positive input token use."""
    ScoreWait(client, sessions, wait_policy, name).until(
        f"session {name!r} to have positive input token usage",
        lambda snapshot: sum(
            actor.usage.tokens.input_tokens or 0 for actor in snapshot.session_data.actors
        ) > 0,
    )


@then(parsers.parse('session "{name}" has positive output token usage'))
def output_usage(
    client: BaqylauClient, sessions: Sessions, wait_policy: WaitPolicy, name: str,
) -> None:
    """Wait for positive output token use."""
    ScoreWait(client, sessions, wait_policy, name).until(
        f"session {name!r} to have positive output token usage",
        lambda snapshot: sum(
            actor.usage.tokens.output_tokens or 0 for actor in snapshot.session_data.actors
        ) > 0,
    )
