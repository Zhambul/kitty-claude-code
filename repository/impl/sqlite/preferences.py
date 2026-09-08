# Copyright (c) 2026 Zhambyl Yermagambet
"""The nine preference tables that replaced one key-value table.

The pruning policies that used to be Python read-modify-write loops over a JSON
map are `DELETE … WHERE … NOT IN (SELECT … ORDER BY … LIMIT ?)` inside the same
transaction as the write that triggers them. The "default is an absence" rule
survives: a mode set back to the default deletes its row, so each table stays
the small set of things someone actually chose.
"""

from __future__ import annotations

from dataclasses import astuple
from typing import TYPE_CHECKING

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
from repository.contract.preferences import (
    HiddenDirectoryRepository,
    NewSessionRepository,
    NotificationSettingRepository,
    PushSigningKeyRepository,
    PushSubscriptionRepository,
    TaskDismissalRepository,
    ViewModeRepository,
)
from repository.impl.sqlite import rows
from repository.mapper import preferences as mapper, push_preferences as push_mapper

if TYPE_CHECKING:
    from collections.abc import Sequence

    from repository.impl.sqlite.connection import SqliteDatabase


class SqliteViewModeRepository(ViewModeRepository):
    """Represent sqlite view mode repository."""

    def __init__(self, sqlite_database: SqliteDatabase) -> None:
        """Initialize the view-mode repository."""
        self.sqlite_database = sqlite_database

    def view_mode(self, session_id: SessionId) -> ViewMode | None:
        """Return the view mode.

        Returns:
            View mode.

        """
        with self.sqlite_database.read() as connection:
            row = connection.execute(
                "SELECT * FROM session_view_modes WHERE session_id=?",
                (str(session_id),),
            ).fetchone()
        return None if row is None else mapper.view_mode(rows.session_view_mode(row))

    def set_view_mode(self, session_id: SessionId, view_mode: ViewMode) -> None:
        """Set view mode."""
        with self.sqlite_database.write() as connection:
            connection.execute(
                "INSERT INTO session_view_modes(session_id, view_mode) VALUES(?, ?) "
                "ON CONFLICT(session_id) DO UPDATE SET view_mode=excluded.view_mode",
                (str(session_id), view_mode),
            )

    def clear_view_mode(self, session_id: SessionId) -> None:
        """Clear view mode."""
        with self.sqlite_database.write() as connection:
            connection.execute(
                "DELETE FROM session_view_modes WHERE session_id=?",
                (str(session_id),),
            )


class SqliteNotificationSettingRepository(NotificationSettingRepository):
    """Represent sqlite notification setting repository."""

    def __init__(self, sqlite_database: SqliteDatabase) -> None:
        """Initialize the notification-setting repository."""
        self.sqlite_database = sqlite_database

    def alerting_enabled(self) -> bool:
        """Return the alerting enabled.

        Returns:
            Alerting enabled.

        """
        with self.sqlite_database.read() as connection:
            row = connection.execute(
                "SELECT alerting_enabled FROM notification_settings WHERE id=1",
            ).fetchone()
        # Absent reads True: a fresh install alerts until the user opts out.
        return True if row is None else bool(row["alerting_enabled"])

    def set_alerting_enabled(self, *, enabled: bool) -> None:
        """Set alerting enabled."""
        with self.sqlite_database.write() as connection:
            connection.execute(
                "INSERT INTO notification_settings(id, alerting_enabled) VALUES(1, ?) "
                "ON CONFLICT(id) DO UPDATE SET alerting_enabled=excluded.alerting_enabled",
                (1 if enabled else 0,),
            )

    def muted_session_ids(self) -> frozenset[SessionId]:
        """Return the muted session ids.

        Returns:
            Muted session ids.

        """
        with self.sqlite_database.read() as connection:
            found = connection.execute(
                "SELECT session_id FROM session_notification_mutes",
            ).fetchall()
        return frozenset(SessionId(row["session_id"]) for row in found)

    def set_muted(self, session_id: SessionId, *, muted: bool) -> None:
        """Set muted."""
        session_id_text = str(session_id)
        with self.sqlite_database.write() as connection:
            if muted:
                connection.execute(
                    "INSERT OR IGNORE INTO session_notification_mutes(session_id, muted_at) "
                    "VALUES(?, strftime('%s','now'))",
                    (session_id_text,),
                )
            else:
                connection.execute(
                    "DELETE FROM session_notification_mutes WHERE session_id=?",
                    (session_id_text,),
                )


