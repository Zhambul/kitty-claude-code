# Copyright (c) 2026 Zhambyl Yermagambet
"""Prepare answers for a complete two-question dialog."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sdk.client import QuestionAnswer
from sdk.state import QuestionState
from tests.e2e.testkit import question_states
from tests.e2e.testkit.references import QuestionRef

if TYPE_CHECKING:
    from tests.e2e.testkit.question_contexts import QuestionInteractionContext

PAIR_PATTERN = r'"([^"\n]+)" with option \'([^\'\n]+)\' and "([^"\n]+)" with option \'([^\'\n]+)\''


@dataclass(frozen=True)
class Pair:
    """Contain two named question answers."""

    first_name: str
    first_answer: str
    second_name: str
    second_answer: str

    def answers_for(self, references: tuple[QuestionRef, ...]) -> dict[str, str]:
        """Return answers by question identity.

        Returns:
            The answers for the two named question references.

        """
        return {
            references[0].question_id: self.first_answer,
            references[1].question_id: self.second_answer,
        }

    def mismatch_message(self, expected_ids: set[str], actual_ids: set[str]) -> str:
        """Describe a difference between named and dialog question identifiers.

        Returns:
            The failure description.

        """
        return (
            f"named questions {self.first_name!r} and {self.second_name!r} differ from dialog: "
            f"named {sorted(expected_ids)!r}; dialog {sorted(actual_ids)!r}"
        )


@dataclass(frozen=True)
class Dialog:
    """Contain one complete dialog and its answers."""

    first: QuestionRef
    state: QuestionState
    answers: dict[str, str]

    def answer_sequence(self) -> tuple[QuestionAnswer, ...]:
        """Build one answer for each question in the dialog.

        Returns:
            The complete dialog answer sequence.

        """
        answers = []
        for prompt in self.state.questions:
            answer = self.answers[prompt.question_id]
            answers.append(QuestionAnswer((answer,), ""))
        return tuple(answers)


def parse_pair(text: str) -> Pair:
    """Parse two named question answers.

    Returns:
        The parsed answer pair.

    Raises:
        AssertionError: If the text is not a valid answer pair.

    """
    matched = re.fullmatch(PAIR_PATTERN, text)
    if matched is None:
        message = f"invalid question answer pair: {text!r}"
        raise AssertionError(message)
    return Pair(*matched.groups())


def prepare(context: QuestionInteractionContext, pair: Pair) -> Dialog:
    """Prepare the complete dialog for its two named answers.

    Returns:
        The dialog state and answers by question identity.

    """
    references = (
        context.questions.get(pair.first_name),
        context.questions.get(pair.second_name),
    )
    first = references[0]
    _assert_one_dialog(references, first)
    state = _complete_state(context, first, references, pair)
    return Dialog(first, state, pair.answers_for(references))


def _assert_one_dialog(references: tuple[QuestionRef, ...], first: QuestionRef) -> None:
    first_key = (first.session, first.attention_id, first.turn_name)
    if any(not _matches_dialog(reference, first_key) for reference in references[1:]):
        message = "named questions do not belong to one dialog"
        raise AssertionError(message)


def _complete_state(
    context: QuestionInteractionContext,
    first: QuestionRef,
    references: tuple[QuestionRef, ...],
    pair: Pair,
) -> QuestionState:
    snapshot = context.client.sessions.snapshot(first.session)
    state, _prompt = question_states.question(snapshot, first)
    expected_ids = {reference.question_id for reference in references}
    actual_ids = {prompt.question_id for prompt in state.questions}
    if expected_ids != actual_ids:
        raise AssertionError(pair.mismatch_message(expected_ids, actual_ids))
    return state


def _matches_dialog(reference: QuestionRef, first_key: tuple[object, object, object]) -> bool:
    return (reference.session, reference.attention_id, reference.turn_name) == first_key
