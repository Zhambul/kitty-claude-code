# Copyright (c) 2026 Zhambyl Yermagambet
"""Select and bind shells for BDD steps."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.e2e.testkit import selector_shells, selector_turns

if TYPE_CHECKING:
    from collections.abc import Callable

    from sdk.state import ShellState
    from tests.e2e.testkit.action_contexts import ShellObservationContext
    from tests.e2e.testkit.references import TurnRef


def bind_shell(
    context: ShellObservationContext,
    turn_name: str,
    command: str,
    name: str,
    predicate: Callable[[ShellState], bool] | None = None,
) -> None:
    """Find a shell in a turn and bind it to a name."""
    turn = context.turns.get(turn_name)
    found = selector_shells.shell(
        context.client.sessions.watch(turn.session),
        selector_shells.ShellCriteria(turn_reference=turn, command_contains=command, predicate=predicate),
        timeout=context.wait_policy.feed,
    )
    context.shells.bind(name, found)


def refresh_turn(context: ShellObservationContext, turn_name: str) -> TurnRef:
    """Wait for and replace the named turn.

    Returns:
        The refreshed turn reference.

    """
    reference = context.turns.get(turn_name)
    turn = selector_turns.turn(
        context.client.sessions.watch(reference.session),
        reference,
        context.wait_policy.turn,
    )
    context.turns.replace(turn_name, turn)
    return turn