class SqliteHiddenDirectoryRepository(HiddenDirectoryRepository):
    """Represent sqlite hidden directory repository."""

    def __init__(self, sqlite_database: SqliteDatabase) -> None:
        """Initialize the hidden-directory repository."""
        self.sqlite_database = sqlite_database

    def hidden(self) -> tuple[HiddenDirectory, ...]:
        """Return the hidden.

        Returns:
            Hidden.

        """
        with self.sqlite_database.read() as connection:
            found = connection.execute(
                "SELECT * FROM hidden_directories ORDER BY working_directory",
            ).fetchall()
        return tuple(mapper.hidden_directory(rows.hidden_directory(row)) for row in found)

    def hide(self, working_directory: str, hidden_at: float) -> None:
        """Hide."""
        with self.sqlite_database.write() as connection:
            connection.execute(
                "INSERT INTO hidden_directories(working_directory, hidden_at) VALUES(?, ?) "
                "ON CONFLICT(working_directory) DO UPDATE SET hidden_at=excluded.hidden_at",
                (str(working_directory), float(hidden_at)),
            )


class SqliteNewSessionRepository(NewSessionRepository):
    """Represent sqlite new session repository."""

    def __init__(self, sqlite_database: SqliteDatabase) -> None:
        """Initialize the new-session repository."""
        self.sqlite_database = sqlite_database

    def preferences(self) -> NewSessionPreferences | None:
        """Return the preferences.

        Returns:
            Preferences.

        """
        with self.sqlite_database.read() as connection:
            row = connection.execute(
                "SELECT * FROM new_session_preferences WHERE id=1",
            ).fetchone()
        if row is None:
            return None
        return mapper.new_session_preferences(rows.new_session_preference(row))

    def save_preferences(self, new_session_preferences: NewSessionPreferences) -> None:
        """Save preferences."""
        with self.sqlite_database.write() as connection:
            connection.execute(
                "INSERT INTO new_session_preferences(id, working_directory, harness, model, effort) "
                "VALUES(1, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
                "working_directory=excluded.working_directory, harness=excluded.harness, "
                "model=excluded.model, effort=excluded.effort",
                (
                    new_session_preferences.working_directory,
                    new_session_preferences.harness,
                    new_session_preferences.model,
                    new_session_preferences.effort,
                ),
            )

    def drafts(self) -> tuple[NewSessionDraft, ...]:
        """Return the drafts.

        Returns:
            Drafts.

        """
        with self.sqlite_database.read() as connection:
            found = connection.execute(
                "SELECT * FROM new_session_drafts ORDER BY working_directory",
            ).fetchall()
        return tuple(mapper.new_session_draft(rows.new_session_draft(row)) for row in found)

    def save_draft(self, new_session_draft: NewSessionDraft, keep_newest: int) -> DraftWrite:
        """Save draft.

        Returns:
            The draft write.

        """
        with self.sqlite_database.write() as connection:
            current = connection.execute(
                "SELECT * FROM new_session_drafts WHERE working_directory=?",
                (new_session_draft.working_directory,),
            ).fetchone()
            if current is not None and new_session_draft.sequence < current["sequence"]:
                # A debounced save in flight when the launch cleared the box
                # must not resurrect it by landing later.
                return DraftWrite(draft=mapper.new_session_draft(rows.new_session_draft(current)), stale=True)
            connection.execute(
                "INSERT INTO new_session_drafts(working_directory, text, sequence) "
                "VALUES(?, ?, ?) ON CONFLICT(working_directory) DO UPDATE SET "
                "text=excluded.text, sequence=excluded.sequence",
                (
                    new_session_draft.working_directory,
                    new_session_draft.text,
                    new_session_draft.sequence,
                ),
            )
            connection.execute(
                "DELETE FROM new_session_drafts WHERE working_directory NOT IN ("
                "  SELECT working_directory FROM new_session_drafts "
                "  ORDER BY sequence DESC LIMIT ?)",
                (keep_newest,),
            )
        return DraftWrite(draft=new_session_draft, stale=False)


