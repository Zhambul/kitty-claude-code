# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that name child actor resources."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from tests.e2e.testkit import (
    assignment_states,
    references as refs,
    selector_actors,
    selector_assignments,
    selector_shells,
)

if TYPE_CHECKING:
    from sdk.client import SessionRef
    from tests.e2e.testkit.reference_contexts import ReferenceBindingContext


@when(parsers.parse('I name the only assignment in turn "{turn_name}" "{assignment_name}"'))
def name_assignment(
    assignment_naming_context: ReferenceBindingContext[refs.TurnRef, refs.AssignmentRef],
    turn_name: str,
    assignment_name: str,
) -> None:
    """Name the assignment from one turn."""
    turn = assignment_naming_context.sources.get(turn_name)
    found = selector_assignments.assignment(
        assignment_naming_context.client.sessions.watch(turn.session),
        turn_reference=turn,
        timeout=assignment_naming_context.wait_policy.feed,
    )
    assignment_naming_context.targets.bind(assignment_name, found)


@when(parsers.parse('I name the actor assigned to assignment "{assignment_name}" "{actor_name}"'))
def name_assigned_actor(
    assigned_actor_naming_context: ReferenceBindingContext[refs.AssignmentRef, refs.ActorRef],
    assignment_name: str,
    actor_name: str,
) -> None:
    """Name the child actor assigned to one assignment."""
    assignment = assigned_actor_naming_context.sources.get(assignment_name)
    found = assigned_actor_naming_context.client.sessions.watch(assignment.session).wait(
        f"assignment {assignment_name!r} to identify its actor",
        partial(assignment_states.assigned_actor, reference=assignment),
        timeout=assigned_actor_naming_context.wait_policy.feed,
    )
    assigned_actor_naming_context.targets.bind(actor_name, found)


@when(parsers.parse('I name the subagent in session "{session_name}" with exact name \'{exact_name}\' "{actor_name}"'))
def name_subagent(
    subagent_naming_context: ReferenceBindingContext[SessionRef, refs.ActorRef],
    session_name: str,
    exact_name: str,
    actor_name: str,
) -> None:
    """Name a child actor by its exact name."""
    found = selector_actors.actor(
        subagent_naming_context.client.sessions.watch(subagent_naming_context.sources.get(session_name)),
        exact_name=exact_name,
        timeout=subagent_naming_context.wait_policy.feed,
    )
    subagent_naming_context.targets.bind(actor_name, found)


@when(parsers.parse('I name the only command for actor "{actor_name}" containing \'{command}\' "{shell_name}"'))
def name_actor_command(
    actor_command_naming_context: ReferenceBindingContext[refs.ActorRef, refs.ShellRef],
    actor_name: str,
    command: str,
    shell_name: str,
) -> None:
    """Name a command from one child actor."""
    actor = actor_command_naming_context.sources.get(actor_name)
    found = selector_shells.shell(
        actor_command_naming_context.client.sessions.watch(actor.session),
        selector_shells.ShellCriteria(actor_id=actor.actor_id, command_contains=command),
        timeout=actor_command_naming_context.wait_policy.feed,
    )
    actor_command_naming_context.targets.bind(shell_name, found)


@when(parsers.parse('I name the exact message \'{text}\' sent to worker of work "{work_name}" "{message_name}"'))
def name_message_to_work_worker(
    actor_message_naming_context: ReferenceBindingContext[refs.WorkRef, refs.ActorMessageRef],
    text: str,
    work_name: str,
    message_name: str,
) -> None:
    """Name a message from a lead to a child actor."""
    work = actor_message_naming_context.sources.get(work_name)
    snapshot = actor_message_naming_context.client.sessions.snapshot(work.session)
    actor_message_naming_context.targets.bind(
        message_name,
        selector_actors.actor_message(
            actor_message_naming_context.client.sessions.watch(work.session),
            sender_actor_id=snapshot.lead().actor_id,
            recipient_actor_id=work.worker.actor_id,
            exact_text=text,
            timeout=actor_message_naming_context.wait_policy.feed,
        ),
    )


@when(parsers.parse('I name the exact message \'{text}\' sent by worker of work "{work_name}" "{message_name}"'))
def name_message_from_work_worker(
    actor_message_naming_context: ReferenceBindingContext[refs.WorkRef, refs.ActorMessageRef],
    text: str,
    work_name: str,
    message_name: str,
) -> None:
    """Name a message from a child actor to its lead."""
    work = actor_message_naming_context.sources.get(work_name)
    lead_actor_id = actor_message_naming_context.client.sessions.snapshot(work.session).lead().actor_id
    actor_message_naming_context.targets.bind(
        message_name,
        selector_actors.actor_message(
            actor_message_naming_context.client.sessions.watch(work.session),
            sender_actor_id=work.worker.actor_id,
            recipient_actor_id=lead_actor_id,
            exact_text=text,
            timeout=actor_message_naming_context.wait_policy.feed,
        ),
    )
