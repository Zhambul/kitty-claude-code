# Copyright (c) 2026 Zhambyl Yermagambet
"""Reference fixtures for real-terminal E2E cases."""

from __future__ import annotations

import pytest

from tests.e2e.testkit import references as refs, status_colors, terminal_models


@pytest.fixture
def terminal_color_reader() -> status_colors.KittyTabColorReader:
    """Return the real Kitty tab color reader.

    Returns:
        The real Kitty tab color reader.

    """
    return status_colors.KittyTabColorReader()


@pytest.fixture
def terminal_pane_geometries() -> refs.References[terminal_models.PaneGeometry]:
    """Return pane geometry references.

    Returns:
        Pane geometry references.

    """
    return refs.References("terminal pane geometry")


@pytest.fixture
def terminal_focuses() -> refs.References[terminal_models.TerminalFocus]:
    """Return terminal focus references.

    Returns:
        Terminal focus references.

    """
    return refs.References("terminal focus")
