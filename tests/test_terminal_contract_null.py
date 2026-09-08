# Copyright (c) 2026 Zhambyl Yermagambet
"""Tests for the terminal that is not present."""

from __future__ import annotations

from terminal.impl.null import null_plugin
from terminal.models.input import TextInputMode, TextInsertRequest, TextSubmitRequest
from terminal.models.metadata import WindowTagRequest
from terminal.models.tabs import TabOpenRequest
from terminal.models.values import WindowId
from terminal.models.viewport import ScreenReadRequest


def test_null_terminal_responses() -> None:
    """Verify a missing terminal returns failed responses."""
    plugin = null_plugin()
    missing_window_id = WindowId("1")
    responses = (
        plugin.tabs.open_tab(TabOpenRequest("/work", ("claude",), "")),
        plugin.metadata.tag_window(WindowTagRequest(missing_window_id, {})),
        plugin.input.insert_text(TextInsertRequest(missing_window_id, "draft", TextInputMode.PASTE)),
        plugin.input.submit_text(TextSubmitRequest(missing_window_id, "hello", TextInputMode.PASTE)),
        plugin.viewport.read_screen(ScreenReadRequest(missing_window_id)),
    )
    assert [response.succeeded for response in responses] == [False, False, False, False, False]
    assert all(response.reason for response in responses)
    assert not plugin.metadata.windows()
    assert plugin.metadata.current_window_id() is None
