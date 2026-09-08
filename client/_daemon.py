# Copyright (c) 2026 Zhambyl Yermagambet
# client/_daemon.py — the whole transport, shared by every client here.
#
# `http.client`, not `urllib.request`: measured 43 ms against 50 ms of total
# process lifetime for a hook that does nothing else (the interpreter floor is
# 23 ms), and a POST to a fixed local port needs nothing urllib adds.
#
# A failure never leaves this module. A client that cannot reach the daemon does
# NOTHING — no debug row, no fallback store, no retry — because it must never
# fail the harness or the terminal that launched it, and because the daemon is
# the one interpreter: a delivery it never accepted did not happen. The single
# exception is `lines()`, whose caller reconnects for a living.
from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus, client as http_client
from typing import TYPE_CHECKING, Protocol

from _daemon_exchange import connection, get_exchange, post_exchange, stream_lines

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

# Hooks are local, but a busy workstation can briefly deschedule both the
# harness client and its daemon while many sessions start together. Keep the
# bound finite without dropping canonical events during that startup burst.
TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True, slots=True)
class ConnectionOptions:
    """Define the daemon connection for one request."""

    host: str = ""
    port: int = 0
    timeout: float = TIMEOUT_SECONDS


DEFAULT_CONNECTION_OPTIONS = ConnectionOptions()


class JsonDocument(Protocol):
    def json_bytes(self) -> bytes: ...


def post(
    path: str,
    body: bytes,
    headers: Mapping[str, str] | None = None,
    options: ConnectionOptions = DEFAULT_CONNECTION_OPTIONS,
) -> bytes | None:
    """Post.

    POST exact bytes. The reply bytes on 200, else None — which every caller
        treats as "nothing happened".

    Returns:
        Byte data.

    """
    active_connection = connection(options.host, options.port, options.timeout)
    try:
        response_status, payload = post_exchange(active_connection, path, body, headers)
    except (OSError, http_client.HTTPException, UnicodeError):
        return None
    else:
        return payload if response_status == HTTPStatus.OK else None
    finally:
        active_connection.close()


def post_json(
    path: str,
    document: JsonDocument,
    options: ConnectionOptions = DEFAULT_CONNECTION_OPTIONS,
) -> bytes | None:
    return post(
        path,
        document.json_bytes(),
        options=options,
    )


def get(
    path: str,
    host: str = "",
    port: int = 0,
    timeout: float = TIMEOUT_SECONDS,
) -> bytes | None:
    """GET one resource. Its bytes on 200, else None.

    Returns:
        Byte data.

    """
    active_connection = connection(host, port, timeout)
    try:
        response_status, payload = get_exchange(active_connection, path)
    except (OSError, http_client.HTTPException, UnicodeError):
        return None
    else:
        return payload if response_status == HTTPStatus.OK else None
    finally:
        active_connection.close()


def lines(path: str, host: str, port: int, timeout: float) -> Iterator[str]:
    """Return the lines.

    The decoded lines of one streaming GET.

        Raises OSError to its caller: a stream client's reconnect loop is the one
        place a failure is not silence, because reconnecting IS its job.

    Yields:
        Decoded response lines.

    Raises:
        OSError: If an operating system operation fails.

    """
    active_connection = connection(host, port, timeout)
    try:
        yield from stream_lines(active_connection, path)
    except http_client.HTTPException as error:
        raise OSError(str(error)) from error
    finally:
        active_connection.close()
