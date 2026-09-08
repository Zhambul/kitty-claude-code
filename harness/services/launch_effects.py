# Copyright (c) 2026 Zhambyl Yermagambet
"""Record confirmed session-launch effects as raw observations."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from domain.ids import HarnessName, RawEventId, SessionId, WindowId
from harness.contract import SessionResumeRecorder
from harness.models.directives import SessionResumeObservation
from harness.models.raw_events import (
    RESUME_SOURCE_TYPE,
    RawEvent,
)
from repository.mapper.documents import encode_document

if TYPE_CHECKING:
    from repository.contract.facts import RawEventRepository
    from repository.contract.sessions import SessionRepository


class SessionLaunchEffectRecorder(SessionResumeRecorder):
    """Make a confirmed resume launch available to the interpreter."""

    def __init__(
        self,
        raw_event_repository: RawEventRepository,
        session_repository: SessionRepository,
    ) -> None:
        """Initialize the object."""
        self.raw_events = raw_event_repository
        self.sessions = session_repository

    def resumed(
        self,
        harness: HarnessName,
        session_id: SessionId,
        window_id: WindowId,
    ) -> None:
        """Return the resumed.

        Raises:
            ValueError: If an input value is not valid.

        """
        session = self.sessions.find(session_id)
        if session is None:
            message = f"cannot resume unknown session: {session_id}"
            raise ValueError(message)
        identity = f"{harness}:resume:{session_id}:{window_id}"
        self.raw_events.record(
            (
                RawEvent(
                    raw_event_id=RawEventId(identity),
                    harness=harness,
                    source_type=RESUME_SOURCE_TYPE,
                    source_name="session_resume",
                    source_position=str(window_id),
                    session_id=session_id,
                    actor_id=session.lead_actor_id,
                    parent_actor_id=None,
                    observed_at=time.time(),
                    encoding="json",
                    payload=encode_document(
                        SessionResumeObservation(
                            working_directory=session.working_directory or "",
                            source_reference=session.source_reference,
                        ),
                    ),
                    source_identity=f"{harness}:resume:{session_id}",
                    terminal_window_id=window_id,
                    harness_process_id=None,
                ),
            ),
        )
