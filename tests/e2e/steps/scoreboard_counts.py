# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check session prompt, shell, and file counts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit.scoreboard import ScoreWait

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import Sessions


@then(parsers.parse('session "{name}" has at least {count:d} prompts'))
def prompt_count(
    client: BaqylauClient, sessions: Sessions, wait_policy: WaitPolicy, name: str, count: int,
) -> None:
    """Wait for the required prompt count."""
    ScoreWait(client, sessions, wait_policy, name).until(
        f"session {name!r} to have at least {count} prompts",
        lambda snapshot: sum(actor.statistics.prompt_count for actor in snapshot.session_data.actors)
        >= count,
    )


@then(parsers.parse('session "{name}" has at least {count:d} shell commands'))
@then(parsers.parse('session "{name}" has at least {count:d} shell command'))
def shell_count(
    client: BaqylauClient, sessions: Sessions, wait_policy: WaitPolicy, name: str, count: int,
) -> None:
    """Wait for the required shell command count."""
    ScoreWait(client, sessions, wait_policy, name).until(
        f"session {name!r} to have at least {count} shell commands",
        lambda snapshot: sum(
            actor.statistics.shell_command_count for actor in snapshot.session_data.actors
        ) >= count,
    )


@then(parsers.parse('session "{name}" has at least {count:d} failed shell command'))
def failed_shell_count(
    client: BaqylauClient, sessions: Sessions, wait_policy: WaitPolicy, name: str, count: int,
) -> None:
    """Wait for the required failed shell command count."""
    ScoreWait(client, sessions, wait_policy, name).until(
        f"session {name!r} to have at least {count} failed shell command",
        lambda snapshot: sum(
            actor.statistics.failed_shell_command_count for actor in snapshot.session_data.actors
        ) >= count,
    )


@then(parsers.parse('session "{name}" has at least {count:d} file operation'))
def file_count(
    client: BaqylauClient, sessions: Sessions, wait_policy: WaitPolicy, name: str, count: int,
) -> None:
    """Wait for the required file operation count."""
    ScoreWait(client, sessions, wait_policy, name).until(
        f"session {name!r} to have at least {count} file operation",
        lambda snapshot: sum(actor.statistics.file_count for actor in snapshot.session_data.actors)
        >= count,
    )
