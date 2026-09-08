# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check shell command results."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from api.sessiondata.models.entry import ShellFinishedBodyResponse
from sdk.client import wait_for
from tests.e2e.testkit import turns as turn_checks
from tests.e2e.testkit.shell_states import finished_cursor, shell, wait_for_output

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.action_contexts import ShellObservationContext
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import Shells, Works


@then(parsers.parse('command "{name}" has state {state}'))
def command_has_state(client: BaqylauClient, shells: Shells, wait_policy: WaitPolicy, name: str, state: str) -> None:
    """Wait for a shell command state."""
    reference = shells.get(name)
    client.sessions.watch(reference.session).wait(
        f"command {name!r} to have state {state!r}",
        lambda snapshot: True if shell(snapshot, reference).state == state else None,
        timeout=wait_policy.feed,
    )


@then(parsers.parse('turn "{turn_name}" produces its final answer after command "{command_name}" finishes'))
def turn_final_answer_is_after_command_finishes(
    shell_observation_context: ShellObservationContext,
    turn_name: str,
    command_name: str,
) -> None:
    """Check that a turn answer follows a shell completion."""
    command = shell_observation_context.shells.get(command_name)
    turn = turn_checks.wait_until_complete(
        shell_observation_context.client,
        shell_observation_context.turns.get(turn_name),
        name=turn_name,
        timeout=shell_observation_context.wait_policy.turn,
    )
    shell_observation_context.turns.replace(turn_name, turn)
    snapshot = shell_observation_context.client.sessions.snapshot(command.session)
    completions = [
        entry
        for entry in snapshot.entries
        if entry.actor_id == command.actor_id
        and isinstance(entry.body, ShellFinishedBodyResponse)
        and entry.body.shell_id == command.shell_id
    ]
    assert len(completions) == 1, f"command {command_name!r} has {len(completions)} completion facts"
    answers = turn_checks.enders(snapshot, turn)
    assert len(answers) == 1, f"turn {turn_name!r} has {len(answers)} final answers"
    assert answers[0].cursor > completions[0].cursor


@then(parsers.parse('command "{command_name}" finishes before message from "{turn_name}" enters the chat'))
def command_finishes_before_message_enters(
    shell_observation_context: ShellObservationContext,
    turn_name: str,
    command_name: str,
) -> None:
    """Check that a command completes before the following prompt.

    Raises:
        AssertionError: If the turn has no prompt cursor.

    """
    turn = turn_checks.resolved(
        shell_observation_context.client,
        shell_observation_context.turns.get(turn_name),
        timeout=shell_observation_context.wait_policy.feed,
    )
    shell_observation_context.turns.replace(turn_name, turn)
    command = shell_observation_context.shells.get(command_name)
    completion = wait_for(
        f"command {command_name!r} to finish",
        partial(finished_cursor, shell_observation_context.client, command, command_name),
        timeout=shell_observation_context.wait_policy.feed,
    )
    if turn.prompt_cursor is None:
        message = f"turn {turn_name!r} has no prompt cursor"
        raise AssertionError(message)
    assert completion < turn.prompt_cursor


@then(parsers.parse("command \"{name}\" has output containing '{text}'"))
def command_has_output(client: BaqylauClient, shells: Shells, wait_policy: WaitPolicy, name: str, text: str) -> None:
    """Wait for shell command output."""
    wait_for_output(client, shells.get(name), wait_policy, name, text)


@then(parsers.parse('command "{name}" has exit code {exit_code:d}'))
def command_has_exit_code(
    client: BaqylauClient, shells: Shells, wait_policy: WaitPolicy, name: str, exit_code: int,
) -> None:
    """Wait for a shell command exit code."""
    reference = shells.get(name)
    client.sessions.watch(reference.session).wait(
        f"command {name!r} to have exit code {exit_code}",
        lambda snapshot: True if shell(snapshot, reference).exit_code == exit_code else None,
        timeout=wait_policy.feed,
    )


@then(parsers.parse('command "{command_name}" belongs to worker of work "{work_name}"'))
def command_belongs_to_work_worker(shells: Shells, works: Works, command_name: str, work_name: str) -> None:
    """Check that a shell command belongs to a work worker."""
    command = shells.get(command_name)
    work = works.get(work_name)
    assert command.session == work.session
    assert command.actor_id == work.worker.actor_id
