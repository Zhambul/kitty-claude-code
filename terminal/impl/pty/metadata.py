# Copyright (c) 2026 Zhambyl Yermagambet
"""Read metadata from live PTY windows."""

from contextlib import suppress
from typing import override

import psutil

from terminal.contract import TerminalMetadata
from terminal.impl.pty.registry import PtyWindows
from terminal.impl.pty.window import PtyWindow
from terminal.models.metadata import WindowTagRequest, WindowTagResponse
from terminal.models.values import TabId, WindowId, WindowInfo, WindowProcess

NO_WINDOW = "no such pty window"
NO_CURRENT_WINDOW: WindowId | None = None


class PtyMetadata(TerminalMetadata):
    """Read PTY window metadata."""

    def __init__(self, pty_windows: PtyWindows) -> None:
        """Initialize PTY metadata operations."""
        self.pty_windows = pty_windows

    def windows(self) -> tuple[WindowInfo, ...]:
        """Return all live PTY windows.

        Returns:
            Live PTY window information.

        """
        with self.pty_windows.lock:
            return tuple(
                WindowInfo(
                    window_id=window.window_id,
                    tab_id=TabId(str(window.window_id)),
                    tags=window.tags,
                    columns=window.screen.columns,
                    lines=window.screen.lines,
                    is_first_in_tab=True,
                    tab_is_active=True,
                    tab_is_focused=False,
                    is_active_in_tab=True,
                    processes=window_processes(window),
                )
                for window in self.pty_windows.windows.values()
                if window.process.poll() is None
            )

    def tag_window(self, window_tag_request: WindowTagRequest) -> WindowTagResponse:
        """Add tags to one PTY window.

        Returns:
            The tag command result.

        """
        with self.pty_windows.lock:
            window = self.pty_windows.get(window_tag_request.window_id)
            if window is None:
                return WindowTagResponse(succeeded=False, reason=NO_WINDOW)
            window.tags.update(window_tag_request.tags)
        return WindowTagResponse(succeeded=True)

    @override
    def current_window_id(self) -> WindowId | None:
        """Return no current window for a headless PTY owner.

        Returns:
            Always ``None``.

        """
        return NO_CURRENT_WINDOW


def window_processes(pty_window: PtyWindow) -> tuple[WindowProcess, ...]:
    """Return the wrapper and all live descendant processes.

    Returns:
        The observed window processes.

    """
    try:
        process_tree = _process_tree(pty_window)
    except (psutil.Error, OSError, SystemError):
        return (WindowProcess(pty_window.process.pid, pty_window.command),)
    reported_processes: list[WindowProcess] = []
    for process in process_tree:
        with suppress(psutil.Error, OSError, SystemError):
            reported_processes.append(
                WindowProcess(process.pid, tuple(process.cmdline())),
            )
    return tuple(reported_processes) or (WindowProcess(pty_window.process.pid, pty_window.command),)


def _process_tree(pty_window: PtyWindow) -> tuple[psutil.Process, ...]:
    root_process = psutil.Process(pty_window.process.pid)
    descendants = (
        pty_window.observe_descendants()
        if isinstance(pty_window, PtyWindow)
        else tuple(root_process.children(recursive=True))
    )
    return (root_process, *descendants)
