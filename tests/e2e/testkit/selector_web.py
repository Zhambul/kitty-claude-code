# Copyright (c) 2026 Zhambyl Yermagambet
"""Select stable web activity references."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from api.sessiondata.models.entry import SearchBodyResponse, WebBodyResponse
from tests.e2e.testkit import references as refs
from tests.e2e.testkit.selector_common import belongs_to_turn

if TYPE_CHECKING:
    from sdk.client import SessionWatch
    from sdk.state import SessionSnapshot


def _find_search(
    snapshot: SessionSnapshot,
    turn_reference: refs.TurnRef,
    query_contains: str,
) -> refs.SearchRef | None:
    candidates = [
        entry
        for entry in snapshot.entries
        if isinstance(entry.body, SearchBodyResponse)
        and query_contains in entry.body.query.text
        and entry.body.state == "succeeded"
        and belongs_to_turn(
            snapshot,
            turn_reference,
            turn_id=entry.turn_id,
            cursor=entry.cursor,
        )
    ]
    entry = min(candidates, key=lambda candidate: candidate.cursor) if candidates else None
    if entry is None:
        return None
    return refs.SearchRef(snapshot.session_reference, entry.entry_id)


def search(
    watch: SessionWatch,
    *,
    turn_reference: refs.TurnRef,
    query_contains: str,
    timeout: float,
) -> refs.SearchRef:
    """Find the first successful search in a turn.

    Returns:
        The search reference.

    """
    return watch.wait(
        f"a successful search with query containing {query_contains!r}",
        partial(
            _find_search,
            turn_reference=turn_reference,
            query_contains=query_contains,
        ),
        timeout=timeout,
    )


def _find_web_fetch(
    snapshot: SessionSnapshot,
    turn_reference: refs.TurnRef,
    url: str,
) -> refs.WebFetchRef | None:
    candidates = [
        entry
        for entry in snapshot.entries
        if isinstance(entry.body, WebBodyResponse)
        and entry.body.url == url
        and entry.body.state == "succeeded"
        and belongs_to_turn(
            snapshot,
            turn_reference,
            turn_id=entry.turn_id,
            cursor=entry.cursor,
        )
    ]
    entry = min(candidates, key=lambda candidate: candidate.cursor) if candidates else None
    if entry is None:
        return None
    return refs.WebFetchRef(snapshot.session_reference, entry.entry_id)


def web_fetch(
    watch: SessionWatch,
    *,
    turn_reference: refs.TurnRef,
    url: str,
    timeout: float,
) -> refs.WebFetchRef:
    """Find the first successful web fetch in a turn.

    Returns:
        The web fetch reference.

    """
    return watch.wait(
        f"a successful web fetch for {url!r}",
        partial(_find_web_fetch, turn_reference=turn_reference, url=url),
        timeout=timeout,
    )
