# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide kitty raw socket operations."""

import socket
from typing import Protocol

from terminal.impl.kitty.remote_commands import KittyRcCommand, KittyRcPayload, KittyRcResponse
from terminal.impl.kitty.remote_constants import (
    KITTY_RC_VERSION,
    RC_CMD_DCS,
    RC_CMD_KEY,
    RC_ST,
    REMOTE_CONTROL_SOCKET_TIMEOUT_SECONDS,
    SOCKET_READ_SIZE,
)


class _KittySocketClient(Protocol):
    @property
    def listen(self) -> str:
        """The remote-control socket address."""


def _validated_socket_reply(
    path: str,
    kitty_rc_command: KittyRcCommand,
    *,
    want_response: bool,
    timeout: float,
) -> KittyRcResponse | bool | None:
    reply = _socket_reply(path, kitty_rc_command, want_response=want_response, timeout=timeout)
    if not isinstance(reply, bytes):
        return reply
    return KittyRcResponse.model_validate_json(reply)


def _socket_reply(
    path: str,
    kitty_rc_command: KittyRcCommand,
    *,
    want_response: bool,
    timeout: float,
) -> bytes | bool | None:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as remote_socket:
        remote_socket.settimeout(timeout)
        remote_socket.connect(path)
        remote_socket.sendall(RC_CMD_DCS + kitty_rc_command.model_dump_json().encode("utf-8") + RC_ST)
        if not want_response:
            return True
        response_buffer = _receive_response(remote_socket)
    if response_buffer is None:
        return None
    return _response_payload(response_buffer)


def _receive_response(remote_socket: socket.socket) -> bytes | None:
    response_buffer = b""
    while RC_ST not in response_buffer:
        response_chunk = remote_socket.recv(SOCKET_READ_SIZE)
        if not response_chunk:
            return None
        response_buffer += response_chunk
    return response_buffer


def _response_payload(response_buffer: bytes) -> bytes:
    payload_start = response_buffer.index(RC_CMD_KEY) + len(RC_CMD_KEY)
    payload_end = response_buffer.index(RC_ST)
    return response_buffer[payload_start:payload_end]


class KittySocketOperations:
    """Provide raw kitty socket operations."""

    def raw(
        self: _KittySocketClient,
        command_name: str,
        payload: KittyRcPayload,
        *,
        want_response: bool = False,
        timeout: float = REMOTE_CONTROL_SOCKET_TIMEOUT_SECONDS,
    ) -> KittyRcResponse | bool | None:
        """Run a raw socket command.

        Returns:
            The decoded response, True after a send without a response, or None
            if the socket or response is not valid.

        """
        path = self.listen.removeprefix("unix:")
        if not path:
            return None
        command = KittyRcCommand(
            cmd=command_name,
            version=KITTY_RC_VERSION,
            no_response=not want_response,
            payload=payload,
        )
        try:
            return _validated_socket_reply(path, command, want_response=want_response, timeout=timeout)
        except (OSError, ValueError):
            return None
