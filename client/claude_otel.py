#!/usr/bin/env python3
# Copyright (c) 2026 Zhambyl Yermagambet
"""Accept Claude Code's OTLP export and forward it to the daemon.

    claude_otel.py HOST PORT LISTEN_PORT GRACE_SECONDS

Claude Code is configured (the `env` block of ~/.claude/settings.json) to POST
metrics to a local port every couple of seconds; being that port is this
process's only reason to exist. It owns its port, its gzip and its idle timer —
properties of being an OTLP endpoint — and nothing else: what an export MEANS is
decided daemon-side (`harness/impl/claude_code/otel/gateway.py`).

The daemon spawns it and passes every number it needs, so the launcher's
already-listening pre-check and this bind can no longer disagree. An export the
daemon does not accept is dropped in silence; OTLP counters are re-exported on
the next interval, so this is the cheapest raw event in the tree to miss.
"""

from __future__ import annotations

import gzip
import sys
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from types import MappingProxyType
from typing import cast, override

sys.path.insert(0, str(Path(__file__).resolve().parent))  # my own directory

import _daemon
import _http

HARNESS = "claude_code"
DELIVERY_TIMEOUT_SECONDS = 5.0
MAX_REQUEST_WAIT_SECONDS = 30.0
COMMAND_ARGUMENT_COUNT = 4
# Answer Claude Code the same way whatever happens downstream: its exporter is
# not our error channel.
ACKNOWLEDGEMENT = b"{}"
TELEMETRY_HEADERS = MappingProxyType({_http.TELEMETRY_KIND_HEADER: "otlp"})


def deliver(body: bytes, daemon_host: str, daemon_port: int) -> bool:
    """Ship one export. True when the daemon accepted it.

    Returns:
        True when the stated condition is met; otherwise, false.

    """
    if not body:
        return False
    return (
        _daemon.post(
            _http.TELEMETRY_PATH % HARNESS,
            body,
            TELEMETRY_HEADERS,
            _daemon.ConnectionOptions(
                host=daemon_host,
                port=daemon_port,
                timeout=DELIVERY_TIMEOUT_SECONDS,
            ),
        )
        is not None
    )


class TelemetryServer(HTTPServer):
    """Store the delivery target and the idle clock for one receiver."""

    def __init__(self, listen_port: int, daemon_host: str, daemon_port: int) -> None:
        """Initialize the server."""
        super().__init__((_http.HOST, listen_port), Receiver)
        self.daemon_host = daemon_host
        self.daemon_port = daemon_port
        self.last_delivery_at = time.time()

    def deliver(self, body: bytes) -> bool:
        """Send one export to this server's daemon target.

        Returns:
            True when the daemon accepts the export.

        """
        return deliver(body, self.daemon_host, self.daemon_port)


class Receiver(BaseHTTPRequestHandler):
    """Represent receiver."""

    @override
    def log_message(self, _format_string: str, *_arguments: str | float) -> None:
        """Discard an HTTP log message."""

    def do_POST(self) -> None:
        """Return the do post."""
        telemetry_server = cast("TelemetryServer", self.server)
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        if self.headers.get("Content-Encoding") == "gzip":
            body = gzip.decompress(body)
        if telemetry_server.deliver(body):
            telemetry_server.last_delivery_at = time.time()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(ACKNOWLEDGEMENT)))
        self.end_headers()
        self.wfile.write(ACKNOWLEDGEMENT)


def _open_server(listen_port: int, daemon_host: str, daemon_port: int) -> TelemetryServer | None:
    try:
        return TelemetryServer(listen_port, daemon_host, daemon_port)
    except OSError:
        return None


def serve(listen_port: int, grace_seconds: float, daemon_host: str, daemon_port: int) -> None:
    """Serve."""
    server = _open_server(listen_port, daemon_host, daemon_port)
    if server is None:
        return
    with server:
        server.timeout = min(MAX_REQUEST_WAIT_SECONDS, grace_seconds)
        while time.time() - server.last_delivery_at < grace_seconds:
            server.handle_request()


def main(arguments: list[str]) -> None:
    """Run the command.

    Exit the process if the command input is not valid.

    """
    if len(arguments) != COMMAND_ARGUMENT_COUNT:
        message = "usage: claude_otel.py HOST PORT LISTEN_PORT GRACE_SECONDS"
        sys.exit(message)
    daemon_host, daemon_port, listen_port, grace_seconds = arguments
    serve(int(listen_port), float(grace_seconds), daemon_host, int(daemon_port))


if __name__ == "__main__":
    main(sys.argv[1:])
