# Copyright (c) 2026 Zhambyl Yermagambet
"""Check input formats without coupling the watcher to a database name."""

from contextlib import closing
from threading import Event

import pytest
from watchdog.events import FileModifiedEvent

from core.input_events import InputEvents


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/profile/state.sqlite", True),
        ("/profile/state.sqlite-wal", True),
        ("/profile/state_5.sqlite", True),
        ("/profile/state_5.sqlite-wal", True),
        ("/profile/session.jsonl", True),
        ("/profile/tasks/item.json", True),
        ("/profile/teams/item.json", True),
        ("/profile/settings.json", False),
        ("/profile/debug.log", False),
    ],
)
def test_input_filter(path: str, *, expected: bool) -> None:
    """Signal source formats, but ignore unrelated profile writes."""
    changed = Event()
    watcher = InputEvents(changed.set, ())
    watcher.start()
    with closing(watcher):
        watcher.on_any_event(FileModifiedEvent(path))
        assert changed.is_set() is expected
