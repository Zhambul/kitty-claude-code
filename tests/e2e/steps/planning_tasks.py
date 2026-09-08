# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that name and check session tasks and goals."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from tests.e2e.testkit import planning_contexts, references as refs, selector_progress, task_states

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.policy import WaitPolicy


@when(parsers.parse('I name the task in session "{session_name}" with subject \'{subject}\' "{task_name}"'))
def name_task(
    task_naming_context: planning_contexts.TaskNamingContext,
    session_name: str,
    subject: str,
    task_name: str,
) -> None:
    """Name one task by its exact subject."""
    found = selector_progress.task(
        task_naming_context.client.sessions.watch(task_naming_context.sessions.get(session_name)),
        exact_subject=subject,
        timeout=task_naming_context.wait_policy.feed,
    )
    task_naming_context.tasks.bind(task_name, found)


@then(parsers.parse('task "{name}" has state {state}'))
def task_has_state(
    client: BaqylauClient,
    tasks: refs.Tasks,
    wait_policy: WaitPolicy,
    name: str,
    state: str,
) -> None:
    """Wait for one task state."""
    reference = tasks.get(name)
    client.sessions.watch(reference.session).wait(
        f"task {name!r} to have state {state!r}",
        lambda snapshot: True if task_states.task(snapshot, reference).state == state else None,
        timeout=wait_policy.feed,
    )


@then(parsers.parse('task "{task_name}" belongs to worker of work "{work_name}"'))
def task_belongs_to_work_worker(
    client: BaqylauClient,
    tasks: refs.Tasks,
    works: refs.Works,
    task_name: str,
    work_name: str,
) -> None:
    """Check that a task belongs to one work child actor."""
    reference = tasks.get(task_name)
    task = task_states.task(client.sessions.snapshot(reference.session), reference)
    assert task.owner_actor_id == works.get(work_name).worker.actor_id


@then(parsers.parse("task \"{name}\" has description '{description}'"))
def task_has_description(
    client: BaqylauClient,
    tasks: refs.Tasks,
    name: str,
    description: str,
) -> None:
    """Check one task description."""
    reference = tasks.get(name)
    assert task_states.task(client.sessions.snapshot(reference.session), reference).description == description


@then(parsers.parse('session "{name}" has exactly {count:d} tasks'))
def session_has_task_count(
    client: BaqylauClient,
    sessions: refs.Sessions,
    wait_policy: WaitPolicy,
    name: str,
    count: int,
) -> None:
    """Wait for the required task count."""
    session = sessions.get(name)
    client.sessions.watch(session).wait(
        f"session {name!r} to have exactly {count} tasks",
        lambda snapshot: True if len(snapshot.session_data.session.tasks) == count else None,
        timeout=wait_policy.feed,
    )
