# Copyright (c) 2026 Zhambyl Yermagambet
"""Update shell-output state after a canonical event."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from domain.event_session import SessionFinished
from domain.event_shell import ShellBackgrounded, ShellFinished, ShellOutputFinished, ShellOutputLocated
from domain.ids import SessionId, ShellId
from domain.shells import ShellFollowState, ShellOutputFollowing
from engine.interpret import output_source
from harness.contract import CanonicalEventReaction

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from repository.contract.facts import RawEventRepository
    from repository.contract.shell_output import ShellOutputRepository


class ShellOutputCanonicalEventReaction(CanonicalEventReaction):
    """Start and stop shell-output file follow operations."""

    def __init__(
        self,
        shell_output_repository: ShellOutputRepository,
        raw_event_repository: RawEventRepository,
    ) -> None:
        """Initialize the object."""
        self.shell_output = shell_output_repository
        self.raw_events = raw_event_repository

    def react(self, canonical_event: CanonicalEvent[EventPayload]) -> None:
        """Update shell-output state for the event."""
        payload = canonical_event.payload
        if isinstance(payload, ShellOutputLocated):
            self._start_following(canonical_event, payload)
            return
        if isinstance(payload, ShellFinished):
            self.shell_output.mark_shell_finished(canonical_event.session_id, payload.shell_id)
            return
        if isinstance(payload, ShellBackgrounded):
            self.shell_output.outlive_shell(canonical_event.session_id, payload.shell_id)
            return
        if isinstance(payload, ShellOutputFinished):
            self.shell_output.mark_finishing(canonical_event.session_id, payload.shell_id)
            return
        if isinstance(payload, SessionFinished):
            self._drain_all(canonical_event.session_id)

    def _start_following(
        self,
        canonical_event: CanonicalEvent[EventPayload],
        shell_output_located: ShellOutputLocated,
    ) -> None:
        self.shell_output.save(
            ShellOutputFollowing(
                session_id=canonical_event.session_id,
                shell_id=shell_output_located.shell_id,
                harness=canonical_event.harness,
                actor_id=canonical_event.actor_id,
                parent_actor_id=canonical_event.parent_actor_id,
                source_path=shell_output_located.source_path,
                chunk_source_type=shell_output_located.chunk_source_type,
                delete_source=shell_output_located.delete_source,
                initial_size=shell_output_located.initial_size,
                initial_modified_at=shell_output_located.initial_modified_at,
                wait_for_source_change=shell_output_located.wait_for_source_change,
                until=shell_output_located.until,
                state=ShellFollowState.ACTIVE,
                created_at=time.time(),
            ),
        )

    def _drain_all(self, session_id: SessionId) -> None:
        followings = self.shell_output.find_for_session(session_id)
        positions = self.raw_events.latest_positions(
            [
                output_source.shell_output_source_identity(
                    following.harness,
                    following.session_id,
                    following.shell_id,
                    following.source_path,
                )
                for following in followings
            ],
        )
        for following in followings:
            source = output_source.ShellOutputRawEventSource(following, self.shell_output)
            raw_events = source.read(positions.get(source.source_identity))
            if raw_events:
                self.raw_events.record(raw_events)
            self.shell_output.remove(
                session_id,
                ShellId(str(following.shell_id)),
                following.source_path,
            )
            output_source.delete_source_file(following)
