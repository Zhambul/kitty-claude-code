# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check messages between lead and child actors."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit import subagent_messages

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import ActorMessages, Works


@then(parsers.parse('actor message "{message_name}" goes from the lead to worker of work "{work_name}"'))
def actor_message_goes_from_lead_to_work_worker(
    client: BaqylauClient,
    works: Works,
    actor_messages: ActorMessages,
    message_name: str,
    work_name: str,
) -> None:
    """Check that a lead sent a message to its child actor."""
    work = works.get(work_name)
    message = actor_messages.get(message_name)
    snapshot = client.sessions.snapshot(work.session)
    assert message.session == work.session
    assert message.sender_actor_id == snapshot.lead().actor_id
    assert message.recipient_actor_id == work.worker.actor_id


@then(parsers.parse("follow-up '{text}' is observed by worker of work \"{work_name}\""))
def followup_is_observed_by_work_worker(
    client: BaqylauClient,
    works: Works,
    wait_policy: WaitPolicy,
    text: str,
    work_name: str,
) -> None:
    """Accept durable evidence that the child actor received a follow-up."""
    work = works.get(work_name)
    lead_actor_id = client.sessions.snapshot(work.session).lead().actor_id
    answer_after = work.turn.activity_cursor or 0
    client.sessions.watch(work.session).wait(
        f"worker of work {work_name!r} to observe follow-up {text!r}",
        partial(
            subagent_messages.followup_was_observed,
            work=work,
            lead_actor_id=lead_actor_id,
            answer_after=answer_after,
            text=text,
        ),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('actor message "{message_name}" goes from worker of work "{work_name}" to the lead'))
def actor_message_goes_from_work_worker_to_lead(
    client: BaqylauClient,
    works: Works,
    actor_messages: ActorMessages,
    message_name: str,
    work_name: str,
) -> None:
    """Check that a child actor sent a message to its lead."""
    work = works.get(work_name)
    message = actor_messages.get(message_name)
    snapshot = client.sessions.snapshot(work.session)
    assert message.session == work.session
    assert message.sender_actor_id == work.worker.actor_id
    assert message.recipient_actor_id == snapshot.lead().actor_id
