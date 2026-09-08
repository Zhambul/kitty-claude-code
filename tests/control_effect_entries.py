# Copyright (c) 2026 Zhambyl Yermagambet
"""Control effect entries."""

from __future__ import annotations

from domain import (
    content as domain_content,
    entries as domain_entries,
    entry_attention,
    entry_conversation,
    entry_lifecycle,
    entry_shells,
    ids as domain_ids,
    outcomes,
)
from tests import control_effect_values as control_values


def pending_plan_entry(
    attention_id: domain_ids.AttentionId,
) -> domain_entries.SessionEntry:
    """Build a pending plan with the supplied attention identifier.

    Returns:
        A plan proposal entry for the test session.

    """
    return domain_entries.SessionEntry(
        domain_ids.CanonicalEventId("plan-proposed"),
        control_values.TEST_SESSION_ID,
        control_values.TEST_ACTOR_ID,
        None,
        control_values.TEST_TURN_ID,
        1.0,
        None,
        entry_attention.PlanProposedBody(
            attention_id,
            domain_content.TextContent("do the work"),
        ),
    )


def open_work_entries() -> tuple[domain_entries.SessionEntry, ...]:
    """Build entries for work that a session close must finish.

    Returns:
        An open turn, shell, and assignment for the child actor.

    """
    return (
        domain_entries.SessionEntry(
            domain_ids.CanonicalEventId("turn-started"),
            control_values.TEST_SESSION_ID,
            domain_ids.ActorId(control_values.TEST_CHILD_ACTOR_ID_TEXT),
            domain_ids.ActorId(control_values.TEST_LEAD_ACTOR_ID_TEXT),
            control_values.TEST_TURN_ID,
            1.0,
            None,
            entry_conversation.TurnStartedBody(),
        ),
        domain_entries.SessionEntry(
            domain_ids.CanonicalEventId("shell-started"),
            control_values.TEST_SESSION_ID,
            domain_ids.ActorId(control_values.TEST_CHILD_ACTOR_ID_TEXT),
            domain_ids.ActorId(control_values.TEST_LEAD_ACTOR_ID_TEXT),
            control_values.TEST_TURN_ID,
            control_values.SHELL_ENTRY_TIME,
            None,
            entry_shells.ShellStartedBody(
                domain_ids.ShellId("shell-one"),
                domain_content.TextContent("sleep 30"),
                outcomes.ExecutionMode.FOREGROUND,
            ),
        ),
        domain_entries.SessionEntry(
            domain_ids.CanonicalEventId("assignment-started"),
            control_values.TEST_SESSION_ID,
            domain_ids.ActorId(control_values.TEST_CHILD_ACTOR_ID_TEXT),
            domain_ids.ActorId(control_values.TEST_LEAD_ACTOR_ID_TEXT),
            control_values.TEST_TURN_ID,
            control_values.ASSIGNMENT_ENTRY_TIME,
            None,
            entry_lifecycle.AssignmentStartedBody(
                domain_ids.AssignmentId("assignment-one"),
            ),
        ),
    )
