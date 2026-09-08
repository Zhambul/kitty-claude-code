# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that launch and assign question work."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from tests.e2e.testkit import references as refs

if TYPE_CHECKING:
    from tests.e2e.testkit import question_contexts


def _worker_kind(worker_name: str) -> refs.WorkerKind:
    try:
        return refs.WorkerKind(worker_name)
    except ValueError as error:
        message = f"unknown worker type {worker_name!r}"
        raise AssertionError(message) from error


def _bind_question_work(works: refs.Works, turns: refs.Turns, work_name: str, work: refs.WorkRef) -> None:
    works.bind(work_name, work)
    turns.bind(work_name, work.turn)


@when(
    parsers.parse(
        'I launch session "{session_name}" and assign question work "{work_name}" to the {worker_type} with prompt',
    ),
)
def launch_question_work(
    question_work_context: question_contexts.QuestionWorkContext,
    session_name: str,
    work_name: str,
    worker_type: str,
    docstring: str,
) -> None:
    """Launch one question-work session."""
    started = question_work_context.driver.launch(
        question_work_context.session_specs.get(session_name),
        work_name=work_name,
        worker_kind=_worker_kind(worker_type),
        prompt=docstring.strip(),
    )
    question_work_context.sessions.bind(session_name, started.session)
    _bind_question_work(question_work_context.works, question_work_context.turns, work_name, started.work)


@when(
    parsers.parse('I assign question work "{work_name}" in session "{session_name}" to the {worker_type} with prompt'),
)
def assign_question_work(
    question_work_context: question_contexts.QuestionWorkContext,
    session_name: str,
    work_name: str,
    worker_type: str,
    docstring: str,
) -> None:
    """Assign question work in one session."""
    work = question_work_context.driver.assign(
        question_work_context.session_specs.get(session_name),
        question_work_context.sessions.get(session_name),
        work_name=work_name,
        worker_kind=_worker_kind(worker_type),
        prompt=docstring.strip(),
    )
    _bind_question_work(question_work_context.works, question_work_context.turns, work_name, work)
