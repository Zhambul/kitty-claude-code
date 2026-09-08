# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that apply and check session rewind controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from api.controls.models.control_outcome_response import RewindResultResponse
from api.sessiondata.models.entry import EntryResponse, MessageBodyResponse

if TYPE_CHECKING:
    from tests.e2e.testkit.references import Controls, TurnRef, Turns
    from tests.e2e.testkit.session_contexts import SessionControlContext


def is_new_prompt(entry: EntryResponse, target: TurnRef) -> bool:
    """Return whether an entry is a prompt after the rewind target.

    Returns:
        True when the entry is a later user prompt.

    """
    if target.prompt_cursor is None or entry.cursor <= target.prompt_cursor:
        return False
    if entry.actor_id != target.actor_id or not isinstance(entry.body, MessageBodyResponse):
        return False
    return entry.body.role == "user" and entry.body.phase == "prompt"


@when(
    parsers.parse(
        'I rewind session "{session_name}" to turn "{turn_name}" with {mode} mode as control "{control_name}"',
    ),
)
def apply_rewind(
    session_control_context: SessionControlContext,
    session_name: str,
    turn_name: str,
    mode: str,
    control_name: str,
) -> None:
    """Apply a session rewind.

    Raises:
        AssertionError: If the target does not identify a prompt in the session.

    """
    session = session_control_context.prompts.sessions.get(session_name)
    target = session_control_context.prompts.turns.get(turn_name)
    if target.session != session:
        message = f"turn {turn_name!r} does not belong to session {session_name!r}"
        raise AssertionError(message)
    if target.actor_id is None or target.prompt_cursor is None or target.prompt_message_id is None:
        message = f"turn {turn_name!r} does not have a resolved prompt identity"
        raise AssertionError(message)
    snapshot = session_control_context.prompts.client.sessions.snapshot(session)
    newer_prompt_count = sum(1 for entry in snapshot.entries if is_new_prompt(entry, target))
    session_control_context.controls.bind(
        control_name,
        session_control_context.prompts.client.sessions.apply_rewind(
            session,
            target_message_id=target.prompt_message_id,
            target_text=target.prompt,
            newer_prompt_count=newer_prompt_count,
            mode=mode,
        ),
    )


@then(parsers.parse('control "{control_name}" restores turn "{turn_name}"'))
def control_restores_turn(
    controls: Controls,
    turns: Turns,
    control_name: str,
    turn_name: str,
) -> None:
    """Check a rewind control restored its target turn."""
    outcome = controls.get(control_name).outcome
    assert isinstance(outcome, RewindResultResponse)
    assert outcome.restored_text == turns.get(turn_name).prompt
