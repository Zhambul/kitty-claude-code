# Copyright (c) 2026 Zhambyl Yermagambet
"""The fallback finish signal for an interrupt no native raw event corroborates.

Some harnesses' raw event streams carry no record that distinguishes a turn
cut short by an interrupt from one that finished on its own, so a session's
busy state can get stuck after an otherwise-successful interrupt. See
`harness.models.InterruptRegistry` for who marks it and why.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from domain.ids import RawEventId
from harness.contract import HarnessRawEventSource
from harness.models.directives import InterruptMark
from harness.models.raw_events import (
    INTERRUPT_SOURCE_TYPE,
    RawEvent,
)
from repository.mapper.documents import encode_document

if TYPE_CHECKING:
    from harness.models.interrupts import (
        InterruptRegistry,
    )
    from harness.models.session import (
        Session,
    )

# How long a marked interrupt waits for the harness's OWN raw event to settle
# the turn on its own before the fallback fires. Long enough that an ordinary
# end-of-turn record — which lands within a tick or two of the harness
# actually quitting — always wins; short enough that a session which truly
# got no further raw event still clears within a few seconds rather than
# staying "busy" indefinitely.
GRACE_SECONDS = 3.0


class PendingInterruptSource(HarnessRawEventSource):
    """Represent pending interrupt source.

    Built by the interpreter for every unfinished session, same as
        `SessionLivenessSource`. Emits nothing until the registry has a pending
        mark AND `GRACE_SECONDS` has passed with no newer mark superseding it —
        the wait is what lets a genuine harness raw event win the race.
    """

    def __init__(self, session: Session, interrupt_registry: InterruptRegistry) -> None:
        """Initialize the object.

        Raises:
            ValueError: If an input value is not valid.

        """
        if session.plugin is None:
            message = f"session has no attached harness plugin: {session.session_id}"
            raise ValueError(message)
        self.session = session
        self.interrupt_registry = interrupt_registry
        harness_name = session.plugin.harness_info.name
        self.harness_name = harness_name
        self.source_identity = f"{harness_name}:interrupt:{session.session_id}"

    def read(self, after_position: str | None) -> tuple[RawEvent, ...]:
        """Return read.

        Returns:
            Read.

        """
        marked_at = self.interrupt_registry.pending(self.session.session_id)
        if marked_at is None:
            return ()
        position = f"{marked_at:.6f}"
        if after_position == position:
            return ()
        if time.time() - marked_at < GRACE_SECONDS:
            return ()
        return (
            RawEvent(
                raw_event_id=RawEventId(f"{self.source_identity}:{position}"),
                harness=self.harness_name,
                source_type=INTERRUPT_SOURCE_TYPE,
                source_name="interrupt",
                source_position=position,
                session_id=self.session.session_id,
                actor_id=self.session.lead_actor_id,
                parent_actor_id=None,
                observed_at=marked_at,
                encoding="json",
                payload=encode_document(InterruptMark(session_id=self.session.session_id)),
                source_identity=self.source_identity,
            ),
        )
