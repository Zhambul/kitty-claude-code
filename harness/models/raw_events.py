# Copyright (c) 2026 Zhambyl Yermagambet
"""Raw events and what interpreting them produces.

The floor of the harness contract: one observation as recorded bytes, the
decision a translator reached about it, and the two constructors that keep
event identity and stored-event stamping in one place.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.event_base import CanonicalEvent, EventPayload
from domain.ids import AccountId, ActorId, HarnessName, RawEventId, SessionId, WindowId
from domain.records import InterpretationAudit, RecordedTranslationDecision


@dataclass(frozen=True)
class RawEvent:
    """Represent raw event."""

    raw_event_id: RawEventId
    harness: HarnessName
    source_type: str
    source_name: str
    source_position: str
    session_id: SessionId
    actor_id: ActorId
    parent_actor_id: ActorId | None
    observed_at: float
    encoding: str
    payload: bytes
    # Which observer produced this. It is the resume key: the recorder stores it,
    # and a pulled source is resumed from the `source_position` of the LAST
    # recorded raw event carrying its identity. Pushed observers (hooks) have no
    # resume and may leave it at their source_type.
    source_identity: str = ""
    # Set only on a hook's raw event, None everywhere else. Flat and typed: a hook
    # delivery is the one observation made from INSIDE the session's terminal
    # window and process tree, so what it saw around itself rides its row.
    terminal_window_id: WindowId | None = None
    harness_process_id: int | None = None
    account_id: AccountId | None = None
    account_display_name: str | None = None


@dataclass(frozen=True)
class RawEventAudit:
    """One raw event and its optional interpretation audit."""

    raw_event: RawEvent
    interpretation: InterpretationAudit | None


@dataclass(frozen=True)
class TranslationResult:
    """Represent translation result."""

    canonical_events: tuple[CanonicalEvent[EventPayload], ...]
    decision: RecordedTranslationDecision
    reason: str | None = None

    def __post_init__(self) -> None:
        """Validate the initialized object.

        Raises:
            ValueError: If an input value is not valid.

        """
        if self.decision == RecordedTranslationDecision.TRANSLATED and not self.canonical_events:
            message = "translated observations must produce at least one canonical event"
            raise ValueError(message)
        if self.decision != RecordedTranslationDecision.TRANSLATED and self.canonical_events:
            message = "ignored observations cannot produce canonical events"
            raise ValueError(message)


class TranslationError(ValueError):
    """Represent translation error."""

    def __init__(self, reason: str, *, context: str | None = None) -> None:
        """Initialize the object."""
        super().__init__(reason)
        self.reason = reason
        self.context = context


class UnknownRawEventError(ValueError):
    """A raw event we can read but have no fact for — a tool nothing maps.

    Raised rather than returned as nothing, because "deliberately not semantic"
    and "never seen before" are different answers and only one of them is worth
    looking at: this becomes the `ignored_unknown` verdict, visible in the audit
    and absent from the feed. It replaces failing the whole record, which is
    what an unmapped tool used to do.
    """

    def __init__(self, reason: str, *, context: str | None = None) -> None:
        """Initialize the object."""
        super().__init__(reason)
        self.reason = reason
        self.context = context


@dataclass(frozen=True)
class RawEventSourceContext:
    """Represent raw event source context."""

    session_id: SessionId
    lead_actor_id: ActorId
    actor_id: ActorId
    parent_actor_id: ActorId | None
    source_reference: str


# --- Shell output directives --------------------------------------------------
#
# A hook that makes a command's output observable cannot follow the file itself —
# it must exit immediately. So the gateway records an output-location directive:
# a raw event carrying the typed `ShellOutputLocated` payload. The core
# translator turns it into the fact, the reaction starts the following, and the
# collect phase reads the file's chunks as their own raw events.

OUTPUT_LOCATION_SOURCE_TYPE = "output_location"
LIVENESS_SOURCE_TYPE = "liveness"
INTERRUPT_SOURCE_TYPE = "interrupt"
CONTROL_SOURCE_TYPE = "control"
RESUME_SOURCE_TYPE = "resume_launch"
RESUME_LIVENESS_SOURCE_TYPE = "resume_liveness"
TITLE_SOURCE_TYPE = "title"
AUTOMATIC_TITLE_SOURCE_TYPE = "automatic_title"
