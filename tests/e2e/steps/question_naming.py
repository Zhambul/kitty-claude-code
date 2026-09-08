# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that name pending questions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from tests.e2e.testkit import selector_attention, selector_turns

if TYPE_CHECKING:
    from tests.e2e.testkit import question_contexts


@when(parsers.parse('I name the pending question in turn "{turn_name}" containing \'{prompt}\' "{question_name}"'))
@when(parsers.parse('I name the pending question in work "{turn_name}" containing \'{prompt}\' "{question_name}"'))
def name_pending_question(
    question_observation_context: question_contexts.QuestionObservationContext,
    turn_name: str,
    prompt: str,
    question_name: str,
) -> None:
    """Name a pending question in one turn."""
    original = question_observation_context.turns.get(turn_name)
    turn = selector_turns.turn(
        question_observation_context.client.sessions.watch(original.session),
        original,
        question_observation_context.wait_policy.turn,
    )
    question_observation_context.turns.replace(turn_name, turn)
    found = selector_attention.question(
        question_observation_context.client.sessions.watch(turn.session),
        turn_reference=turn,
        turn_name=turn_name,
        prompt_contains=prompt,
        timeout=question_observation_context.wait_policy.turn,
    )
    question_observation_context.questions.bind(question_name, found)
