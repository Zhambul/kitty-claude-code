# Copyright (c) 2026 Zhambyl Yermagambet
"""Read and wait for named shell state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.sessiondata.models.entry import ShellFinishedBodyResponse

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from sdk.state import SessionSnapshot, ShellState
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import ShellRef


def shell(snapshot: SessionSnapshot, reference: ShellRef) -> ShellState:
    """Return the shell state for a reference.

    Returns:
        The matching shell state.

    Raises:
        AssertionError: If the snapshot does not have exactly one matching shell.

    """
    found = [shell_state for shell_state in snapshot.shells() if shell_state.shell_id == reference.shell_id]
    if len(found) != 1:
        message = f"shell {reference.shell_id!r} has {len(found)} matches in session {snapshot.session_id!r}"
        raise AssertionError(message)
    return found[0]


def wait_for_output(
    client: BaqylauClient,
    reference: ShellRef,
    wait_policy: WaitPolicy,
    name: str,
    text: str,
) -> None:
    """Wait for shell output to contain text."""
    client.sessions.watch(reference.session).wait(
        f"command {name!r} output to contain {text!r}",
        lambda snapshot: True if text in shell(snapshot, reference).output else None,
        timeout=wait_policy.background,
    )


def finished_cursor(client: BaqylauClient, reference: ShellRef, command_name: str) -> int | None:
    """Return the cursor of one shell completion.

    Returns:
        The completion cursor, or None before a completion arrives.

    Raises:
        AssertionError: If more than one completion exists for the shell.

    """
    snapshot = client.sessions.snapshot(reference.session)
    completions = [
        entry.cursor
        for entry in snapshot.entries
        if entry.actor_id == reference.actor_id
        and isinstance(entry.body, ShellFinishedBodyResponse)
        and entry.body.shell_id == reference.shell_id
    ]
    if len(completions) > 1:
        message = f"command {command_name!r} has {len(completions)} completion facts"
        raise AssertionError(message)
    return completions[0] if completions else None
