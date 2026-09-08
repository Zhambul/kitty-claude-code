# Copyright (c) 2026 Zhambyl Yermagambet
"""Select stable shell references."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING

from sdk.state import ShellState
from tests.e2e.testkit import references as refs
from tests.e2e.testkit.selector_common import _one, belongs_to_turn

if TYPE_CHECKING:

    from sdk.client import SessionWatch
    from sdk.state import SessionSnapshot


@dataclass(frozen=True, slots=True)
class ShellCriteria:
    """Specify the shell command to find."""

    command_contains: str
    turn_reference: refs.TurnRef | None = None
    actor_id: str | None = None
    predicate: Callable[[ShellState], bool] | None = None


def _find_shell(snapshot: SessionSnapshot, criteria: ShellCriteria) -> refs.ShellRef | None:
    candidates = [
        shell_state
        for shell_state in snapshot.shells(actor_id=criteria.actor_id)
        if criteria.command_contains in shell_state.command
        and (
            criteria.turn_reference is None
            or belongs_to_turn(
                snapshot,
                criteria.turn_reference,
                turn_id=shell_state.turn_id,
                cursor=shell_state.started_cursor,
            )
        )
        and (criteria.predicate is None or criteria.predicate(shell_state))
    ]
    shell_state = _one(candidates, f"shell command containing {criteria.command_contains!r}")
    if shell_state is None:
        return None
    return refs.ShellRef(
        snapshot.session_reference,
        shell_state.shell_id,
        shell_state.actor_id,
    )


def shell(
    watch: SessionWatch,
    criteria: ShellCriteria,
    *,
    timeout: float,
) -> refs.ShellRef:
    """Find one shell command that meets the criteria.

    Returns:
        The shell command reference.

    """
    return watch.wait(
        f"one shell command containing {criteria.command_contains!r}",
        partial(_find_shell, criteria=criteria),
        timeout=timeout,
    )


def _find_first_shell(
    snapshot: SessionSnapshot,
    turn_reference: refs.TurnRef,
    command_contains: str,
    predicate: Callable[[ShellState], bool],
) -> refs.ShellRef | None:
    candidates = [
        shell_state
        for shell_state in snapshot.shells()
        if command_contains in shell_state.command
        and belongs_to_turn(
            snapshot,
            turn_reference,
            turn_id=shell_state.turn_id,
            cursor=shell_state.started_cursor,
        )
        and predicate(shell_state)
    ]
    if not candidates:
        return None
    shell_state = min(candidates, key=lambda candidate: candidate.started_cursor)
    return refs.ShellRef(
        snapshot.session_reference,
        shell_state.shell_id,
        shell_state.actor_id,
    )


def first_shell_attempt(
    watch: SessionWatch,
    *,
    turn_reference: refs.TurnRef,
    command_contains: str,
    predicate: Callable[[ShellState], bool],
    timeout: float,
) -> refs.ShellRef:
    """Bind the first attempt when a harness retries a command.

    Returns:
        The first shell command reference that meets the criteria.

    """
    return watch.wait(
        f"a shell attempt containing {command_contains!r}",
        partial(
            _find_first_shell,
            turn_reference=turn_reference,
            command_contains=command_contains,
            predicate=predicate,
        ),
        timeout=timeout,
    )
