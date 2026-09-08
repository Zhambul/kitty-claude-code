# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that wait for recorded question answers."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit import question_states

if TYPE_CHECKING:
    from tests.e2e.testkit import question_contexts


@then(parsers.parse("question \"{name}\" records option '{option}'"))
def question_records_option(
    question_observation_context: question_contexts.QuestionObservationContext,
    name: str,
    option: str,
) -> None:
    """Wait for one recorded option."""
    _wait_for_labels(question_observation_context, name, frozenset((option,)))


@then(parsers.parse("question \"{name}\" records free text '{answer}'"))
def question_records_free_text(
    question_observation_context: question_contexts.QuestionObservationContext,
    name: str,
    answer: str,
) -> None:
    """Wait for one recorded free-text answer."""
    _wait_for_labels(question_observation_context, name, frozenset((answer,)))


@then(parsers.parse("question \"{name}\" records options '{first}' and '{second}'"))
def question_records_two_options(
    question_observation_context: question_contexts.QuestionObservationContext,
    name: str,
    first: str,
    second: str,
) -> None:
    """Wait for two recorded options."""
    _wait_for_labels(question_observation_context, name, frozenset((first, second)))


def _wait_for_labels(
    context: question_contexts.QuestionObservationContext,
    name: str,
    labels: frozenset[str],
) -> None:
    reference = context.questions.get(name)
    context.client.sessions.watch(reference.session).wait(
        f"question {name!r} to record labels {sorted(labels)!r}",
        partial(question_states.records_labels, reference=reference, expected_labels=labels),
        timeout=context.wait_policy.feed,
    )
