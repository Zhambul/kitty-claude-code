# Copyright (c) 2026 Zhambyl Yermagambet
"""Write session identity and lifecycle facts."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, override

from domain.event_conversation import MessageCreated
from domain.event_session import SessionAccountChanged, SessionFinished, SessionStarted, SessionTitleChanged
from domain.lifecycle import LifecycleState
from domain.session_state import SessionFacts
from engine.sessiondata import session_titles
from engine.sessiondata.contract import AggregateState, SessionDataWriter

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload


class SessionWriter(SessionDataWriter):
    """Write session identity, lifecycle, and title facts."""

    @override
    def write(
        self,
        canonical_event: CanonicalEvent[EventPayload],
        aggregate_state: AggregateState,
    ) -> AggregateState:
        """Write the event into session facts.

        Returns:
            State with session identity, title, account, or lifecycle changes applied.

        """
        event = canonical_event
        if isinstance(event.payload, SessionStarted):
            return _started_session(aggregate_state, event, event.payload)
        session = aggregate_state.session
        if session is None:
            return aggregate_state
        return replace(aggregate_state, session=_changed_session(session, event))


def _started_session(
    aggregate_state: AggregateState,
    canonical_event: CanonicalEvent[EventPayload],
    session_started: SessionStarted,
) -> AggregateState:
    born = _born(canonical_event, session_started)
    if aggregate_state.session is None:
        return replace(aggregate_state, session=born)
    resumed = replace(
        aggregate_state.session,
        state=LifecycleState.RUNNING,
        finished_at=None,
        working_directory=(born.working_directory or aggregate_state.session.working_directory),
    )
    return replace(aggregate_state, session=resumed)


def _changed_session(
    session_facts: SessionFacts,
    canonical_event: CanonicalEvent[EventPayload],
) -> SessionFacts:
    payload = canonical_event.payload
    if isinstance(payload, SessionTitleChanged):
        return session_titles.titled(session_facts, payload)
    if isinstance(payload, SessionAccountChanged):
        return replace(session_facts, account=payload.account)
    if isinstance(payload, SessionFinished):
        return replace(session_facts, state=LifecycleState.FINISHED, finished_at=canonical_event.happened_at)
    if (
        isinstance(payload, MessageCreated)
        and session_titles.is_prompt(payload)
        and session_facts.prompt_title_internal is None
    ):
        return session_titles.prompt_titled(session_facts, payload)
    return session_facts


def _born(canonical_event: CanonicalEvent[EventPayload], session_started: SessionStarted) -> SessionFacts:
    return SessionFacts(
        session_id=canonical_event.session_id,
        harness=canonical_event.harness,
        state=LifecycleState.RUNNING,
        working_directory=session_started.working_directory,
        started_at=canonical_event.happened_at,
        lead_actor_id=canonical_event.actor_id,
        account=session_started.account,
        continued_from=session_started.continued_from,
        automatic_title_internal=session_started.title,
    )
