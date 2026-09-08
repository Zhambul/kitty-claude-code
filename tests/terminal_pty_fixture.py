# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide a real headless PTY fixture for terminal tests."""

from __future__ import annotations

import tempfile
import time
from typing import TYPE_CHECKING

import pytest

from terminal.contract import TerminalPlugin
from terminal.impl.pty.plugin import pty_plugin
from terminal.impl.pty.registry import PtyWindows
from terminal.models.tabs import TabCloseRequest, TabOpenRequest
from terminal.models.values import WindowId
from terminal.models.viewport import ScreenReadRequest

if TYPE_CHECKING:
    from collections.abc import Iterator

TIMEOUT_SECONDS = 10.0
POLL_SECONDS = 0.05
TEST_WORKING_DIRECTORY = tempfile.gettempdir()
CAT_COMMAND = ("/bin/cat",)
PYTHON_COMMAND_OPTION = "-c"
type PtyFixture = tuple[TerminalPlugin, list[WindowId]]


@pytest.fixture
def terminal() -> Iterator[PtyFixture]:
    """Create a PTY plugin and close its registered windows after the test.

    Yields:
        The plugin and the list of opened window identities.

    """
    plugin = pty_plugin(PtyWindows())
    opened: list[WindowId] = []
    yield plugin, opened
    for window_id in opened:
        plugin.tabs.close_tab(TabCloseRequest(window_id))


def open_terminal(terminal: PtyFixture, command: tuple[str, ...]) -> WindowId:
    """Open one command window and register it for fixture cleanup.

    Returns:
        The identity of the new window.

    """
    plugin, opened = terminal
    response = plugin.tabs.open_tab(TabOpenRequest(TEST_WORKING_DIRECTORY, command, ""))
    assert response.succeeded, response.reason
    assert response.window_id, response.reason
    opened.append(response.window_id)
    return response.window_id


def await_screen(plugin: TerminalPlugin, window_id: WindowId, contains: str) -> str:
    """Return visible screen text after it contains the expected string.

    Returns:
        Visible screen text after it contains the expected string.

    Raises:
        AssertionError: If the screen does not show the expected text before the timeout.

    """
    deadline = time.monotonic() + TIMEOUT_SECONDS
    while True:
        screen = plugin.viewport.read_screen(ScreenReadRequest(window_id))
        assert screen.succeeded, screen.reason
        if contains in (screen.text or ""):
            return screen.text or ""
        if time.monotonic() >= deadline:
            msg = f"never showed {contains!r}; screen reads:\n{screen.text}"
            raise AssertionError(msg)
        time.sleep(POLL_SECONDS)
