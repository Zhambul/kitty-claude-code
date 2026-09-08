# Copyright (c) 2026 Zhambyl Yermagambet
"""Read question state from session snapshots."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.sessiondata.models.entry import QuestionResponse
    from sdk.state import QuestionState, SessionSnapshot
    from tests.e2e.testkit import references as refs


def question(snapshot: SessionSnapshot, reference: refs.QuestionRef) -> tuple[QuestionState, QuestionResponse]:
    """Return state and prompt for one question reference.

    Returns:
        The dialog state and matching question prompt.

    Raises:
        AssertionError: If the snapshot does not have one matching dialog and prompt.

    """
    states = [state for state in snapshot.questions() if state.attention_id == reference.attention_id]
    if len(states) != 1:
        message = f"question attention {reference.attention_id!r} has {len(states)} matches"
        raise AssertionError(message)
    prompts = [prompt for prompt in states[0].questions if prompt.question_id == reference.question_id]
    if len(prompts) != 1:
        message = f"question {reference.question_id!r} has {len(prompts)} matches"
        raise AssertionError(message)
    return states[0], prompts[0]


def records_labels(
    snapshot: SessionSnapshot,
    reference: refs.QuestionRef,
    expected_labels: frozenset[str],
) -> bool | None:
    """Return true when one question records the required labels.

    Returns:
        True for the required labels, else None.

    """
    state, _prompt = question(snapshot, reference)
    if state.answers is None:
        return None
    answers = [
        answer
        for answer in state.answers
        if answer.question_id == reference.question_id and frozenset(answer.labels) == expected_labels
    ]
    return True if len(answers) == 1 else None


def is_resolved(snapshot: SessionSnapshot, reference: refs.QuestionRef) -> bool | None:
    """Return true when one question dialog is resolved.

    Returns:
        True when the dialog is resolved, else None.

    """
    return None if question(snapshot, reference)[0].pending else True


def choice_label_matches(observed: str, expected: str) -> bool:
    """Return true for an exact label or its recommendation form.

    Returns:
        True when the observed label matches.

    """
    return observed in {expected, f"{expected} (Recommended)"}
