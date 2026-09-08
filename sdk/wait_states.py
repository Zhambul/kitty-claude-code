# Copyright (c) 2026 Zhambyl Yermagambet
"""State values for SDK wait operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.diagnostics.models import DiagnosticsCheckpointResponse

DRAIN_STABLE_READ_COUNT = 2


@dataclass
class SessionCandidates:
    """Store session IDs found during a launch wait."""

    session_ids: list[str] = field(default_factory=list)


@dataclass
class DrainProgress:
    """Track stable reads while the event pipeline drains."""

    previous_raw_event_cursor: int = -1
    stable_read_count: int = 0

    def observe(self, checkpoint: DiagnosticsCheckpointResponse) -> bool:
        """Record a checkpoint and report if the pipeline is drained.

        Returns:
            True when the pipeline is empty and stable.

        """
        if checkpoint.raw_event_cursor == self.previous_raw_event_cursor:
            self.stable_read_count += 1
        else:
            self.stable_read_count = 0
        self.previous_raw_event_cursor = checkpoint.raw_event_cursor
        return (
            checkpoint.pending_raw_event_count == 0
            and checkpoint.reaction_cursor >= checkpoint.canonical_cursor
            and self.stable_read_count >= DRAIN_STABLE_READ_COUNT
        )
