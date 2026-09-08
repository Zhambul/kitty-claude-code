# Copyright (c) 2026 Zhambyl Yermagambet
"""The terminal that isn't there.

A concrete `TerminalPlugin` whose every operation returns its failure-shaped
response and whose one read returns nothing. Bootstrap wires it when `resolve()`
finds no terminal, so every service above stays unconditional — nothing has to
ask whether a terminal exists, and "no terminal" reads out of the audit as a
reason string like any other failure.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from terminal.contract import (
    TerminalInput,
    TerminalMetadata,
    TerminalPanes,
    TerminalPlugin,
    TerminalTabs,
    TerminalViewport,
)
from terminal.models.input import (
    KeySendRequest,
    KeySendResponse,
    TextInsertRequest,
    TextInsertResponse,
    TextSubmitRequest,
    TextSubmitResponse,
)
from terminal.models.metadata import WindowTagRequest, WindowTagResponse
from terminal.models.pane_results import (
    PaneCloseResponse,
    PaneOpenResponse,
    PaneResizeResponse,
    WindowFocusResponse,
)
from terminal.models.tab_results import (
    TabCloseResponse,
    TabColorClearResponse,
    TabColorSetResponse,
    TabOpenResponse,
    TabRenameResponse,
)
from terminal.models.viewport import ScreenReadRequest, ScreenReadResponse

if TYPE_CHECKING:
    from terminal.models.panes import (
        PaneCloseRequest,
        PaneOpenRequest,
        PaneResizeRequest,
        WindowFocusRequest,
    )
    from terminal.models.tabs import (
        TabCloseRequest,
        TabColorClearRequest,
        TabColorSetRequest,
        TabOpenRequest,
        TabRenameRequest,
    )
    from terminal.models.values import WindowId, WindowInfo

NO_TERMINAL = "no terminal available"


class NullTabs(TerminalTabs):
    """Represent null tabs."""

    @override
    def open_tab(self, tab_open_request: TabOpenRequest) -> TabOpenResponse:
        """Open tab.

        Returns:
            The tab open response.

        """
        return TabOpenResponse(succeeded=False, window_id=None, reason=NO_TERMINAL)

    @override
    def close_tab(self, tab_close_request: TabCloseRequest) -> TabCloseResponse:
        """Close tab.

        Returns:
            The tab close response.

        """
        return TabCloseResponse(succeeded=False, reason=NO_TERMINAL)

    @override
    def rename_tab(self, tab_rename_request: TabRenameRequest) -> TabRenameResponse:
        """Rename tab.

        Returns:
            The tab rename response.

        """
        return TabRenameResponse(succeeded=False, reason=NO_TERMINAL)

    @override
    def set_tab_color(self, tab_color_set_request: TabColorSetRequest) -> TabColorSetResponse:
        """Set tab color.

        Returns:
            The tab color set response.

        """
        return TabColorSetResponse(succeeded=False, reason=NO_TERMINAL)

    @override
    def clear_tab_color(self, tab_color_clear_request: TabColorClearRequest) -> TabColorClearResponse:
        """Clear tab color.

        Returns:
            The tab color clear response.

        """
        return TabColorClearResponse(succeeded=False, reason=NO_TERMINAL)


class NullPanes(TerminalPanes):
    """Represent null panes."""

    @override
    def open_pane(self, pane_open_request: PaneOpenRequest) -> PaneOpenResponse:
        """Open pane.

        Returns:
            The pane open response.

        """
        return PaneOpenResponse(succeeded=False, window_id=None, reason=NO_TERMINAL)

    @override
    def close_pane(self, pane_close_request: PaneCloseRequest) -> PaneCloseResponse:
        """Close pane.

        Returns:
            The pane close response.

        """
        return PaneCloseResponse(succeeded=False, reason=NO_TERMINAL)

    @override
    def resize_pane(self, pane_resize_request: PaneResizeRequest) -> PaneResizeResponse:
        """Return the resize pane.

        Returns:
            Resize pane.

        """
        return PaneResizeResponse(succeeded=False, reason=NO_TERMINAL)

    @override
    def focus_window(self, window_focus_request: WindowFocusRequest) -> WindowFocusResponse:
        """Return the focus window.

        Returns:
            Focus window.

        """
        return WindowFocusResponse(succeeded=False, reason=NO_TERMINAL)


class NullMetadata(TerminalMetadata):
    """Represent null metadata."""

    @override
    def windows(self) -> tuple[WindowInfo, ...]:
        """Return the windows.

        Returns:
            Windows.

        """
        return ()

    @override
    def tag_window(self, window_tag_request: WindowTagRequest) -> WindowTagResponse:
        """Return the tag window.

        Returns:
            Tag window.

        """
        return WindowTagResponse(succeeded=False, reason=NO_TERMINAL)

    @override
    def current_window_id(self) -> WindowId | None:
        """Return the current window ID.

        Returns:
            Current window ID.

        """


class NullInput(TerminalInput):
    """Represent null input."""

    @override
    def insert_text(self, text_insert_request: TextInsertRequest) -> TextInsertResponse:
        """Return the insert text.

        Returns:
            Insert text.

        """
        return TextInsertResponse(succeeded=False, reason=NO_TERMINAL)

    @override
    def submit_text(self, text_submit_request: TextSubmitRequest) -> TextSubmitResponse:
        """Submit text.

        Returns:
            The text submit response.

        """
        return TextSubmitResponse(succeeded=False, reason=NO_TERMINAL)

    @override
    def send_key(self, key_send_request: KeySendRequest) -> KeySendResponse:
        """Send key.

        Returns:
            The key send response.

        """
        return KeySendResponse(succeeded=False, reason=NO_TERMINAL)


class NullViewport(TerminalViewport):
    """Represent null viewport."""

    @override
    def read_screen(self, screen_read_request: ScreenReadRequest) -> ScreenReadResponse:
        """Return screen.

        Returns:
            Screen.

        """
        return ScreenReadResponse(succeeded=False, text=None, reason=NO_TERMINAL)


def null_plugin() -> TerminalPlugin:
    """Return the null plugin.

    Returns:
        Null plugin.

    """
    return TerminalPlugin(
        name="none",
        tabs=NullTabs(),
        panes=NullPanes(),
        metadata=NullMetadata(),
        input=NullInput(),
        viewport=NullViewport(),
    )


def build_plugin() -> TerminalPlugin:
    """Build the terminal plugin.

    Returns:
        The terminal plugin.

    """
    return null_plugin()
