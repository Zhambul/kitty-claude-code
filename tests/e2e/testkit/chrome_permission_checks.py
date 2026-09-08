# Copyright (c) 2026 Zhambyl Yermagambet
"""Check stored results for the Claude-in-Chrome E2E test."""

from __future__ import annotations

import sqlite3
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

WAIT_POLL_SECONDS = 0.05


def wait(
    description: str,
    predicate: Callable[[], bool],
    timeout: float = 20.0,
) -> None:
    """Wait for one Chrome test result.

    Raises:
        AssertionError: If the predicate does not become true before the timeout.

    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(WAIT_POLL_SECONDS)
    raise AssertionError(description)


def permission_request_was_recorded(database_path: Path, session_id: str) -> bool:
    """Return true when one permission request is stored.

    Returns:
        True when one permission request is stored.

    """
    with sqlite3.connect(f"file:{database_path}?mode=ro", uri=True) as connection:
        row = connection.execute(
            "SELECT count(*) FROM raw_events WHERE session_id=? AND source_name='PermissionRequest'",
            (session_id,),
        ).fetchone()
    return row is not None and int(row[0]) == 1


def browser_action_was_recorded(database_path: Path, session_id: str) -> bool:
    """Return true when the Chrome action is stored as a browser fact.

    Returns:
        True when the Chrome action is stored as a browser fact.

    """
    with sqlite3.connect(f"file:{database_path}?mode=ro", uri=True) as connection:
        browser_event = connection.execute(
            "SELECT json_extract(payload, '$.action') "
            "FROM canonical_events "
            "WHERE session_id=? AND event_type='browser.interacted'",
            (session_id,),
        ).fetchone()
        web_event_count = connection.execute(
            "SELECT count(*) FROM canonical_events WHERE session_id=? AND event_type='web.fetched'",
            (session_id,),
        ).fetchone()
        browser_entry = connection.execute(
            "SELECT json_extract(payload, '$.action') "
            "FROM session_entries "
            "WHERE session_id=? AND entry_type='browser'",
            (session_id,),
        ).fetchone()
    expected_action = ("Navigate to https://example.com",)
    return bool(
        browser_event == expected_action
        and web_event_count == (0,)
        and browser_entry == expected_action,
    )
