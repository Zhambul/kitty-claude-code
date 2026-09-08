# Copyright (c) 2026 Zhambyl Yermagambet
"""Turn resolution and checks shared by turn and work steps."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from api.sessiondata.models.entry import EntryResponse, MessageBodyResponse, TurnFinishedBodyResponse
from tests.e2e.testkit import selector_common, selector_turns

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit.references import TurnRef

MINIMUM_FENCED_ANSWER_LINES = 3


def matches_final_answer(observed: str, expected: str) -> bool:
    """Match a marker with optional code fences, capitalization, or a final period.

    Returns:
        True if the answer matches an accepted form of the marker.

    """
    answer = observed.strip()
    lines = answer.splitlines()
    if (
        len(lines) >= MINIMUM_FENCED_ANSWER_LINES
        and lines[0].startswith("```")
        and lines[0][3:].strip() in {"", "text", "txt"}
        and lines[-1].strip() == "```"
    ):
        answer = "\n".join(lines[1:-1]).strip()
    capitalized = expected.capitalize()
    return answer in {expected, f"{expected}.", capitalized, f"{capitalized}."}


def enders(snapshot: SessionSnapshot, reference: TurnRef) -> list[EntryResponse]:
    """Read final answers within the selected turn's cursor boundaries.

    Returns:
        The final assistant messages that are not addressed to another actor.

    Raises:
        AssertionError: If the turn has no resolved start cursor or actor.

    """
    start_cursor = reference.activity_cursor
    if start_cursor is None:
        message = "turn does not have a resolved start cursor"
        raise AssertionError(message)
    if reference.actor_id is None:
        message = "turn does not have a resolved actor identity"
        raise AssertionError(message)
    answer_after = max(
        start_cursor,
        reference.completion_after_cursor or start_cursor,
    )
    boundaries = [
        cursor
        for cursor in (
            selector_common.next_prompt_cursor(snapshot, reference, after=answer_after),
            _next_completion_cursor(snapshot, reference),
        )
        if cursor is not None
    ]
    boundary = min(boundaries) if boundaries else None
    return [
        entry
        for entry in snapshot.messages(
            actor_id=reference.actor_id,
            role="assistant",
            phase="end_turn",
        )
        if entry.cursor > answer_after
        and (boundary is None or entry.cursor < boundary)
        and isinstance(entry.body, MessageBodyResponse)
        and entry.body.recipient_actor_id is None
    ]


def _next_completion_cursor(
    snapshot: SessionSnapshot,
    reference: TurnRef,
) -> int | None:
    """Find the next completion for the selected actor.

    The next autonomous turn for this actor ends the selected answer window.

    Claude Code can write a Stop hook before the selected turn's final message.
    It can later run a notification turn without a new user prompt. The second
    completion gives a boundary when no new prompt is present.

    Returns:
        The next completion cursor, or None if it cannot be found.

    Raises:
        AssertionError: If the selected turn has multiple completion facts.

    """
    if reference.actor_id is None or reference.turn_id is None:
        return None
    selected_finishes = [
        entry.cursor
        for entry in snapshot.entries
        if entry.actor_id == reference.actor_id
        and entry.turn_id == reference.turn_id
        and isinstance(entry.body, TurnFinishedBodyResponse)
    ]
    if len(selected_finishes) > 1:
        message = f"turn {reference.turn_id!r} has {len(selected_finishes)} completion facts"
        raise AssertionError(
            message,
        )
    if not selected_finishes:
        return None
    selected_finish = selected_finishes[0]
    later = [
        entry.cursor
        for entry in snapshot.entries
        if entry.cursor > selected_finish
        and entry.actor_id == reference.actor_id
        and isinstance(entry.body, TurnFinishedBodyResponse)
    ]
    return min(later) if later else None


def resolved(
    client: BaqylauClient,
    reference: TurnRef,
    *,
    timeout: float,
) -> TurnRef:
    """Wait for the selected turn to have a resolved identity.

    Returns:
        The resolved turn reference.

    """
    return selector_turns.turn(client.sessions.watch(reference.session), reference, timeout)


def _turn_is_complete(
    snapshot: SessionSnapshot,
    reference: TurnRef,
    name: str,
) -> bool | None:
    final_answers = enders(snapshot, reference)
    if reference.actor_id is None:
        message = "turn does not have a resolved actor identity"
        raise AssertionError(message)
    finishes = [
        entry
        for entry in snapshot.entries
        if entry.actor_id == reference.actor_id
        and entry.turn_id == reference.turn_id
        and isinstance(entry.body, TurnFinishedBodyResponse)
    ]
    prompt_count = snapshot.actor(reference.actor_id).statistics.prompt_count
    if len(final_answers) > 1:
        message = f"turn {name!r} has {len(final_answers)} final answers"
        raise AssertionError(message)
    if len(finishes) > 1:
        message = f"turn {name!r} has {len(finishes)} completion facts"
        raise AssertionError(message)
    complete = all(
        (
            len(final_answers) == 1,
            len(finishes) == 1,
            prompt_count >= reference.expected_prompt_count,
        ),
    )
    return True if complete else None


def wait_until_complete(
    client: BaqylauClient,
    reference: TurnRef,
    *,
    name: str,
    timeout: float,
) -> TurnRef:
    """Wait for one final answer, one completion fact, and the expected prompts.

    Returns:
        The resolved reference for the complete turn.

    """
    current = resolved(client, reference, timeout=timeout)

    client.sessions.watch(current.session).wait(
        f"turn {name!r} to have one final answer, prompt, and completion fact",
        partial(_turn_is_complete, reference=current, name=name),
        timeout=timeout,
    )
    return current


def final_answer_texts(client: BaqylauClient, reference: TurnRef) -> list[str]:
    """Read the final answer text for the selected turn.

    Returns:
        The final answer texts with leading and trailing spaces removed.

    """
    return [
        entry.body.content.text.strip()
        for entry in enders(client.sessions.snapshot(reference.session), reference)
        if isinstance(entry.body, MessageBodyResponse)
    ]
