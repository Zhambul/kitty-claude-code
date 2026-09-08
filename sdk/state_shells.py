# Copyright (c) 2026 Zhambyl Yermagambet
"""Materialize shell state from session entries."""

from __future__ import annotations

from api.sessiondata.models import entry as entry_models
from sdk.state_models import ShellState

SHELL_BODIES = (
    entry_models.ShellStartedBodyResponse,
    entry_models.ShellOutputBodyResponse,
    entry_models.ShellBackgroundedBodyResponse,
    entry_models.ShellFinishedBodyResponse,
)


def shells(
    entries: tuple[entry_models.EntryResponse, ...],
    *,
    actor_id: str | None,
) -> tuple[ShellState, ...]:
    """Return materialized shells, optionally for one actor.

    Returns:
        Materialized shells, optionally for one actor.

    """
    folded: dict[str, ShellState] = {}
    for entry in entries:
        if actor_id is not None and entry.actor_id != actor_id:
            continue
        _fold_entry(folded, entry)
    return tuple(folded.values())


def _fold_entry(folded: dict[str, ShellState], entry: entry_models.EntryResponse) -> None:
    body = entry.body
    if not isinstance(body, SHELL_BODIES):
        return
    if isinstance(body, entry_models.ShellStartedBodyResponse):
        folded[body.shell_id] = ShellState(
            shell_id=body.shell_id,
            actor_id=entry.actor_id,
            turn_id=entry.turn_id,
            command=body.command.text,
            execution=body.execution,
            started_cursor=entry.cursor,
        )
    shell = folded.get(body.shell_id)
    if shell is None:
        return
    shell.entry_ids.append(entry.entry_id)
    _update(shell, body)


def _update(
    shell: ShellState,
    body: entry_models.ShellStartedBodyResponse
    | entry_models.ShellOutputBodyResponse
    | entry_models.ShellBackgroundedBodyResponse
    | entry_models.ShellFinishedBodyResponse,
) -> None:
    if isinstance(body, entry_models.ShellOutputBodyResponse):
        _update_output(shell, body)
    elif isinstance(body, entry_models.ShellBackgroundedBodyResponse):
        shell.backgrounded = True
    elif isinstance(body, entry_models.ShellFinishedBodyResponse):
        _finish(shell, body)


def _update_output(shell: ShellState, body: entry_models.ShellOutputBodyResponse) -> None:
    current = shell.status if body.stream == "status" else shell.output
    next_output = body.content.text
    if body.mode != "replace":
        next_output = current + body.content.text
    if body.stream == "status":
        shell.status = next_output
    else:
        shell.output = next_output


def _finish(shell: ShellState, body: entry_models.ShellFinishedBodyResponse) -> None:
    shell.state = body.state
    shell.exit_code = body.exit_code
    if body.result is not None and body.result.text:
        shell.output = body.result.text
