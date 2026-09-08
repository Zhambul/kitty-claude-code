# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify terminal client architecture and behavior."""

from __future__ import annotations

import socket
import threading
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator

TEXT_ENCODING = "utf-8"


@dataclass
class Delivery:
    """Represent delivery."""

    method: str
    path: str
    headers: dict[str, str]
    body: bytes


class _Capture:
    def __init__(self) -> None:
        self.deliveries: list[Delivery] = []
        self.reply = b"{}"
        # A reply per path fragment, for the clients that read more than one
        # resource: the pane asks for an aggregate and then a page of entries,
        # and one `reply` cannot answer both.
        self.replies: dict[str, bytes] = {}
        self.stream = ""
        self.port = 0

    def delivery(self, path_fragment: str = "") -> Delivery:
        return next(found for found in self.deliveries if path_fragment in found.path)


class CaptureServer(HTTPServer):
    """An HTTP server with its test capture."""

    capture: _Capture


def _stop_capture_server(server: CaptureServer, thread: threading.Thread) -> None:
    """Stop a capture server and wait for its thread."""
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


class _StubHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format_string: str, *arguments: str | float) -> None:
        """Discard the HTTP server access log."""

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length") or 0)
        self._record("POST", self.rfile.read(content_length))
        self._answer(self.capture.reply)

    def do_GET(self) -> None:
        self._record("GET")
        # A stream first: every other path is answered by fragment, and a
        # stream's path is a resource's path with `/stream` on the end.
        if "/stream" not in self.path:
            for fragment, payload in self.capture.replies.items():
                if fragment in self.path:
                    self._answer(payload)
                    return
        if "/stream" in self.path or "/panes/" in self.path:
            frames = self.capture.stream.encode(TEXT_ENCODING)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Content-Length", str(len(frames)))
            self.end_headers()
            self.wfile.write(frames)
            return
        self._answer(self.capture.reply)

    @property
    def capture(self) -> _Capture:
        """Read the server capture.

        Raises:
            TypeError: If the handler is not attached to a capture server.

        """
        if not isinstance(self.server, CaptureServer):
            message = "stub handler requires a capture server"
            raise TypeError(message)
        return self.server.capture

    def _record(self, method: str, body: bytes = b"") -> None:
        self.capture.deliveries.append(
            Delivery(method, self.path, dict(self.headers), body),
        )

    def _answer(self, payload: bytes) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


@pytest.fixture
def daemon() -> Iterator[_Capture]:
    """Run a test daemon on a free port until the test ends.

    Yields:
        The request recorder with the daemon's assigned port.

    """
    capture = _Capture()
    server = CaptureServer(("127.0.0.1", 0), _StubHandler)
    server.capture = capture
    capture.port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield capture
    finally:
        _stop_capture_server(server, thread)


def free_port() -> int:
    """Ask the operating system for an unused local TCP port.

    Returns:
        The port number, released when the temporary socket closes.

    """
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]
