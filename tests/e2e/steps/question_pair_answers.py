# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that answer all questions in one two-question dialog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from tests.e2e.testkit import question_actions, question_dialog

if TYPE_CHECKING:
    from tests.e2e.testkit import question_contexts


@when(
    parsers.re(
        rf'I answer questions (?P<answer_pair>{question_dialog.PAIR_PATTERN}) as control "(?P<control_name>[^"\n]+)"',
    ),
)
def answer_two_questions(
    question_interaction_context: question_contexts.QuestionInteractionContext,
    answer_pair: str,
    control_name: str,
) -> None:
    """Answer two questions in one dialog."""
    pair = question_dialog.parse_pair(answer_pair)
    dialog = question_dialog.prepare(question_interaction_context, pair)
    answers = dialog.answer_sequence()
    question_actions.answer(question_interaction_context, dialog.first, control_name, answers)
