# Copyright (c) 2026 Zhambyl Yermagambet
"""Select stable question and plan references."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from tests.e2e.testkit import references as refs
from tests.e2e.testkit.selector_common import _one, belongs_to_turn

if TYPE_CHECKING:
    from sdk.client import SessionWatch
    from sdk.state import SessionSnapshot


def _find_question(
    snapshot: SessionSnapshot,
    turn_reference: refs.TurnRef,
    turn_name: str,
    prompt_contains: str,
) -> refs.QuestionRef | None:
    candidates = [
        (question_state, question_prompt)
        for question_state in snapshot.questions()
        if question_state.pending
        and belongs_to_turn(
            snapshot,
            turn_reference,
            turn_id=question_state.turn_id,
            cursor=question_state.asked_cursor,
        )
        for question_prompt in question_state.questions
        if prompt_contains in question_prompt.question
    ]
    selected_question = _one(candidates, f"pending question containing {prompt_contains!r}")
    if selected_question is None:
        return None
    return refs.QuestionRef(
        snapshot.session_reference,
        selected_question[0].attention_id,
        selected_question[1].question_id,
        turn_name,
    )


def question(
    watch: SessionWatch,
    *,
    turn_reference: refs.TurnRef,
    turn_name: str,
    prompt_contains: str,
    timeout: float,
) -> refs.QuestionRef:
    """Find one pending question in a turn.

    Returns:
        The question reference.

    """
    return watch.wait(
        f"one pending question containing {prompt_contains!r}",
        partial(
            _find_question,
            turn_reference=turn_reference,
            turn_name=turn_name,
            prompt_contains=prompt_contains,
        ),
        timeout=timeout,
    )


def _find_plan(
    snapshot: SessionSnapshot,
    turn_reference: refs.TurnRef,
    turn_name: str,
    text_contains: str,
) -> refs.PlanRef | None:
    candidates = [
        plan_state
        for plan_state in snapshot.plans()
        if plan_state.pending
        and belongs_to_turn(
            snapshot,
            turn_reference,
            turn_id=plan_state.turn_id,
            cursor=plan_state.proposed_cursor,
        )
        and text_contains in plan_state.text
    ]
    plan_state = _one(candidates, f"pending plan containing {text_contains!r}")
    if plan_state is None:
        return None
    return refs.PlanRef(
        snapshot.session_reference,
        plan_state.attention_id,
        turn_name,
    )


def plan(
    watch: SessionWatch,
    *,
    turn_reference: refs.TurnRef,
    turn_name: str,
    text_contains: str,
    timeout: float,
) -> refs.PlanRef:
    """Find one pending plan in a turn.

    Returns:
        The plan reference.

    """
    return watch.wait(
        f"one pending plan containing {text_contains!r}",
        partial(
            _find_plan,
            turn_reference=turn_reference,
            turn_name=turn_name,
            text_contains=text_contains,
        ),
        timeout=timeout,
    )
