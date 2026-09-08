# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that launch parallel subagent work."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from tests.e2e.steps.work_actions import _bind_work
from tests.e2e.testkit.work_models import WorkRequest

if TYPE_CHECKING:
    from tests.e2e.testkit.work_contexts import WorkLaunchContext


PARALLEL_WORK_COLUMNS = 2


def _parallel_work_requests(datatable: list[list[str]]) -> tuple[WorkRequest, ...]:
    if not datatable or datatable[0] != ["work", "prompt"]:
        message = "parallel work table must have work and prompt columns"
        raise AssertionError(message)
    return tuple(_parallel_work_request(row) for row in datatable[1:])


def _parallel_work_request(row: list[str]) -> WorkRequest:
    """Return one validated parallel-work request.

    Returns:
        The work request.

    Raises:
        AssertionError: If the row has invalid data.

    """
    if len(row) != PARALLEL_WORK_COLUMNS:
        message = "parallel work rows must have work and prompt columns"
        raise AssertionError(message)
    name, prompt = (cell.strip() for cell in row)
    request = WorkRequest(name, prompt)
    if not request.name or not request.prompt:
        message = "parallel work names and prompts must not be empty"
        raise AssertionError(message)
    return request


@when(
    parsers.parse(
        'I launch session "{session_name}" as turn "{turn_name}" and assign these work items in parallel to subagents',
    ),
)
def launch_parallel_work(
    work_launch_context: WorkLaunchContext,
    session_name: str,
    turn_name: str,
    datatable: list[list[str]],
) -> None:
    """Launch parallel work."""
    started = work_launch_context.driver.launch_parallel(
        work_launch_context.session_specs.get(session_name),
        _parallel_work_requests(datatable),
    )
    work_launch_context.sessions.bind(session_name, started.session)
    work_launch_context.turns.bind(turn_name, started.request_turn)
    for work_name, work in started.works:
        _bind_work(work_launch_context.works, work_launch_context.turns, work_name, work)
