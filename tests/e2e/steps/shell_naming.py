# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that find and name shell commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from tests.e2e.testkit import selector_shells
from tests.e2e.testkit.shell_naming import bind_shell, refresh_turn

if TYPE_CHECKING:
    from tests.e2e.testkit.action_contexts import ShellObservationContext


@when(parsers.parse('I name the only shell command in turn "{turn_name}" containing \'{command}\' "{name}"'))
@when(parsers.parse('I name the only shell command in work "{turn_name}" containing \'{command}\' "{name}"'))
def name_shell_command(
    shell_observation_context: ShellObservationContext,
    turn_name: str,
    command: str,
    name: str,
) -> None:
    """Name one shell command."""
    bind_shell(shell_observation_context, turn_name, command, name)


@when(parsers.parse('I name the successful shell command in turn "{turn_name}" containing \'{command}\' "{name}"'))
@when(parsers.parse('I name the successful shell command in work "{turn_name}" containing \'{command}\' "{name}"'))
def name_successful_shell_command(
    shell_observation_context: ShellObservationContext,
    turn_name: str,
    command: str,
    name: str,
) -> None:
    """Name one successful shell command."""
    bind_shell(
        shell_observation_context,
        turn_name,
        command,
        name,
        lambda shell_state: shell_state.state == "succeeded",
    )


@when(parsers.parse('I name a successful shell attempt in turn "{turn_name}" containing \'{command}\' "{name}"'))
def name_successful_shell_attempt(
    shell_observation_context: ShellObservationContext,
    turn_name: str,
    command: str,
    name: str,
) -> None:
    """Name the first successful shell attempt."""
    turn = shell_observation_context.turns.get(turn_name)
    found = selector_shells.first_shell_attempt(
        shell_observation_context.client.sessions.watch(turn.session),
        turn_reference=turn,
        command_contains=command,
        predicate=lambda shell_state: shell_state.state == "succeeded",
        timeout=shell_observation_context.wait_policy.feed,
    )
    shell_observation_context.shells.bind(name, found)


@when(
    parsers.parse('I name the only running foreground command in turn "{turn_name}" containing \'{command}\' "{name}"'),
)
@when(
    parsers.parse('I name the only running foreground command in work "{turn_name}" containing \'{command}\' "{name}"'),
)
def name_running_foreground_command(
    shell_observation_context: ShellObservationContext,
    turn_name: str,
    command: str,
    name: str,
) -> None:
    """Name a running foreground shell command."""
    turn = refresh_turn(shell_observation_context, turn_name)
    found = selector_shells.shell(
        shell_observation_context.client.sessions.watch(turn.session),
        selector_shells.ShellCriteria(
            turn_reference=turn,
            command_contains=command,
            predicate=lambda shell_state: (
                shell_state.execution == "foreground" and shell_state.state is None and not shell_state.backgrounded
            ),
        ),
        timeout=shell_observation_context.wait_policy.turn,
    )
    shell_observation_context.shells.bind(name, found)


@when(parsers.parse('I name the only running command in turn "{turn_name}" containing \'{command}\' "{name}"'))
@when(parsers.parse('I name the only running command in work "{turn_name}" containing \'{command}\' "{name}"'))
def name_running_command(
    shell_observation_context: ShellObservationContext,
    turn_name: str,
    command: str,
    name: str,
) -> None:
    """Name a running shell command."""
    turn = refresh_turn(shell_observation_context, turn_name)
    found = selector_shells.shell(
        shell_observation_context.client.sessions.watch(turn.session),
        selector_shells.ShellCriteria(
            turn_reference=turn,
            command_contains=command,
            predicate=lambda shell_state: shell_state.state is None,
        ),
        timeout=shell_observation_context.wait_policy.turn,
    )
    shell_observation_context.shells.bind(name, found)


@when(parsers.parse('I name the only background job in turn "{turn_name}" containing \'{command}\' "{name}"'))
@when(parsers.parse('I name the only background job in work "{turn_name}" containing \'{command}\' "{name}"'))
def name_background_job(
    shell_observation_context: ShellObservationContext,
    turn_name: str,
    command: str,
    name: str,
) -> None:
    """Name one background shell job."""
    bind_shell(
        shell_observation_context,
        turn_name,
        command,
        name,
        lambda shell_state: shell_state.execution == "background" or shell_state.backgrounded,
    )


@when(parsers.parse('I name the only monitor in turn "{turn_name}" containing \'{command}\' "{name}"'))
@when(parsers.parse('I name the only monitor in work "{turn_name}" containing \'{command}\' "{name}"'))
def name_monitor(
    shell_observation_context: ShellObservationContext,
    turn_name: str,
    command: str,
    name: str,
) -> None:
    """Name one monitor shell."""
    bind_shell(
        shell_observation_context,
        turn_name,
        command,
        name,
        lambda shell_state: shell_state.execution == "monitor",
    )
