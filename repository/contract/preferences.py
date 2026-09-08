# Copyright (c) 2026 Zhambyl Yermagambet
"""What YOU chose — seven aggregates, nine tables, no key-value store.

Each of these was a JSON blob under a key in one `kv` table. The pruning
policies that used to be Python read-modify-write loops are now part of the
write method, and run in its transaction.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

    from domain.ids import SessionId, TaskId
    from domain.preferences import (
        DraftWrite,
        HiddenDirectory,
        NewSessionDraft,
        NewSessionPreferences,
        PushSigningKeypair,
        PushSubscription,
        ViewMode,
    )


class ViewModeRepository(Protocol):
    """One session's mirror density. Absent means the caller's default."""

    def view_mode(self, session_id: SessionId) -> ViewMode | None:
        """Return the view mode."""
        ...

    def set_view_mode(self, session_id: SessionId, view_mode: ViewMode) -> None:
        """Set view mode."""
        ...

    def clear_view_mode(self, session_id: SessionId) -> None:
        """Clear view mode.

        Back to the default. Stored as an ABSENCE, so the table stays the
                small set of sessions someone actually switched.
        """
        ...


class NotificationSettingRepository(Protocol):
    """One global switch, and the set of sessions muted under it.

    An alert fires only when both say yes. The global off OVERRIDES the mutes;
    the global on leaves them applying.
    """

    def alerting_enabled(self) -> bool:
        """Defaults to True when never set: a fresh install alerts until you opt out."""
        ...

    def set_alerting_enabled(self, *, enabled: bool) -> None:
        """Set alerting enabled."""
        ...

    def muted_session_ids(self) -> frozenset[SessionId]:
        """Return the muted session ids.

        Every muted session in one query — the notifier asks once per pass,
                not once per armed session.
        """
        ...

    def set_muted(self, session_id: SessionId, *, muted: bool) -> None:
        """Set muted."""
        ...


class HiddenDirectoryRepository(Protocol):
    """Represent hidden directory repository."""

    def hidden(self) -> tuple[HiddenDirectory, ...]:
        """Return the hidden."""
        ...

    def hide(self, working_directory: str, hidden_at: float) -> None:
        """Hide.

        Stamp a directory hidden. A re-hide overwrites with the newer time,
                which is what re-hides it.
        """
        ...


class NewSessionRepository(Protocol):
    """Represent new session repository."""

    def preferences(self) -> NewSessionPreferences | None:
        """Return the preferences."""
        ...

    def save_preferences(self, new_session_preferences: NewSessionPreferences) -> None:
        """Save preferences."""
        ...

    def drafts(self) -> tuple[NewSessionDraft, ...]:
        """Return the drafts."""
        ...

    def save_draft(self, new_session_draft: NewSessionDraft, keep_newest: int) -> DraftWrite:
        """Stale-sequence compare, write and prune, in one transaction.

        A write older than the stored sequence is REJECTED, per directory, so
        two directories' saves never fight. The map is pruned to `keep_newest`
        by sequence — tombstones included, because recency and not emptiness is
        what decides.
        """
        ...


class TaskDismissalRepository(Protocol):
    """Represent task dismissal repository."""

    def dismissed_task_ids(self, session_id: SessionId) -> frozenset[TaskId]:
        """Return the dismissed task ids."""
        ...

    def dismiss(
        self,
        session_id: SessionId,
        task_ids: Sequence[TaskId],
        dismissed_at: float,
        keep_newest: int,
    ) -> None:
        """Record which ids the dismissal covered, and prune old sessions.

        The id SET is stored rather than a flag because the card must come back
        when the list moves on: a new task, or a completed one re-opened, makes
        the current list differ and the caller re-shows the card on its own.
        """
        ...

    def restore(self, session_id: SessionId) -> None:
        """Restore."""
        ...


class PushSubscriptionRepository(Protocol):
    """Represent push subscription repository."""

    def subscriptions(self) -> tuple[PushSubscription, ...]:
        """Return the subscriptions."""
        ...

    def upsert(self, push_subscription: PushSubscription) -> None:
        """Return the upsert.

        Keyed by endpoint, so a re-subscribe from the same browser replaces
                its prior entry instead of piling up duplicates.
        """
        ...

    def remove(self, endpoint: str) -> None:
        """Remove remove.

        An unsubscribe, or a prune after the push service reports it gone.
        """
        ...


class PushSigningKeyRepository(Protocol):
    """The VAPID keypair. A secret we mint, with its own lifecycle."""

    def keypair(self) -> PushSigningKeypair | None:
        """Return the keypair."""
        ...

    def save_keypair(self, push_signing_keypair: PushSigningKeypair) -> None:
        """Save keypair."""
        ...
