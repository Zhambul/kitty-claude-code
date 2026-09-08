# Copyright (c) 2026 Zhambyl Yermagambet
"""Read the real color overrides that Kitty applied to one session tab."""

from __future__ import annotations

import json
import time
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

from sdk.client import wait_for
from terminal.impl.kitty.remote import KittyRemote
from terminal.models.values import WindowId

if TYPE_CHECKING:
    from terminal.models.values import RGB, TabAppearance

COLOR_KITTEN = Path(__file__).resolve().parents[1] / "real_terminal" / "read_tab_colors.py"
RED_COMPONENT_SHIFT = 16


def _rgb_integer(color: RGB) -> int:
    return (color.red << RED_COMPONENT_SHIFT) | (color.green << 8) | color.blue


def _appearance_values(appearance: TabAppearance) -> dict[str, int]:
    return {
        "active_bg": _rgb_integer(appearance.active_background),
        "active_fg": _rgb_integer(appearance.active_foreground),
        "inactive_bg": _rgb_integer(appearance.inactive_background),
        "inactive_fg": _rgb_integer(appearance.inactive_foreground),
    }


class KittyTabColorReader:
    """A read-only E2E probe for Kitty's stored tab color overrides."""

    def __init__(self, remote: KittyRemote | None = None) -> None:
        """Initialize the object."""
        self._remote = remote or KittyRemote()

    def wait_for(self, window_id: str, expected: TabAppearance, timeout: float) -> None:
        """Process wait for."""
        wanted = _appearance_values(expected)
        wait_for(
            f"Kitty tab {window_id!r} to have colors {wanted}",
            partial(self._matches, WindowId(window_id), wanted),
            timeout=timeout,
        )

    def assert_not_seen_for(
        self,
        window_id: str,
        unexpected: TabAppearance,
        duration: float,
    ) -> None:
        """Check that Kitty does not use the unexpected colors during the interval.

        Raises:
            AssertionError: If an observation matches the unexpected colors.

        """
        unwanted = _appearance_values(unexpected)
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            found = self._read(WindowId(window_id))
            if found == unwanted:
                message = f"Kitty tab {window_id!r} used unexpected colors {unwanted}"
                raise AssertionError(
                    message,
                )
            time.sleep(0.1)

    def _matches(self, window_id: WindowId, wanted: dict[str, int]) -> bool | None:
        found = self._read(window_id)
        return True if found == wanted else None

    def _read(self, window_id: WindowId) -> dict[str, int | None] | None:
        output = self._remote.capture(
            "kitten",
            "--match",
            f"id:{window_id}",
            str(COLOR_KITTEN),
        )
        if output is None:
            return None
        color_document = json.loads(output)
        if not isinstance(color_document, dict):
            return None
        return {
            name: color_value if isinstance(color_value, int) else None
            for name, color_value in color_document.items()
            if isinstance(name, str)
        }
