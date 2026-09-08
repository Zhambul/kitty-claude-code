# Copyright (c) 2026 Zhambyl Yermagambet
"""Tests for terminal window metadata."""

from __future__ import annotations

from terminal.impl.kitty.plugin import kitty_plugin
from terminal.models.values import ACTIVITY_PANE_TAG, WindowInfo
from tests.terminal_contract_data import last_good_tree, window_tree
from tests.terminal_contract_remote import FakeRemote, SocketRemote


def test_window_tree_rows() -> None:
    """Verify a kitty tree becomes terminal-neutral rows."""
    remote = FakeRemote(tree=window_tree())

    windows = kitty_plugin(remote).metadata.windows()

    first, second = windows
    assert [found.window_id for found in windows] == ["7", "8"]
    assert [found.is_first_in_tab for found in windows] == [True, False]
    assert first.tab_id == "3"
    assert first.tab_is_focused
    assert_window_details(first, second)


def assert_window_details(first: WindowInfo, second: WindowInfo) -> None:
    """Verify flattened window details."""
    assert first.is_active_in_tab
    assert not second.is_active_in_tab
    assert second.tags == {ACTIVITY_PANE_TAG: "session-one"}
    assert (first.columns, first.lines) == (75, 40)


def test_window_tree_uses_socket_without_kitten() -> None:
    """Verify the window tree uses the socket without a kitten process."""
    remote = SocketRemote()

    windows = kitty_plugin(remote).metadata.windows()

    assert [window.window_id for window in windows] == ["7"]
    assert remote.raw_calls[0][0] == "ls"


def test_failed_listing_uses_last_good() -> None:
    """Verify a failed query does not remove known windows."""
    remote = FakeRemote(tree=last_good_tree())
    metadata = kitty_plugin(remote).metadata

    first = metadata.windows()
    assert [found.window_id for found in first] == ["7"]
    remote.tree = None
    assert metadata.windows() == first
    remote.tree = []
    assert not metadata.windows()
