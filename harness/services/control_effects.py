# Copyright (c) 2026 Zhambyl Yermagambet
"""Record confirmed control effects as raw observations."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from domain import entries, ids, outcomes, work_state
from harness.models.control_observations import (
    EffortSelectionObservation,
    MessageQueueObservation,
    ModelSelectionObservation,
    PlanDecisionObservation,
    SessionRenameObservation,
)
from harness.models.controls import (
    CloseSession,
    DecidePlan,
    RenameSession,
    SelectEffort,
    SelectModel,
    SendText,
)
from harness.models.raw_events import CONTROL_SOURCE_TYPE, RawEvent
from harness.services import control_contract, open_session_work, session_close_events
from repository.mapper.documents import encode_document

if TYPE_CHECKING:
    from harness.models.session import Session
    from repository.contract import facts, session_data

JSON_ENCODING = "json"


def _message_text(send_text: SendText) -> str:
    attachments = " ".join(attachment.local_path for attachment in send_text.attachments)
    separator = "\n" if attachments and send_text.text else ""
    text = attachments + separator
    return (text + send_text.text).strip()


class ControlEffectRecorder(control_contract.ControlEffects):
    """Make confirmed control effects durable for the interpreter."""

    def __init__(
        self,
        raw_event_repository: facts.RawEventRepository,
        session_data_repository: session_data.SessionDataRepository,
    ) -> None:
        """Initialize the object."""
        self.raw_events = raw_event_repository
        self.session_data = session_data_repository

    def message_queued(self, session: Session, send_text: SendText) -> None:
        """Record a queue acceptance that the harness confirmed.

        Raises:
            ValueError: If an input value is not valid.

        """
        if session.plugin is None:
            message = f"session has no attached harness plugin: {session.session_id}"
            raise ValueError(message)
        text = _message_text(send_text)
        if not text:
            return
        harness = session.plugin.harness_info.name
        identity = f"{harness}:control:{send_text.session_id}:{send_text.request_id}:message_queued"
        self.raw_events.record(
            (
                RawEvent(
                    raw_event_id=ids.RawEventId(identity),
                    harness=harness,
                    source_type=CONTROL_SOURCE_TYPE,
                    source_name="message_queued",
                    source_position=str(send_text.request_id),
                    session_id=send_text.session_id,
                    actor_id=session.lead_actor_id,
                    parent_actor_id=None,
                    observed_at=time.time(),
                    encoding=JSON_ENCODING,
                    payload=encode_document(MessageQueueObservation(send_text.request_id, text)),
                    source_identity=f"{harness}:control:{send_text.session_id}",
                ),
            ),
        )

    def plan_decided(
        self,
        session: Session,
        decide_plan: DecidePlan,
        pending_session_entry: entries.SessionEntry,
    ) -> None:
        """Return the plan decided.

        Raises:
            ValueError: If an input value is not valid.

        """
        if session.plugin is None:
            message = f"session has no attached harness plugin: {session.session_id}"
            raise ValueError(message)
        state = outcomes.PlanState.CHANGES_REQUESTED
        if decide_plan.feedback is None:
            state = outcomes.PlanState.APPROVED
        if decide_plan.decision == "dismiss":
            state = outcomes.PlanState.REJECTED
        observed_at = time.time()
        identity_parts = (
            str(session.plugin.harness_info.name),
            "control",
            str(decide_plan.session_id),
            str(decide_plan.request_id),
        )
        identity = ":".join(identity_parts)
        self.raw_events.record(
            (
                RawEvent(
                    raw_event_id=ids.RawEventId(identity),
                    harness=session.plugin.harness_info.name,
                    source_type=CONTROL_SOURCE_TYPE,
                    source_name="plan_decision",
                    source_position=str(decide_plan.request_id),
                    session_id=decide_plan.session_id,
                    actor_id=pending_session_entry.actor_id,
                    parent_actor_id=pending_session_entry.parent_actor_id,
                    observed_at=observed_at,
                    encoding=JSON_ENCODING,
                    payload=encode_document(
                        PlanDecisionObservation(
                            attention_id=decide_plan.attention_id,
                            state=state,
                            feedback=decide_plan.feedback,
                            edited=False,
                            turn_id=pending_session_entry.turn_id,
                        ),
                    ),
                    source_identity=":".join(identity_parts[:-1]),
                ),
            ),
        )

    def session_renamed(
        self,
        session: Session,
        rename_session: RenameSession,
    ) -> None:
        """Record a title that was written directly with no live source poll.

        Raises:
            ValueError: If an input value is not valid.

        """
        if session.plugin is None:
            message = f"session has no attached harness plugin: {session.session_id}"
            raise ValueError(message)
        harness = session.plugin.harness_info.name
        identity = f"{harness}:control:{rename_session.session_id}:{rename_session.request_id}:session_rename"
        self.raw_events.record(
            (
                RawEvent(
                    raw_event_id=ids.RawEventId(identity),
                    harness=harness,
                    source_type=CONTROL_SOURCE_TYPE,
                    source_name="session_rename",
                    source_position=str(rename_session.request_id),
                    session_id=rename_session.session_id,
                    actor_id=session.lead_actor_id,
                    parent_actor_id=None,
                    observed_at=time.time(),
                    encoding=JSON_ENCODING,
                    payload=encode_document(
                        SessionRenameObservation(
                            rename_session.name,
                            work_state.TitleOrigin.CUSTOM,
                        ),
                    ),
                    source_identity=f"{harness}:control:{rename_session.session_id}",
                ),
            ),
        )

    def selection_changed(
        self,
        session: Session,
        selection: SelectModel | SelectEffort,
    ) -> None:
        """Record a confirmed TUI selection even when the client omits a slash record.

        Raises:
            ValueError: If an input value is not valid.

        """
        if session.plugin is None:
            message = f"session has no attached harness plugin: {session.session_id}"
            raise ValueError(message)
        harness = session.plugin.harness_info.name
        if isinstance(selection, SelectModel):
            source_name = "model_selection"
            payload = encode_document(ModelSelectionObservation(selection.model))
        else:
            source_name = "effort_selection"
            payload = encode_document(EffortSelectionObservation(selection.effort))
        identity = f"{harness}:control:{selection.session_id}:{selection.request_id}:{source_name}"
        self.raw_events.record(
            (
                RawEvent(
                    raw_event_id=ids.RawEventId(identity),
                    harness=harness,
                    source_type=CONTROL_SOURCE_TYPE,
                    source_name=source_name,
                    source_position=str(selection.request_id),
                    session_id=selection.session_id,
                    actor_id=session.lead_actor_id,
                    parent_actor_id=None,
                    observed_at=time.time(),
                    encoding=JSON_ENCODING,
                    payload=payload,
                    source_identity=f"{harness}:control:{selection.session_id}",
                ),
            ),
        )

    def work_before_close(
        self,
        session_id: ids.SessionId,
    ) -> tuple[open_session_work.SessionCloseWork, ...]:
        """Read the open work before the terminal can end or change it.

        Returns:
            Result items.

        """
        session_entries = self.session_data.entries_of_types(
            session_id,
            (
                entries.EntryTypeName.TURN_STARTED,
                entries.EntryTypeName.TURN_FINISHED,
                entries.EntryTypeName.SHELL_STARTED,
                entries.EntryTypeName.SHELL_FINISHED,
                entries.EntryTypeName.ASSIGNMENT_STARTED,
                entries.EntryTypeName.ASSIGNMENT_FINISHED,
            ),
        )
        return open_session_work.open_work(session_entries)

    def session_closed(
        self,
        session: Session,
        close_session: CloseSession,
        observations: tuple[open_session_work.SessionCloseWork, ...],
    ) -> None:
        """Record the confirmed close and every work item that it stopped.

        Raises:
            ValueError: If an input value is not valid.

        """
        if session.plugin is None:
            message = f"session has no attached harness plugin: {session.session_id}"
            raise ValueError(message)
        observed_at = time.time()
        harness = session.plugin.harness_info.name
        raw_events = [
            session_close_events.session_finish_event(
                session,
                close_session,
                harness,
                observed_at,
            ),
        ]
        raw_events.extend(
            session_close_events.work_close_event(
                work,
                close_session,
                harness,
                observed_at,
            )
            for work in observations
        )
        self.raw_events.record(tuple(raw_events))
