# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the kitty remote-control channel."""

import os
import shutil
import stat
import tempfile
from pathlib import Path

import psutil

from terminal.impl.kitty import remote_client, remote_commands, remote_constants, remote_query, remote_text, remote_tree

GetTextRcPayload = remote_commands.GetTextRcPayload
KittyRcCommand = remote_commands.KittyRcCommand
KittyRcPayload = remote_commands.KittyRcPayload
KittyRcResponse = remote_commands.KittyRcResponse
LsRcPayload = remote_commands.LsRcPayload
SetTabColorRcPayload = remote_commands.SetTabColorRcPayload
KITTEN_QUERY_TIMEOUT_SECONDS = remote_constants.KITTEN_QUERY_TIMEOUT_SECONDS
KITTEN_TIMEOUT_SECONDS = remote_constants.KITTEN_TIMEOUT_SECONDS
KITTY_RC_VERSION = remote_constants.KITTY_RC_VERSION
RC_CMD_DCS = remote_constants.RC_CMD_DCS
RC_CMD_KEY = remote_constants.RC_CMD_KEY
RC_ST = remote_constants.RC_ST
REMOTE_CONTROL_MARKER = remote_constants.REMOTE_CONTROL_MARKER
REMOTE_CONTROL_SOCKET_TIMEOUT_SECONDS = remote_constants.REMOTE_CONTROL_SOCKET_TIMEOUT_SECONDS
SEND_ENTER_DELAY_SECONDS = remote_constants.SEND_ENTER_DELAY_SECONDS
SOCKET_READ_SIZE = remote_constants.SOCKET_READ_SIZE
TAB_COLOR_NONE = remote_constants.TAB_COLOR_NONE
TARGET_OPTION = remote_constants.TARGET_OPTION
WINDOW_ID_VARIABLE = remote_constants.WINDOW_ID_VARIABLE
KittyOSWindow = remote_tree.KittyOSWindow
KittyProcess = remote_tree.KittyProcess
KittyTab = remote_tree.KittyTab
KittyWindowInfo = remote_tree.KittyWindowInfo


def find_kitten() -> str | None:
    """Find the kitten executable.

    Returns:
        The configured path, a PATH match, or the executable in the macOS bundle; None if none is available.

    """
    kitten_path = os.environ.get("KITTY_KITTEN_BIN")
    if kitten_path:
        return kitten_path
    kitten_path = shutil.which("kitten")
    if kitten_path:
        return kitten_path
    bundle = "/Applications/kitty.app/Contents/MacOS/kitten"
    return bundle if os.access(bundle, os.X_OK) else None


def _is_socket(path: str) -> bool:
    try:
        return stat.S_ISSOCK(Path(path).stat().st_mode)
    except OSError:
        return False


def _socket_directories() -> tuple[Path, ...]:
    """Check the process temporary folder and Kitty's shared temporary folder.

    Returns:
        The resolved folders in search order, without duplicates.

    """
    directories = (
        Path(tempfile.gettempdir()).resolve(),
        Path("/tmp").resolve(),  # noqa: S108 -- Find existing Kitty sockets; do not create temporary files.
    )
    return tuple(dict.fromkeys(directories))


def resolve_listen_on() -> str:
    """Resolve the kitty remote-control socket address.

    Returns:
        The configured address, an ancestor's socket, or the only available socket; otherwise empty text.

    """
    if os.environ.get("KITTY_LISTEN_ON"):
        return os.environ["KITTY_LISTEN_ON"]
    directories = _socket_directories()
    process_id = os.getppid()
    while process_id > 1:
        for directory in directories:
            socket_path = directory / f"kitty-{process_id}"
            if _is_socket(str(socket_path)):
                return f"unix:{socket_path}"
        try:
            process_id = psutil.Process(process_id).ppid()
        except (psutil.Error, ValueError, OSError):
            break
    sockets = [
        path
        for folder in directories
        for path in folder.glob("kitty-*")
        if _is_socket(str(path))
    ]
    return f"unix:{sockets[0]}" if len(sockets) == 1 else ""


def current_window_id() -> str:
    """Return the current kitty window identifier.

    Returns:
        The current kitty window identifier.

    """
    return os.environ.get(WINDOW_ID_VARIABLE, "")


class KittyRemote(
    remote_client.KittyClientOperations, remote_text.KittyTextOperations, remote_query.KittyQueryOperations,
):
    """Provide one kitty remote-control channel."""

    def __init__(self, listen: str | None = None, kitten: str | None = None) -> None:
        """Initialize the object."""
        self._pinned_listen = listen
        self.kitten: str | None = find_kitten() if kitten is None else kitten

    @property
    def listen(self) -> str:
        """The remote-control socket address."""
        if self._pinned_listen is not None:
            return self._pinned_listen
        return resolve_listen_on()
