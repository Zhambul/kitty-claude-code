# Copyright (c) 2026 Zhambyl Yermagambet
"""The follow list: one row per command output file being read to its end.

Rows are written by the reaction to the committed `shell.output_located` fact,
marked finishing by the reaction to `shell.finished` (foreground rows only) or
by the harness's own completion notification, and removed when the reader
reaches the end.

Nothing here touches the filesystem. `remove_expired` RETURNS what it removed
so the caller can unlink the files — deleting a user's file was previously a
side effect of listing the rows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from domain.ids import SessionId, ShellId
    from domain.shells import ShellOutputFollowing


class ShellOutputLifecycle(Protocol):
    """Apply lifecycle changes to followed shell output."""

    def mark_shell_finished(self, session_id: SessionId, shell_id: ShellId) -> None:
        """Mark shell finished.

        End a FOREGROUND following. A background row's launch reports
                "finished" while output keeps flowing, so it is untouched here — its end
                is `mark_finishing` or the session's.
        """
        ...

    def mark_finishing(self, session_id: SessionId, shell_id: ShellId) -> None:
        """Mark finishing.

        The output file is complete whatever its `until`: drain and remove.
        """
        ...

    def outlive_shell(self, session_id: SessionId, shell_id: ShellId) -> None:
        """Return the outlive shell.

        This following must survive its command's `finished` — the command
                moved to the background mid-run.

                Re-arms `state` as well as `until`, because the two facts come from the
                SAME raw event: if the finish is applied first the row is already
                `finishing`, and one drain later the file the job is still writing to is
                unlinked. Translators emit `shell.backgrounded` first so that does not
                happen; re-arming is what makes the order a preference rather than a
                requirement.
        """
        ...


class ShellOutputRepository(ShellOutputLifecycle, Protocol):
    """Store, read, and remove followed output with its lifecycle changes."""

    def save(self, shell_output_following: ShellOutputFollowing) -> None:
        """Insert-or-ignore: the fact may be re-observed, the following is one."""
        ...

    def find_for_session(self, session_id: SessionId) -> tuple[ShellOutputFollowing, ...]:
        """Return for session."""
        ...

    def oldest_created_at(self) -> float | None:
        """Return the oldest output start time, including finished sessions."""
        ...

    def remove(self, session_id: SessionId, shell_id: ShellId, source_path: str) -> None:
        """Remove remove."""
        ...

    def remove_expired(self, created_before: float) -> tuple[ShellOutputFollowing, ...]:
        """Remove expired.

        Drop followings older than the cutoff and return them, so the caller
                can unlink the source files it owns.
        """
        ...
