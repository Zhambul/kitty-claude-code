# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check turn prompts and final answers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from api.sessiondata.models.entry import MessageBodyResponse
from tests.e2e.testkit import references as refs, turns as turn_checks

if TYPE_CHECKING:
    from api.sessiondata.models.entry import EntryResponse
    from sdk.client import BaqylauClient


def _matches_turn_prompt(entry: EntryResponse, reference: refs.TurnRef, text: str) -> bool:
    if entry.turn_id != reference.turn_id or not isinstance(entry.body, MessageBodyResponse):
        return False
    if entry.body.role != "user" or entry.body.phase != "prompt":
        return False
    return entry.body.content.text.strip() == text


@then(parsers.parse("turn \"{name}\" has prompt '{text}'"))
def turn_has_prompt(client: BaqylauClient, turns: refs.Turns, name: str, text: str) -> None:
    """Check one turn prompt."""
    reference = turns.get(name)
    snapshot = client.sessions.snapshot(reference.session)
    found = [entry for entry in snapshot.entries if _matches_turn_prompt(entry, reference, text)]
    assert len(found) == 1, f"turn {name!r} has {len(found)} matching prompts"


@then(parsers.parse("turn \"{name}\" has final answer '{text}'"))
def turn_has_final_answer(client: BaqylauClient, turns: refs.Turns, name: str, text: str) -> None:
    """Check one final answer."""
    reference = turns.get(name)
    answers = turn_checks.final_answer_texts(client, reference)
    found = [answer for answer in answers if turn_checks.matches_final_answer(answer, text)]
    assert len(found) == 1, (
        f"turn {name!r} has {len(found)} final answers equal to {text!r}; actual final answers: {answers}"
    )


@then(parsers.parse("turn \"{name}\" has one final answer containing '{text}'"))
def turn_has_one_final_answer_containing(
    client: BaqylauClient,
    turns: refs.Turns,
    name: str,
    text: str,
) -> None:
    """Check a final answer part."""
    answers = turn_checks.final_answer_texts(client, turns.get(name))
    message = f"turn {name!r} does not have one final answer containing {text!r}; actual final answers: {answers}"
    assert len(answers) == 1, message
    assert text in answers[0], message
