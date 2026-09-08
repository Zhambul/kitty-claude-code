# Copyright (c) 2026 Zhambyl Yermagambet
"""Send question answers and update their named turn."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sdk.client import QuestionAnswer
    from tests.e2e.testkit.question_contexts import QuestionInteractionContext
    from tests.e2e.testkit.references import QuestionRef


def answer(
    context: QuestionInteractionContext,
    reference: QuestionRef,
    control_name: str,
    answers: tuple[QuestionAnswer, ...],
) -> None:
    """Send answers and update the question turn."""
    receipt = context.controls.bind(
        control_name,
        context.client.sessions.answer_question(
            reference.session,
            attention_id=reference.attention_id,
            answers=answers,
        ),
    )
    turn = context.turns.get(reference.turn_name)
    context.turns.replace(reference.turn_name, turn.resumed_after(receipt.cursor_before))