class SqliteTaskDismissalRepository(TaskDismissalRepository):
    """Represent sqlite task dismissal repository."""

    def __init__(self, sqlite_database: SqliteDatabase) -> None:
        """Initialize the task-dismissal repository."""
        self.sqlite_database = sqlite_database

    def dismissed_task_ids(self, session_id: SessionId) -> frozenset[TaskId]:
        """Return the dismissed task ids.

        Returns:
            Dismissed task ids.

        """
        with self.sqlite_database.read() as connection:
            found = connection.execute(
                "SELECT task_id FROM task_dismissals WHERE session_id=?",
                (str(session_id),),
            ).fetchall()
        return frozenset(TaskId(row["task_id"]) for row in found)

    def dismiss(
        self,
        session_id: SessionId,
        task_ids: Sequence[TaskId],
        dismissed_at: float,
        keep_newest: int,
    ) -> None:
        """Return the dismiss."""
        session_id_text = str(session_id)
        with self.sqlite_database.write() as connection:
            connection.execute(
                "DELETE FROM task_dismissals WHERE session_id=?",
                (session_id_text,),
            )
            connection.executemany(
                "INSERT INTO task_dismissals(session_id, task_id, dismissed_at) VALUES(?, ?, ?)",
                tuple((session_id_text, str(task_id), dismissed_at) for task_id in task_ids),
            )
            # Bound by SESSION, not by row: a finished task list is dismissed
            # for most sessions eventually, and the map would otherwise gain a
            # row per session forever.
            connection.execute(
                "DELETE FROM task_dismissals WHERE session_id NOT IN ("
                "  SELECT session_id FROM task_dismissals "
                "  GROUP BY session_id ORDER BY MAX(dismissed_at) DESC LIMIT ?)",
                (keep_newest,),
            )

    def restore(self, session_id: SessionId) -> None:
        """Restore."""
        with self.sqlite_database.write() as connection:
            connection.execute(
                "DELETE FROM task_dismissals WHERE session_id=?",
                (str(session_id),),
            )


class SqlitePushSubscriptionRepository(PushSubscriptionRepository):
    """Represent sqlite push subscription repository."""

    def __init__(self, sqlite_database: SqliteDatabase) -> None:
        """Initialize the push-subscription repository."""
        self.sqlite_database = sqlite_database

    def subscriptions(self) -> tuple[PushSubscription, ...]:
        """Return the subscriptions.

        Returns:
            Subscriptions.

        """
        with self.sqlite_database.read() as connection:
            found = connection.execute(
                "SELECT * FROM push_subscriptions ORDER BY created_at DESC",
            ).fetchall()
        return tuple(push_mapper.push_subscription(rows.push_subscription(row)) for row in found)

    def upsert(self, push_subscription: PushSubscription) -> None:
        """Return the upsert."""
        with self.sqlite_database.write() as connection:
            connection.execute(
                "INSERT INTO push_subscriptions(endpoint, public_key, authentication_secret, "
                "device_id, device_label, created_at) VALUES(?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(endpoint) DO UPDATE SET "
                "public_key=excluded.public_key, "
                "authentication_secret=excluded.authentication_secret, "
                "device_id=excluded.device_id, device_label=excluded.device_label, "
                "created_at=excluded.created_at",
                astuple(push_mapper.push_subscription_row(push_subscription)),
            )

    def remove(self, endpoint: str) -> None:
        """Remove remove."""
        with self.sqlite_database.write() as connection:
            connection.execute(
                "DELETE FROM push_subscriptions WHERE endpoint=?",
                (str(endpoint),),
            )


class SqlitePushSigningKeyRepository(PushSigningKeyRepository):
    """Represent sqlite push signing key repository."""

    def __init__(self, sqlite_database: SqliteDatabase) -> None:
        """Initialize the push-signing-key repository."""
        self.sqlite_database = sqlite_database

    def keypair(self) -> PushSigningKeypair | None:
        """Return the keypair.

        Returns:
            Keypair.

        """
        with self.sqlite_database.read() as connection:
            row = connection.execute("SELECT * FROM push_signing_keys WHERE id=1").fetchone()
        return None if row is None else push_mapper.push_signing_keypair(rows.push_signing_key(row))

    def save_keypair(self, push_signing_keypair: PushSigningKeypair) -> None:
        """Save keypair."""
        with self.sqlite_database.write() as connection:
            connection.execute(
                "INSERT INTO push_signing_keys(id, private_key_pem, public_key) "
                "VALUES(1, ?, ?) ON CONFLICT(id) DO UPDATE SET "
                "private_key_pem=excluded.private_key_pem, public_key=excluded.public_key",
                (push_signing_keypair.private_key_pem, push_signing_keypair.public_key),
            )
