# Copyright (c) 2026 Zhambyl Yermagambet
"""Check parent-process socket discovery without querying live processes."""

from pathlib import Path
from unittest.mock import Mock

import psutil
import pytest

from terminal.impl.kitty import remote

PARENT_PROCESS_ID = 789
KITTY_PROCESS_ID = 456


@pytest.fixture
def parent_query(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Mock:
    """Set up a controlled parent query and an empty socket directory.

    Returns:
        The mock process constructor.

    """
    monkeypatch.delenv("KITTY_LISTEN_ON", raising=False)
    monkeypatch.setattr("terminal.impl.kitty.remote.os.getppid", lambda: PARENT_PROCESS_ID)
    monkeypatch.setattr(remote, "_socket_directories", lambda: (tmp_path,))
    query = Mock()
    query.return_value.ppid.return_value = KITTY_PROCESS_ID
    monkeypatch.setattr("terminal.impl.kitty.remote.psutil.Process", query)
    return query


def test_socket_lookup_follows_parent(
    parent_query: Mock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Find the ancestor socket through the process library."""
    socket_path = str(tmp_path / f"kitty-{KITTY_PROCESS_ID}")
    monkeypatch.setattr(remote, "_is_socket", lambda path: path == socket_path)
    assert remote.resolve_listen_on() == f"unix:{socket_path}"
    parent_query.assert_called_once_with(PARENT_PROCESS_ID)
    parent_query.return_value.ppid.assert_called_once_with()


@pytest.mark.parametrize("error", [psutil.NoSuchProcess(PARENT_PROCESS_ID), psutil.AccessDenied(PARENT_PROCESS_ID)])
def test_socket_lookup_handles_missing_parent(parent_query: Mock, error: psutil.Error) -> None:
    """Stop the ancestor walk if a parent exits or cannot be read."""
    parent_query.side_effect = error
    assert not remote.resolve_listen_on()
    parent_query.assert_called_once_with(PARENT_PROCESS_ID)
