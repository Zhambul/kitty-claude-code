# Copyright (c) 2026 Zhambyl Yermagambet
"""Split SDK client implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlencode

from sdk import application_models, state

if TYPE_CHECKING:
    import builtins

from sdk.client_adapters import (
    ENTRY_PAGE,
    SESSION_DATA,
)
from sdk.client_feed import (
    _matches_delivered_prompt,
    _next_page_cursor,
    _validate_entries,
)
from sdk.client_models import (
    SessionRef,
    SessionSnapshotRead,
)
from sdk.client_session_launch import _SessionsLaunches
from sdk.client_wait import (
    _finished_wait_description,
    wait_for,
)
from sdk.client_watch import SessionWatch


class _SessionsSnapshots(_SessionsLaunches):
    """Read session snapshots and entry pages."""

    def read_snapshot(
        self,
        session: SessionRef,
        *,
        page_size: int = 1000,
    ) -> SessionSnapshotRead:
        """Return snapshot.

        The transport raises ApiFailureError if an API request fails.

        Returns:
            Snapshot.

        Raises:
            ValueError: If an input value is not valid.

        """
        if page_size < 1:
            message = "page size must be positive"
            raise ValueError(message)
        session_id = session.path_segment
        snapshot = self.transport.get(f"/sessionData/{session_id}", SESSION_DATA)
        pages = self._entry_pages(session_id, snapshot.cursor, page_size)
        entries = tuple(entry for page_items in reversed(pages) for entry in page_items)
        _validate_entries(entries, snapshot.cursor)
        return SessionSnapshotRead(
            state.SessionSnapshot(session_data=snapshot, entries=entries),
            len(pages),
        )

    def snapshot(self, session: SessionRef) -> state.SessionSnapshot:
        """Return snapshot.

        Returns:
            Snapshot.

        """
        return self.read_snapshot(session).snapshot

    def watch(self, session: SessionRef) -> SessionWatch:
        """Return the watch.

        Returns:
            Watch.

        """
        return SessionWatch(self, session)

    def wait_until_finished(self, session: SessionRef, timeout: float) -> state.SessionSnapshot:
        """Wait until finished.

        Returns:
            The session snapshot.

        """
        return self.watch(session).wait(
            lambda snapshot: _finished_wait_description(snapshot, session.session_id),
            lambda snapshot: (
                snapshot
                if snapshot.session_data.session.state == "finished"
                and all(actor.state == "finished" for actor in snapshot.session_data.actors)
                else None
            ),
            timeout=timeout,
        )

    def _entry_pages(
        self,
        session_id: str,
        snapshot_cursor: int,
        page_size: int,
    ) -> builtins.list[tuple[application_models.entry.EntryResponse, ...]]:
        pages: builtins.list[tuple[application_models.entry.EntryResponse, ...]] = []
        before: int | None = None
        while True:
            page = self._entry_page(session_id, snapshot_cursor, page_size, before)
            pages.append(page.entries)
            if page.has_more:
                before = _next_page_cursor(page, before)
            else:
                break
        return pages

    def _entry_page(
        self,
        session_id: str,
        snapshot_cursor: int,
        page_size: int,
        before: int | None,
    ) -> application_models.entry.EntryPageResponse:
        query_parameters: dict[str, int] = {"limit": page_size, "at": snapshot_cursor}
        if before is not None:
            query_parameters["before"] = before
        return self.transport.get(
            f"/sessionData/{session_id}/entries?{urlencode(query_parameters)}",
            ENTRY_PAGE,
        )


class _SessionsPromptOwners(_SessionsSnapshots):
    """Find the session that owns a sent prompt."""

    def wait_for_prompt_owner(
        self,
        source: SessionRef,
        *,
        prompt: str,
        after_cursor: int,
        timeout: float,
    ) -> SessionRef:
        """Find the session that accepted a prompt after an in-place action.

        Most harnesses keep the current native session. A harness can instead
        continue under a new native id. The new session states that relation,
        so callers do not need a harness-specific branch.

        Returns:
            The session ref.

        """
        candidates: list[str] = []
        return wait_for(
            lambda: f"prompt {prompt!r} to belong to one of sessions {candidates}",
            lambda: self._find_prompt_owner(candidates, source, prompt, after_cursor),
            timeout=timeout,
        )

    def _find_prompt_owner(
        self,
        candidates: builtins.list[str],
        source: SessionRef,
        prompt: str,
        after_cursor: int,
    ) -> SessionRef | None:
        candidates.clear()
        candidates.extend(self._prompt_candidates(source))
        return self._unique_prompt_owner(candidates, source, prompt, after_cursor)

    def _prompt_candidates(self, source: SessionRef) -> builtins.list[str]:
        listed = self.list()
        continued = [
            session_summary.session.session_id
            for session_summary in listed.sessions
            if session_summary.session.continued_from == source.session_id
        ]
        return [source.session_id, *continued]

    def _unique_prompt_owner(
        self,
        candidates: builtins.list[str],
        source: SessionRef,
        prompt: str,
        after_cursor: int,
    ) -> SessionRef | None:
        matches = [
            session_id for session_id in candidates if self._has_prompt(session_id, source, prompt, after_cursor)
        ]
        if len(matches) > 1:
            message = f"prompt {prompt!r} belongs to multiple sessions: {matches}"
            raise AssertionError(message)
        return SessionRef(matches[0]) if matches else None

    def _has_prompt(
        self,
        session_id: str,
        source: SessionRef,
        prompt: str,
        after_cursor: int,
    ) -> bool:
        snapshot = self.snapshot(SessionRef(session_id))
        lower_bound = after_cursor if session_id == source.session_id else 0
        prompts = [entry for entry in snapshot.entries if _matches_delivered_prompt(entry, lower_bound, prompt)]
        if len(prompts) > 1:
            message = f"session {session_id!r} has {len(prompts)} matching prompts"
            raise AssertionError(message)
        return bool(prompts)
