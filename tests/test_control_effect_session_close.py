# Copyright (c) 2026 Zhambyl Yermagambet
"""Test control effect session close."""

from __future__ import annotations

from domain import (
    event_actor,
    event_conversation,
    event_session,
    event_shell,
    ids as domain_ids,
    outcomes,
)
from harness.models import controls as control_models
from tests import (
    control_effect_close_session as close_session,
    control_effect_entries as entries,
    control_effect_recording as recording,
    control_effect_values as control_values,
)


def test_confirmed_close_cancels_each_open_work() -> None:
    """Verify a confirmed close cancels each open work identity."""
    session = close_session.closing_session()
    control_fixture = recording.control_effect_fixture(entries.open_work_entries(), session)

    observations = control_fixture.recorder.work_before_close(session.session_id)
    control_fixture.recorder.session_closed(
        session,
        control_models.CloseSession(session.session_id, domain_ids.RequestId("close-one")),
        observations,
    )

    translated = close_session.translated_control_events(control_fixture.raw_events)
    child_events = translated[1:]
    assert (
        len(control_fixture.raw_events.events),
        [type(canonical_event.payload) for canonical_event in translated],
        translated[0].actor_id,
        {canonical_event.actor_id for canonical_event in child_events},
        {canonical_event.parent_actor_id for canonical_event in child_events},
        {canonical_event.turn_id for canonical_event in child_events},
    ) == (
        4,
        [
            event_session.SessionFinished,
            event_conversation.TurnAborted,
            event_shell.ShellFinished,
            event_actor.ActorAssignmentFinished,
        ],
        domain_ids.ActorId(control_values.TEST_LEAD_ACTOR_ID_TEXT),
        {domain_ids.ActorId(control_values.TEST_CHILD_ACTOR_ID_TEXT)},
        {domain_ids.ActorId(control_values.TEST_LEAD_ACTOR_ID_TEXT)},
        {control_values.TEST_TURN_ID},
    )
    assert isinstance(translated[2].payload, event_shell.ShellFinished)
    assert isinstance(translated[3].payload, event_actor.ActorAssignmentFinished)
    assert (translated[2].payload.outcome, translated[3].payload.outcome) == (
        outcomes.Outcome.CANCELLED,
        outcomes.Outcome.CANCELLED,
    )
