# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check work completion and final answers."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit import turns as turn_checks, work_assertions
from tests.e2e.testkit.references import Turns, WorkerControls, WorkRef, Works

if TYPE_CHECKING:
    from sdk.client import BaqylauClient, SessionWatch
    from tests.e2e.testkit.policy import WaitPolicy


def _watch_work(client: BaqylauClient, work: WorkRef) -> SessionWatch:
    """Return the session watch for one work item.

    Returns:
        The session watch.

    """
    return client.sessions.watch(work.session)


@then(parsers.parse('worker control "{name}" request completes'))
def worker_control_request_completes(
    client: BaqylauClient,
    worker_controls: WorkerControls,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Check one worker-control request.

    Raises:
        AssertionError: If the control has no request evidence.

    """
    control = worker_controls.get(name)
    if control.receipt is not None:
        assert control.receipt.status_code in {200, 202}
        assert control.receipt.outcome.status in {"acknowledged", "indeterminate"}
        return
    if control.turn is None:
        message = f"worker control {name!r} has no request evidence"
        raise AssertionError(message)
    current = turn_checks.wait_until_complete(
        client,
        control.turn,
        name=name,
        timeout=wait_policy.turn,
    )
    answers = turn_checks.final_answer_texts(client, current)
    assert answers == ["INTERRUPT_SENT"]


@then(parsers.parse('work "{name}" completes'))
def work_completes(
    client: BaqylauClient,
    works: Works,
    turns: Turns,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Wait until one work item completes."""
    work = works[name]
    if work.assignment is not None:
        _watch_work(client, work).wait(
            f"subagent work {name!r} assignment to complete",
            partial(work_assertions.completed_assignment, work=work, name=name),
            timeout=wait_policy.turn,
        )
        return
    current = turn_checks.wait_until_complete(
        client,
        turns.get(name),
        name=name,
        timeout=wait_policy.turn,
    )
    turns.replace(name, current)
    works.replace(
        name,
        WorkRef(
            work.session,
            work.requested_prompt,
            work.request_turn,
            work.worker,
            current,
            work.assignment,
        ),
    )


@then(parsers.parse("work \"{name}\" has final answer '{text}'"))
def work_has_final_answer(
    client: BaqylauClient,
    works: Works,
    wait_policy: WaitPolicy,
    name: str,
    text: str,
) -> None:
    """Check one work final answer."""
    work = works[name]
    if work.assignment is not None:
        _watch_work(client, work).wait(
            f"subagent work {name!r} to have final answer {text!r}",
            lambda snapshot: (
                True
                if turn_checks.matches_final_answer(
                    work_assertions.assignment_result(snapshot, work),
                    text,
                )
                else None
            ),
            timeout=wait_policy.background,
        )
        return
    answers = turn_checks.final_answer_texts(client, work.turn)
    found = [answer for answer in answers if turn_checks.matches_final_answer(answer, text)]
    assert len(found) == 1, (
        f"work {name!r} has {len(found)} final answers equal to {text!r}; actual final answers: {answers}"
    )


@then(parsers.parse("work \"{name}\" has final answer containing '{text}'"))
def work_has_final_answer_containing(
    client: BaqylauClient,
    works: Works,
    wait_policy: WaitPolicy,
    name: str,
    text: str,
) -> None:
    """Check part of one work final answer."""
    work = works[name]
    if work.assignment is not None:
        _watch_work(client, work).wait(
            f"subagent work {name!r} to have a final answer containing {text!r}",
            lambda snapshot: True if text in work_assertions.assignment_result(snapshot, work) else None,
            timeout=wait_policy.background,
        )
        return
    answers = turn_checks.final_answer_texts(client, work.turn)
    found = [answer for answer in answers if text in answer]
    assert len(found) == 1, (
        f"work {name!r} has {len(found)} final answers containing {text!r}; actual final answers: {answers}"
    )


@then(parsers.parse("work \"{name}\" has first final answer '{text}'"))
def work_has_first_final_answer(
    client: BaqylauClient,
    works: Works,
    name: str,
    text: str,
) -> None:
    """Check the first work final answer."""
    work = works[name]
    answers = turn_checks.final_answer_texts(client, work.turn)
    message = f"work {name!r} first final answer is not {text!r}; actual final answers: {answers}"
    assert answers, message
    assert turn_checks.matches_final_answer(answers[0], text), message
