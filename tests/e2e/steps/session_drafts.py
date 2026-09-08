# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that save and restore session drafts."""

from __future__ import annotations

import time
from http import HTTPStatus
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from sdk.client import BaqylauClient, QuestionAnswer
from tests.e2e.testkit import references as refs, session_contexts

if TYPE_CHECKING:
    from sdk.client import ActionReceipt
    from tests.e2e.testkit.references import Questions, Sessions

E2E_DRAFT_ORIGIN = "e2e"


def _require_acknowledged(receipt: ActionReceipt, action: str) -> None:
    if receipt.status_code != HTTPStatus.OK or receipt.outcome.status not in {"sent", "queued"}:
        message = f"{action} action {receipt.request_id!r} was not accepted: {receipt.outcome}"
        raise AssertionError(message)


@when(parsers.parse("I save composer draft '{text}' for session \"{name}\""))
def save_composer_draft(client: BaqylauClient, sessions: Sessions, name: str, text: str) -> None:
    """Save one composer draft."""
    client.preferences.save_composer_draft(
        sessions[name],
        text=text,
        origin=E2E_DRAFT_ORIGIN,
        sequence=time.time(),
    )


@when(parsers.parse("I save a draft for question \"{name}\" with option '{option}' and free text '{text}'"))
def save_question_draft(
    client: BaqylauClient,
    questions: Questions,
    name: str,
    option: str,
    text: str,
) -> None:
    """Save one question dialog draft."""
    reference = questions.get(name)
    client.preferences.save_question_draft(
        reference.session,
        attention_id=reference.attention_id,
        answers=(QuestionAnswer((option,), text),),
        origin=E2E_DRAFT_ORIGIN,
    )


@then(parsers.parse("composer draft for session \"{name}\" is '{text}'"))
def composer_draft_is_saved(client: BaqylauClient, sessions: Sessions, name: str, text: str) -> None:
    """Verify one composer draft."""
    found = client.preferences.session_state(sessions.get(name)).composer.draft
    assert found is not None
    assert (found.text, found.origin) == (text, E2E_DRAFT_ORIGIN)


@then(parsers.parse("question draft \"{name}\" restores option '{option}' and free text '{text}'"))
def question_draft_is_restored(
    client: BaqylauClient,
    questions: Questions,
    name: str,
    option: str,
    text: str,
) -> None:
    """Verify one question dialog draft."""
    reference = questions.get(name)
    found = client.preferences.session_state(reference.session).dialog.draft
    assert found is not None
    assert (found.attention_id, found.origin) == (reference.attention_id, E2E_DRAFT_ORIGIN)
    assert len(found.answers) == 1
    answer = found.answers[0]
    assert (answer.selected, answer.other) == ((option,), text)


@when(
    parsers.parse(
        'I revise the restored draft in session "{session_name}" as turn "{turn_name}"',
    ),
)
def revise_restored_draft(
    session_continuation_context: session_contexts.SessionContinuationContext,
    session_name: str,
    turn_name: str,
    docstring: str,
) -> None:
    """Revise a restored draft."""
    prompt = docstring.strip()
    source = session_continuation_context.prompts.sessions.get(session_name)
    receipt = session_continuation_context.prompts.client.sessions.send(
        source,
        prompt,
        replace_terminal_draft=True,
    )
    _require_acknowledged(receipt, "draft revision")
    owner = session_continuation_context.prompts.client.sessions.wait_for_prompt_owner(
        source,
        prompt=prompt,
        after_cursor=receipt.cursor_before,
        timeout=session_continuation_context.wait_policy.feed,
    )
    lead = session_continuation_context.prompts.client.sessions.snapshot(owner).lead()
    session_continuation_context.prompts.sessions.replace(session_name, owner)
    session_continuation_context.continuations.bind(
        session_name,
        refs.SessionContinuationRef(before=source, after=owner),
    )
    session_continuation_context.prompts.turns.bind(
        turn_name,
        refs.TurnRef(
            owner,
            prompt,
            receipt.cursor_before,
            max(1, lead.statistics.prompt_count),
            actor_id=lead.actor_id,
        ),
    )
