# Copyright (c) 2026 Zhambyl Yermagambet
"""Record automatic titles as harness observations."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from domain.ids import RawEventId
from domain.work_state import TitleOrigin
from harness.models.control_observations import SessionRenameObservation
from harness.models.raw_events import (
    AUTOMATIC_TITLE_SOURCE_TYPE,
    RawEvent,
)
from naming.errors import MissingHarnessPluginError
from repository.mapper.documents import encode_document

if TYPE_CHECKING:
    from harness.models.session import (
        Session,
    )
    from repository.contract.facts import RawEventRepository


class AutomaticTitleRecorder:
    """Record automatic title changes in the raw event stream."""

    def __init__(self, raw_event_repository: RawEventRepository) -> None:
        """Create a recorder with its raw event repository."""
        self.raw_events = raw_event_repository

    def record(self, session: Session, job_key: str, title: str) -> None:
        """Record one automatic title observation.

        Raises:
            MissingHarnessPluginError: If a required harness plug-in is absent.

        """
        if session.plugin is None:
            raise MissingHarnessPluginError(str(session.session_id))
        observation = SessionRenameObservation(title, TitleOrigin.AUTOMATIC)
        source_identity = f"automatic-title:{session.session_id}"
        self.raw_events.record(
            (
                RawEvent(
                    raw_event_id=RawEventId(f"automatic-title:{job_key}"),
                    harness=session.plugin.harness_info.name,
                    source_type=AUTOMATIC_TITLE_SOURCE_TYPE,
                    source_name="automatic_title",
                    source_position=job_key,
                    session_id=session.session_id,
                    actor_id=session.lead_actor_id,
                    parent_actor_id=None,
                    observed_at=time.time(),
                    encoding="json",
                    payload=encode_document(observation),
                    source_identity=source_identity,
                ),
            ),
        )
