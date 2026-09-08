# Copyright (c) 2026 Zhambyl Yermagambet
"""Terminal drivers for Claude question-dialog tests."""

from domain.ids import WindowId


class ClippedCursorDriver:
    """Show successive clipped views as the cursor moves."""

    def __init__(self) -> None:
        """Initialize the driver."""
        self.state = 0
        self.read_requests: list[tuple[WindowId, str, bool]] = []
        self.key_windows: list[WindowId] = []
        self.key_sequences: list[tuple[str, ...]] = []

    def read_text(
        self,
        window_id: WindowId,
        extent: str = "screen",
        *,
        ansi: bool = False,
    ) -> str:
        """Return the current clipped view.

        Returns:
            The current screen text.

        """
        self.read_requests.append((window_id, extent, ansi))
        if self.state == 0:
            return "  2. Green\n  3. Red\nEnter to select"
        if self.state == 1:
            return "\u276f 2. Green\n  3. Red\nEnter to select"
        return "\u276f 1. Blue\n  2. Green\nEnter to select"

    def send_key(self, window_id: WindowId, *keys: str) -> bool:
        """Record a key and move the simulated cursor.

        Returns:
            True after the driver accepts the key.

        """
        self.key_windows.append(window_id)
        self.key_sequences.append(keys)
        key = keys[0]
        if self.state == 0 and key == "down":
            self.state = 1
        elif self.state == 1 and key == "up":
            self.state = 2
        return True


class FrozenCursorDriver:
    """Keep the screen fixed while it records navigation keys."""

    def __init__(self) -> None:
        """Initialize the driver."""
        self.keys: list[str] = []
        self.read_requests: list[tuple[WindowId, str, bool]] = []

    def read_text(
        self,
        window_id: WindowId,
        extent: str = "screen",
        *,
        ansi: bool = False,
    ) -> str:
        """Return the fixed screen.

        Returns:
            The fixed screen text.

        """
        self.read_requests.append((window_id, extent, ansi))
        return "  1. Blue\n  2. Green\nEnter to select"

    def send_key(self, window_id: WindowId, *keys: str) -> bool:
        """Record the attempted navigation.

        Returns:
            True after the driver accepts the keys.

        """
        self.last_window_id = window_id
        self.keys.extend(keys)
        return True


class ResizeDriver:
    """Record temporary viewport changes for a question dialog."""

    def __init__(self) -> None:
        """Initialize the driver."""
        self.resizes: list[int] = []
        self._line_windows: list[WindowId] = []
        self._read_requests: list[tuple[WindowId, str, bool]] = []
        self._key_windows: list[WindowId] = []
        self._key_sequences: list[tuple[str, ...]] = []
        self._paste_requests: list[tuple[WindowId, str]] = []

    def lines(self, window_id: WindowId) -> int:
        """Return the original viewport height.

        Returns:
            The original viewport height.

        """
        self._line_windows.append(window_id)
        return 24

    def resize_lines(self, window_id: WindowId, cells: int) -> bool:
        """Record a viewport size change.

        Returns:
            True after the driver accepts the size change.

        """
        self.last_resize_window = window_id
        self.resizes.append(cells)
        return True

    def read_text(
        self,
        window_id: WindowId,
        extent: str = "screen",
        *,
        ansi: bool = False,
    ) -> str:
        """Return an empty dialog screen.

        Returns:
            Empty screen text.

        """
        self._read_requests.append((window_id, extent, ansi))
        return ""

    def send_key(self, window_id: WindowId, *keys: str) -> bool:
        """Record accepted keys.

        Returns:
            True after the driver accepts the keys.

        """
        self._key_windows.append(window_id)
        self._key_sequences.append(keys)
        return True

    def paste_text(self, window_id: WindowId, text: str) -> bool:
        """Record accepted text.

        Returns:
            True after the driver accepts the text.

        """
        self._paste_requests.append((window_id, text))
        return True
