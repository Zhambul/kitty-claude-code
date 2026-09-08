# Copyright (c) 2026 Zhambyl Yermagambet
"""Pure value operations for the browser test-kit."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.sessiondata.models.entry import QuestionResponse
    from sdk.client import SessionRef
    from sdk.state import PlanState, QuestionState, SessionSnapshot
    from tests.e2e.testkit import references as refs

SECONDS_PER_HOUR = 3_600


def duration_seconds(text: str) -> int:
    """Convert the dashboard duration text to seconds.

    Returns:
        The duration in seconds.

    Raises:
        AssertionError: If the text has no duration value.

    """
    duration_parts = re.findall(r"(\d+)([hms])", text)
    if not duration_parts:
        message = f"browser operation time is not readable: {text!r}"
        raise AssertionError(message)
    unit_multipliers = {
        "h": SECONDS_PER_HOUR,
        "m": 60,
        "s": 1,
    }
    return sum(
        int(duration_value) * unit_multipliers[duration_unit] for duration_value, duration_unit in duration_parts
    )


def resume_catalog_requests(paths: list[str]) -> tuple[str, ...]:
    """Return requests for the resumable-session catalog.

    Returns:
        The matching request paths.

    """
    return tuple(path for path in paths if path == "/api/resumable-sessions")


def form_source(form: refs.BrowserSessionFormRef) -> SessionRef:
    """Return the required resume source from a browser form.

    Returns:
        The session source.

    Raises:
        AssertionError: If the form has no source.

    """
    if form.source is None:
        message = "browser session form has no resume source"
        raise AssertionError(message)
    return form.source


def question(
    snapshot: SessionSnapshot,
    reference: refs.QuestionRef,
) -> tuple[QuestionState, QuestionResponse]:
    """Return one named question and its parent state.

    Returns:
        The question state and the selected question.

    Raises:
        AssertionError: If the question is absent or is not unique.

    """
    states = [
        question_state
        for question_state in snapshot.questions()
        if question_state.attention_id == reference.attention_id
    ]
    if len(states) != 1:
        message = f"question attention {reference.attention_id!r} has {len(states)} matches"
        raise AssertionError(message)
    prompts = [
        question_prompt
        for question_prompt in states[0].questions
        if question_prompt.question_id == reference.question_id
    ]
    if len(prompts) != 1:
        message = f"question {reference.question_id!r} has {len(prompts)} matches"
        raise AssertionError(message)
    return states[0], prompts[0]


def plan(snapshot: SessionSnapshot, reference: refs.PlanRef) -> PlanState:
    """Return one named plan state.

    Returns:
        The selected plan state.

    Raises:
        AssertionError: If the plan is absent or is not unique.

    """
    states = [plan_state for plan_state in snapshot.plans() if plan_state.attention_id == reference.attention_id]
    if len(states) != 1:
        message = f"plan attention {reference.attention_id!r} has {len(states)} matches"
        raise AssertionError(message)
    return states[0]


def milliseconds(seconds: float) -> float:
    """Convert seconds to milliseconds.

    Returns:
        The duration in milliseconds.

    """
    return seconds * 1000
