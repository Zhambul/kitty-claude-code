# Copyright (c) 2026 Zhambyl Yermagambet
"""Write the session task list."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, override

from domain.event_work import TaskChanged, TaskListChanged
from domain.session_state import SessionFacts, SessionTask
from engine.sessiondata.contract import AggregateState, SessionDataWriter

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload


class TaskWriter(SessionDataWriter):
    """Write task facts and their ordered membership list."""

    @override
    def write(
        self,
        canonical_event: CanonicalEvent[EventPayload],
        aggregate_state: AggregateState,
    ) -> AggregateState:
        """Write the event into the session task list.

        Returns:
            State with task changes or ordering applied, or unchanged state when the event does not apply.

        """
        payload = canonical_event.payload
        session = aggregate_state.session
        if session is None:
            return aggregate_state
        if isinstance(payload, TaskChanged):
            return replace(aggregate_state, session=_task_changed(session, payload))
        if isinstance(payload, TaskListChanged):
            return replace(
                aggregate_state,
                session=_ordered(replace(session, task_order_internal=payload.task_ids)),
            )
        return aggregate_state


def _task_changed(session_facts: SessionFacts, task_changed: TaskChanged) -> SessionFacts:
    task = SessionTask(
        task_id=task_changed.task_id,
        subject=task_changed.subject,
        description=task_changed.description,
        state=task_changed.state,
        owner_actor_id=task_changed.owner_actor_id,
    )
    known = {existing.task_id: existing for existing in session_facts.tasks}
    known[task.task_id] = task
    order = session_facts.task_order_internal or tuple(known)
    if task.task_id not in order:
        order = (*order, task.task_id)
    return _ordered(replace(session_facts, tasks=tuple(known.values()), task_order_internal=order))


def _ordered(session_facts: SessionFacts) -> SessionFacts:
    """Return the named tasks in their declared order.

    Returns:
        The named tasks in their declared order.

    """
    known = {task.task_id: task for task in session_facts.tasks}
    order = session_facts.task_order_internal or tuple(known)
    return replace(
        session_facts,
        tasks=tuple(known[task_id] for task_id in order if task_id in known),
    )
