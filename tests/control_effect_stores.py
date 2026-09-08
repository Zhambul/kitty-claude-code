# Copyright (c) 2026 Zhambyl Yermagambet
"""Control effect stores."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import (
    composer,
    entries as domain_entries,
    ids as domain_ids,
    workspace,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from harness.models import raw_events as raw_event_models
    from harness.models.session import (
        Session,
    )

from tests import control_effect_values as control_values


class RawEvents:
    """Represent raw events."""

    def __init__(self) -> None:
        """Create an empty raw-event recorder."""
        self.events: list[raw_event_models.RawEvent] = []

    def record(self, raw_events: Sequence[raw_event_models.RawEvent]) -> None:
        """Record record."""
        self.events.extend(raw_events)


class Workspaces:
    """Represent workspaces."""

    def __init__(self) -> None:
        """Create an empty queued-message record."""
        self.queued: list[tuple[domain_ids.SessionId, composer.QueuedMessage, str]] = []

    def enqueue_composer_message(
        self,
        session_id: domain_ids.SessionId,
        message: composer.QueuedMessage,
        origin: str,
    ) -> None:
        """Process enqueue composer message."""
        self.queued.append((session_id, message, origin))


class SessionEntries:
    """Represent session entries."""

    def __init__(self, entries: tuple[domain_entries.SessionEntry, ...] = ()) -> None:
        """Store fixed session entries."""
        self.entries = tuple(entries)

    def entries_of_types(
        self,
        _session_id: domain_ids.SessionId,
        _entry_types: Sequence[str],
    ) -> tuple[domain_entries.SessionEntry, ...]:
        """Provide the fixed entries without applying query filters.

        Returns:
            All entries supplied to this test store.

        """
        return self.entries


class Sessions:
    """Represent sessions."""

    def __init__(self, session: Session) -> None:
        """Store one session fixture."""
        self.session = session

    def find(self, session_id: domain_ids.SessionId) -> Session | None:
        """Return find.

        Returns:
            Find.

        """
        return self.session if self.session.session_id == session_id else None


class DurableQueue:
    """Represent durable queue."""

    def __init__(self) -> None:
        """Create one queued-message fixture."""
        self.session_id = control_values.TEST_SESSION_ID
        self.messages = [
            composer.QueuedMessage(control_values.TEST_REQUEST_ID, "same prompt"),
            composer.QueuedMessage(domain_ids.RequestId("request-two"), "same prompt"),
        ]
        self.removed: list[domain_ids.RequestId] = []

    def find(self, session_id: domain_ids.SessionId) -> workspace.SessionWorkspace:
        """Return find.

        Returns:
            Find.

        """
        assert session_id == self.session_id
        return workspace.SessionWorkspace(
            session_id,
            queue=composer.ComposerQueue(tuple(self.messages), "send"),
        )

    def remove_queued_message(self, session_id: domain_ids.SessionId, request_id: domain_ids.RequestId) -> None:
        """Remove queued message."""
        assert session_id == self.session_id
        self.removed.append(request_id)
        self.messages = [message for message in self.messages if message.request_id != request_id]

    def enqueue_composer_message(
        self,
        session_id: domain_ids.SessionId,
        queued_message: composer.QueuedMessage,
        origin: str,
    ) -> None:
        """Add a queued message."""
        assert session_id == self.session_id
        assert origin
        self.messages.append(queued_message)
