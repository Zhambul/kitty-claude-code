# Copyright (c) 2026 Zhambyl Yermagambet
"""Select stable turn references."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from api.sessiondata.models.entry import MessageBodyResponse
from tests.e2e.testkit import references as refs
from tests.e2e.testkit.selector_common import _one

if TYPE_CHECKING:
    from api.sessiondata.models.entry import EntryResponse
    from sdk.client import SessionWatch
    from sdk.state import SessionSnapshot

USER_MESSAGE_ROLE = "user"
PROMPT_MESSAGE_PHASE = "prompt"


def _matches_turn_prompt(entry: EntryResponse, reference: refs.TurnRef) -> bool:
    if entry.cursor <= reference.cursor_before:
        return False
    if reference.actor_id is not None and entry.actor_id != reference.actor_id:
        return False
    if not isinstance(entry.body, MessageBodyResponse):
        return False
    return (
        entry.body.role == USER_MESSAGE_ROLE
        and entry.body.phase == PROMPT_MESSAGE_PHASE
        and prompt_matches(reference, entry.body.content.text)
    )


def _find_turn(snapshot: SessionSnapshot, reference: refs.TurnRef) -> refs.TurnRef | None:
    prompts = [entry for entry in snapshot.entries if _matches_turn_prompt(entry, reference)]
    prompt = _one(prompts, f"prompt {reference.prompt!r}")
    if prompt is None or not isinstance(prompt.body, MessageBodyResponse):
        return None
    body = prompt.body
    return refs.TurnRef(
        session=reference.session,
        prompt=reference.prompt,
        cursor_before=reference.cursor_before,
        expected_prompt_count=reference.expected_prompt_count,
        actor_id=prompt.actor_id,
        turn_id=prompt.turn_id,
        prompt_cursor=prompt.cursor,
        prompt_message_id=body.message_id,
        completion_after_cursor=reference.completion_after_cursor,
        start_cursor=prompt.cursor,
        attachment_paths=reference.attachment_paths,
        native_attachment_names=reference.native_attachment_names,
    )


def turn(watch: SessionWatch, reference: refs.TurnRef, timeout: float) -> refs.TurnRef:
    """Find the stable identity of a turn.

    Returns:
        The turn reference with its stable identity.

    """
    if (
        reference.actor_id is not None
        and reference.activity_cursor is not None
        and (
            reference.turn_id is not None
            or (reference.prompt_cursor is not None and reference.prompt_message_id is not None)
        )
    ):
        return reference

    return watch.wait(
        f"one prompt for the named turn with text {reference.prompt!r}",
        partial(_find_turn, reference=reference),
        timeout=timeout,
    )


def prompt_matches(reference: refs.TurnRef, delivered: str) -> bool:
    """Check the delivered prompt text and attachment names.

    Returns:
        True if the delivered text matches the turn reference.

    """
    expected = reference.prompt.strip()
    actual = delivered.strip()
    if not reference.attachment_paths and not reference.native_attachment_names:
        return actual == expected
    if any(path not in actual for path in reference.attachment_paths):
        return False
    if any(name not in actual for name in reference.native_attachment_names):
        return False
    return not expected or actual.endswith(expected)


def _find_launched_turn(snapshot: SessionSnapshot) -> refs.TurnRef | None:
    prompts = [
        entry for entry in snapshot.entries if _is_lead_prompt(entry, snapshot.session_data.session.lead_actor_id)
    ]
    prompt = _one(prompts, "first user prompt in the launched session")
    if prompt is None:
        return None
    if prompt.turn_id is None:
        return None
    if not isinstance(prompt.body, MessageBodyResponse):
        return None
    body = prompt.body
    return refs.TurnRef(
        session=snapshot.session_reference,
        prompt=body.content.text,
        cursor_before=0,
        expected_prompt_count=1,
        actor_id=prompt.actor_id,
        turn_id=prompt.turn_id,
        prompt_cursor=prompt.cursor,
        prompt_message_id=body.message_id,
        start_cursor=prompt.cursor,
    )


def _is_lead_prompt(entry: EntryResponse, lead_actor_id: str) -> bool:
    """Return whether an entry is the lead actor prompt.

    Returns:
        Whether an entry is the lead actor prompt.

    """
    if entry.actor_id != lead_actor_id or not isinstance(entry.body, MessageBodyResponse):
        return False
    return entry.body.role == USER_MESSAGE_ROLE and entry.body.phase == PROMPT_MESSAGE_PHASE


def launched_turn(watch: SessionWatch, timeout: float) -> refs.TurnRef:
    """Find the first user turn in a new session.

    The harness owns the prompt text that it delivers. It can add attachment
    paths. Thus, the client reads that text and does not rebuild it.

    Returns:
        The first user turn.

    """
    return watch.wait("one first user prompt in the launched session", _find_launched_turn, timeout=timeout)
