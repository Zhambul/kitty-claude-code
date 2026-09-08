# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide browser values."""

from __future__ import annotations

from tests.e2e.testkit import (
    browser_client_dependencies as client_dependencies,
    browser_model_dependencies as model_dependencies,
    browser_runtime_dependencies as runtime_dependencies,
    browser_standard_dependencies as standard_dependencies,
    browser_terminal_dependencies as terminal_dependencies,
    references as browser_references,
)

browser_expectation = model_dependencies.expect
regular_expressions = standard_dependencies.re


def duration_component(match: regular_expressions.Match[str] | None, multiplier: int) -> int:
    """Return one parsed duration component in seconds.

    Returns:
        One parsed duration component in seconds.

    """
    if match is None:
        return 0
    return int(match.group(1)) * multiplier


def usage_rows_for_harness(
    usage_rows: standard_dependencies.Sequence[model_dependencies.UsageRowResponse], harness: str,
) -> list[model_dependencies.UsageRowResponse]:
    """Return usage rows for one harness.

    Returns:
        Usage rows for one harness.

    """
    return [usage_row for usage_row in usage_rows if usage_row.harness == harness]


def resume_catalog_requests(paths: list[str]) -> tuple[str, ...]:
    """Return requests for the resume catalog.

    Returns:
        Requests for the resume catalog.

    """
    return tuple(path for path in paths if path == "/api/resumable-sessions")


def form_source(
    form: browser_references.BrowserSessionFormRef,
) -> runtime_dependencies.SessionRef:
    """Return the selected source session from a browser form.

    Returns:
        The selected source session from a browser form.

    Raises:
        AssertionError: If the form has no source session.

    """
    if form.source is None:
        msg = "browser session form has no resume source"
        raise AssertionError(msg)
    return form.source


def question(
    snapshot: runtime_dependencies.SessionSnapshot,
    reference: browser_references.QuestionRef,
) -> tuple[runtime_dependencies.QuestionState, runtime_dependencies.QuestionResponse]:
    """Return the question state and prompt for one reference.

    Returns:
        The question state and prompt for one reference.

    Raises:
        AssertionError: If the reference does not match one state and one prompt.

    """
    states = [
        question_state
        for question_state in snapshot.questions()
        if question_state.attention_id == reference.attention_id
    ]
    if len(states) != 1:
        msg = f"question attention {reference.attention_id!r} has {len(states)} matches"
        raise AssertionError(msg)
    prompts = [question for question in states[0].questions if question.question_id == reference.question_id]
    if len(prompts) != 1:
        msg = f"question {reference.question_id!r} has {len(prompts)} matches"
        raise AssertionError(msg)
    return (states[0], prompts[0])


def plan(
    snapshot: runtime_dependencies.SessionSnapshot, reference: browser_references.PlanRef,
) -> runtime_dependencies.PlanState:
    """Return the plan state for one reference.

    Returns:
        The plan state for one reference.

    Raises:
        AssertionError: If the reference does not match exactly one plan.

    """
    states = [plan_state for plan_state in snapshot.plans() if plan_state.attention_id == reference.attention_id]
    if len(states) != 1:
        msg = f"plan attention {reference.attention_id!r} has {len(states)} matches"
        raise AssertionError(msg)
    return states[0]


def assert_status_color(locator: client_dependencies.Locator, status: str) -> None:
    """Verify the status indicator has the expected terminal color."""
    appearance = terminal_dependencies.tab_appearance(runtime_dependencies.ActorStatus(status))
    color = appearance.active_background
    expected_color = f"rgb({color.red}, {color.green}, {color.blue})"
    browser_expectation(locator).to_have_css("background-color", expected_color)
