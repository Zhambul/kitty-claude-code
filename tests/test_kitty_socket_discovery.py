# Copyright (c) 2026 Zhambyl Yermagambet
"""Check Kitty socket discovery outside the terminal process tree."""

import os
import socket
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from terminal.impl.kitty import remote

PARENT_KITTY_PROCESS_ID = 456


@pytest.fixture
def folders(monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[Path, Path]]:
    """Use separate process and shared temporary folders.

    Yields:
        The two socket search folders.

    """
    # macOS limits Unix socket paths to 104 bytes.
    with TemporaryDirectory(prefix="kitty-test-", dir="/tmp") as folder:
        process = Path(folder) / "process"
        shared = Path(folder) / "shared"
        process.mkdir()
        shared.mkdir()
        monkeypatch.delenv("KITTY_LISTEN_ON", raising=False)
        monkeypatch.setattr(os, "getppid", lambda: 1)
        monkeypatch.setattr(remote, "_socket_directories", lambda: (process, shared))
        yield process, shared


@pytest.mark.parametrize("folder_index", [0, 1])
def test_daemon_finds_socket_in_either_folder(folders: tuple[Path, Path], folder_index: int) -> None:
    """Find Kitty without an inherited address or a Kitty parent."""
    path = folders[folder_index] / "kitty-123"
    with socket.socket(socket.AF_UNIX) as listener:
        listener.bind(str(path))
        assert remote.resolve_listen_on() == f"unix:{path}"


def test_daemon_does_not_choose_between_instances(folders: tuple[Path, Path]) -> None:
    """Keep an ambiguous address unset."""
    with socket.socket(socket.AF_UNIX) as first, socket.socket(socket.AF_UNIX) as second:
        first.bind(str(folders[0] / "kitty-123"))
        second.bind(str(folders[1] / "kitty-456"))
        assert not remote.resolve_listen_on()


@pytest.mark.usefixtures("folders")
def test_explicit_address_has_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the address supplied by Kitty or the user."""
    monkeypatch.setenv("KITTY_LISTEN_ON", "unix:/explicit/kitty")
    assert remote.resolve_listen_on() == "unix:/explicit/kitty"


def test_parent_instance_has_priority(folders: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    """Select the parent Kitty even when another instance is available."""
    monkeypatch.setattr(os, "getppid", lambda: PARENT_KITTY_PROCESS_ID)
    path = folders[1] / f"kitty-{PARENT_KITTY_PROCESS_ID}"
    with socket.socket(socket.AF_UNIX) as first, socket.socket(socket.AF_UNIX) as second:
        first.bind(str(folders[0] / "kitty-123"))
        second.bind(str(path))
        assert remote.resolve_listen_on() == f"unix:{path}"
