# Copyright (c) 2026 Zhambyl Yermagambet
"""Build raw events for a confirmed session close."""

from domain.ids import HarnessName, RawEventId
from harness.models.controls import (
    CloseSession,
)
from harness.models.directives import ProcessExit, ProcessExitState
from harness.models.raw_events import (
    CONTROL_SOURCE_TYPE,
    RawEvent,
)
from harness.models.session import (
    Session,
)
from harness.services.open_session_work import SessionCloseWork
from repository.mapper.documents import encode_document

JSON_ENCODING = "json"


def session_finish_event(
    session: Session,
    close_session: CloseSession,
    harness: HarnessName,
    observed_at: float,
) -> RawEvent:
    """Build the session finish observation.

    Returns:
        The raw event.

    """
    identity = f"{harness}:control:{close_session.session_id}:{close_session.request_id}:session_finish"
    return RawEvent(
        raw_event_id=RawEventId(identity),
        harness=harness,
        source_type=CONTROL_SOURCE_TYPE,
        source_name="session_finish",
        source_position=str(close_session.request_id),
        session_id=close_session.session_id,
        actor_id=session.lead_actor_id,
        parent_actor_id=None,
        observed_at=observed_at,
        encoding=JSON_ENCODING,
        payload=encode_document(
            ProcessExit(
                process_id=session.harness_process_id,
                state=ProcessExitState.EXITED,
            ),
        ),
        source_identity=f"{harness}:control:{close_session.session_id}",
        terminal_window_id=session.terminal_window_id,
        harness_process_id=session.harness_process_id,
    )


def work_close_event(
    session_close_work: SessionCloseWork,
    close_session: CloseSession,
    harness: HarnessName,
    observed_at: float,
) -> RawEvent:
    """Build the close observation for one open work item.

    Returns:
        The raw event.

    """
    identity_parts = (
        str(harness),
        "control",
        str(close_session.session_id),
        str(close_session.request_id),
        str(session_close_work.observation.kind),
        str(session_close_work.observation.subject_id),
    )
    identity = ":".join(identity_parts)
    return RawEvent(
        raw_event_id=RawEventId(identity),
        harness=harness,
        source_type=CONTROL_SOURCE_TYPE,
        source_name="session_close",
        source_position=identity,
        session_id=close_session.session_id,
        actor_id=session_close_work.entry.actor_id,
        parent_actor_id=session_close_work.entry.parent_actor_id,
        observed_at=observed_at,
        encoding=JSON_ENCODING,
        payload=encode_document(session_close_work.observation),
        source_identity=f"{harness}:control:{close_session.session_id}",
    )
