# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify PTY window lifecycle and process cleanup."""

from __future__ import annotations

import sys
import time
from contextlib import ExitStack
from typing import TYPE_CHECKING

from terminal.impl.pty.plugin import pty_plugin
from terminal.impl.pty.registry import PtyWindows
from terminal.models.tabs import TabCloseRequest, TabOpenRequest, TabRenameRequest
from terminal.models.viewport import ScreenReadRequest
from tests import terminal_pty_fixture as pty_fixture, terminal_pty_waits as pty_waits

if TYPE_CHECKING:
    from pathlib import Path

pytest_plugins = ("tests.terminal_pty_fixture",)


def test_window_identity_does_not_repeat() -> None:
    """Verify window identity does not repeat after terminal restart."""
    first = pty_plugin(PtyWindows())
    second = pty_plugin(PtyWindows())
    first_window = first.tabs.open_tab(TabOpenRequest(pty_fixture.TEST_WORKING_DIRECTORY, pty_fixture.CAT_COMMAND, ""))
    second_window = second.tabs.open_tab(
        TabOpenRequest(pty_fixture.TEST_WORKING_DIRECTORY, pty_fixture.CAT_COMMAND, ""),
    )
    with ExitStack() as cleanup:
        if first_window.window_id is not None:
            cleanup.callback(first.tabs.close_tab, TabCloseRequest(first_window.window_id))
        if second_window.window_id is not None:
            cleanup.callback(second.tabs.close_tab, TabCloseRequest(second_window.window_id))
        assert first_window.succeeded
        assert first_window.window_id
        assert second_window.succeeded
        assert second_window.window_id
        assert first_window.window_id != second_window.window_id


def test_terminal_lifecycle_closes_every_owned() -> None:
    """Verify terminal lifecycle closes every owned window."""
    plugin = pty_plugin(PtyWindows())
    first = plugin.tabs.open_tab(TabOpenRequest(pty_fixture.TEST_WORKING_DIRECTORY, pty_fixture.CAT_COMMAND, ""))
    second = plugin.tabs.open_tab(TabOpenRequest(pty_fixture.TEST_WORKING_DIRECTORY, pty_fixture.CAT_COMMAND, ""))
    assert first.succeeded
    assert second.succeeded
    plugin.close()
    assert not plugin.metadata.windows()


def test_headless_tab_rename_is_completed_noop(terminal: pty_fixture.PtyFixture) -> None:
    """Verify a headless tab rename is a completed no-op."""
    plugin, _ = terminal
    window_id = pty_fixture.open_terminal(terminal, pty_fixture.CAT_COMMAND)
    response = plugin.tabs.rename_tab(TabRenameRequest(window_id, "New title"))
    assert response.succeeded
    assert response.reason is None


def test_headless_terminal_publishes_its_terminal(terminal: pty_fixture.PtyFixture) -> None:
    """Verify headless terminal publishes its terminal type."""
    window_id = pty_fixture.open_terminal(
        terminal,
        (sys.executable, pty_fixture.PYTHON_COMMAND_OPTION, "import os; print(os.environ['TERM'])"),
    )
    screen = pty_fixture.await_screen(terminal[0], window_id, "xterm-256color")
    assert "xterm-256color" in screen


def test_window_close_kills_tool_that_escaped(terminal: pty_fixture.PtyFixture, tmp_path: Path) -> None:
    """Verify window close kills a tool in a separate process session."""
    plugin, _ = terminal
    child_pid_path = tmp_path / "escaped-child.pid"
    window_id = pty_fixture.open_terminal(
        terminal,
        (
            sys.executable,
            pty_fixture.PYTHON_COMMAND_OPTION,
            (
                "import pathlib, subprocess, time; "
                "child = subprocess.Popen(['/bin/sleep', '30'], start_new_session=True); "
                f"pathlib.Path({str(child_pid_path)!r}).write_text(str(child.pid)); "
                "time.sleep(30)"
            ),
        ),
    )
    deadline = time.monotonic() + pty_fixture.TIMEOUT_SECONDS
    while not child_pid_path.exists() and time.monotonic() < deadline:
        time.sleep(pty_fixture.POLL_SECONDS)
    assert child_pid_path.exists()
    child_pid = int(child_pid_path.read_text())
    assert plugin.tabs.close_tab(TabCloseRequest(window_id)).succeeded
    pty_waits.wait_for_process_exit(child_pid)


def test_window_close_kills_observed_tool(terminal: pty_fixture.PtyFixture, tmp_path: Path) -> None:
    """Verify window close kills an observed tool after its parent exits."""
    plugin = terminal[0]
    child_pid_path = tmp_path / "orphaned-child.pid"
    release_path = tmp_path / "release-parent"
    window_id = pty_fixture.open_terminal(
        terminal,
        (
            sys.executable,
            pty_fixture.PYTHON_COMMAND_OPTION,
            (
                "import pathlib, subprocess, time; "
                "child = subprocess.Popen(['/bin/sleep', '30'], start_new_session=True); "
                f"pathlib.Path({str(child_pid_path)!r}).write_text(str(child.pid)); "
                f"release = pathlib.Path({str(release_path)!r}); "
                "\nwhile not release.exists(): time.sleep(0.05)"
            ),
        ),
    )
    child_pid = pty_waits.wait_for_process_id(child_pid_path)
    assert pty_waits.window_has_process(plugin, child_pid)
    release_path.write_text("release\n")
    pty_waits.wait_for_no_windows(plugin)
    assert plugin.tabs.close_tab(TabCloseRequest(window_id)).succeeded
    pty_waits.wait_for_process_exit(child_pid)


def test_what_a_pty_does_not_have_it_says_so(terminal: pty_fixture.PtyFixture) -> None:
    """Verify unsupported terminal chrome is not reported as available."""
    plugin, _ = terminal
    window_id = pty_fixture.open_terminal(terminal, pty_fixture.CAT_COMMAND)
    assert not plugin.viewport.read_screen(ScreenReadRequest(window_id, ansi=True)).succeeded
    assert plugin.metadata.current_window_id() is None
    window = plugin.metadata.windows()[0]
    assert window.window_id == window_id
    assert window.is_first_in_tab
    assert not window.tab_is_focused
