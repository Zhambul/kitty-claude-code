# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check messages after question controls."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit.question_followups import FollowupCriteria, has_followup

if TYPE_CHECKING:
    from tests.e2e.testkit import question_contexts, references as refs


@then(parsers.parse('question "{question_name}" is followed by final answer \'{text}\' after control "{control_name}"'))
def question_is_followed_by_final_answer(
    question_interaction_context: question_contexts.QuestionInteractionContext,
    question_name: str,
    text: str,
    control_name: str,
) -> None:
    """Wait for the final answer after one question control."""
    reference = question_interaction_context.questions.get(question_name)
    control = question_interaction_context.controls.get(control_name)
    criteria = FollowupCriteria(control.cursor_before, text, "assistant", "end_turn", f"question {question_name!r}")
    _wait_for_followup(question_interaction_context, reference, criteria, question_interaction_context.wait_policy.turn)


@then(parsers.parse('question "{question_name}" sends chat prompt \'{text}\' after control "{control_name}"'))
def question_sends_chat_prompt(
    question_interaction_context: question_contexts.QuestionInteractionContext,
    question_name: str,
    text: str,
    control_name: str,
) -> None:
    """Wait for the chat prompt after one question control."""
    reference = question_interaction_context.questions.get(question_name)
    control = question_interaction_context.controls.get(control_name)
    criteria = FollowupCriteria(control.cursor_before, text, "user", "prompt", f"question {question_name!r}")
    _wait_for_followup(question_interaction_context, reference, criteria, question_interaction_context.wait_policy.feed)


def _wait_for_followup(
    context: question_contexts.QuestionInteractionContext,
    reference: refs.QuestionRef,
    criteria: FollowupCriteria,
    timeout: float,
) -> None:
    context.client.sessions.watch(reference.session).wait(
        f"{criteria.description} to have follow-up {criteria.text!r}",
        partial(has_followup, reference=reference, criteria=criteria),
        timeout=timeout,
    )
