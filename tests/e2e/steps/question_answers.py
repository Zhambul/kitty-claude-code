# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that answer or dismiss one named question."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from sdk.client import QuestionAnswer
from tests.e2e.testkit import question_actions

if TYPE_CHECKING:
    from tests.e2e.testkit import question_contexts


@when(parsers.parse('I answer question "{question_name}" with option \'{option}\' as control "{control_name}"'))
def answer_question(
    question_interaction_context: question_contexts.QuestionInteractionContext,
    question_name: str,
    option: str,
    control_name: str,
) -> None:
    """Answer one question with one option."""
    reference = question_interaction_context.questions.get(question_name)
    question_actions.answer(question_interaction_context, reference, control_name, (QuestionAnswer((option,), ""),))


@when(parsers.parse('I answer question "{question_name}" with free text \'{answer}\' as control "{control_name}"'))
def answer_question_with_free_text(
    question_interaction_context: question_contexts.QuestionInteractionContext,
    question_name: str,
    answer: str,
    control_name: str,
) -> None:
    """Answer one question with free text."""
    reference = question_interaction_context.questions.get(question_name)
    question_actions.answer(question_interaction_context, reference, control_name, (QuestionAnswer((), answer),))


@when(
    parsers.parse(
        "I answer question \"{question_name}\" with options '{first}' and '{second}' as control \"{control_name}\"",
    ),
)
def answer_question_with_two_options(
    question_interaction_context: question_contexts.QuestionInteractionContext,
    question_name: str,
    first: str,
    second: str,
    control_name: str,
) -> None:
    """Answer one question with two options."""
    reference = question_interaction_context.questions.get(question_name)
    question_actions.answer(
        question_interaction_context,
        reference,
        control_name,
        (QuestionAnswer((first, second), ""),),
    )


@when(
    parsers.parse(
        'I dismiss question "{question_name}" and send chat text \'{discussion}\' as control "{control_name}"',
    ),
)
def discuss_question(
    question_interaction_context: question_contexts.QuestionInteractionContext,
    question_name: str,
    discussion: str,
    control_name: str,
) -> None:
    """Dismiss one question and send discussion text."""
    reference = question_interaction_context.questions.get(question_name)
    question_interaction_context.controls.bind(
        control_name,
        question_interaction_context.client.sessions.discuss_question(
            reference.session,
            attention_id=reference.attention_id,
            discussion=discussion,
        ),
    )
