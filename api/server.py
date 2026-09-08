# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the server module."""

# The HTTP server for an application that already owns a bound socket and a
# provider graph. api.runtime owns configuration and the port bind. The
# application's lifespan owns all background work.
from __future__ import annotations

import contextlib
import signal
from typing import TYPE_CHECKING

import uvicorn

from api import dependencies
from api.app import build_web_application
from app import injection, provider_audit_storage
from audit.documents import PortAudit

if TYPE_CHECKING:
    import socket
    from types import FrameType

    from fastapi import FastAPI


def build_server(web_application: FastAPI, graceful_shutdown_seconds: int = 3) -> uvicorn.Server:
    """Build server.

    One uvicorn server for an already-bound socket (passed to run()).
        Shared with the HTTP test fixture so the tests exercise the daemon's real
        engine configuration, not a lookalike.

    Returns:
        The server.

    """
    return uvicorn.Server(
        uvicorn.Config(
            web_application,
            # The graceful path waits for open connections, and the SSE
            # streams never close on their own — force-close after the grace.
            timeout_graceful_shutdown=graceful_shutdown_seconds,
            lifespan="on",
            access_log=False,
            log_level="warning",
        ),
    )


def _bound_port_source(bound_socket: socket.socket) -> tuple[int, str]:
    host, port = bound_socket.getsockname()[:2]
    return int(port), f"http://{host}:{port}"


def _run_uvicorn(server: uvicorn.Server, bound_socket: socket.socket) -> None:
    try:
        server.run(sockets=[bound_socket])
    except KeyboardInterrupt:
        return
    finally:
        with contextlib.suppress(OSError):
            bound_socket.close()


def _absorb_signal(_signal_number: int, _frame: FrameType | None) -> None:
    """Let the application runtime complete its shutdown work."""


def run_server(bound_socket: socket.socket, instances: injection.Instances) -> int:
    """Run one configured application on an already-bound socket.

    Returns:
        Integer result.

    """
    audit = injection.resolve(instances, provider_audit_storage.recorder)
    port, source = _bound_port_source(bound_socket)
    stream_id = audit.stream_start("", "dashboard", src_path=source)
    try:
        _serve_bound_socket(bound_socket, instances)
    except Exception:
        audit.error("", "dashboard serve", PortAudit(port=port))
        audit.stream_end(stream_id, "crash")
        raise
    else:
        audit.stream_end(stream_id, "stopped")
        return 0


def _serve_bound_socket(bound_socket: socket.socket, instances: injection.Instances) -> None:
    server = build_server(
        build_web_application(instances, run_background_workers=True),
        injection.resolve(instances, dependencies.policy).graceful_shutdown_seconds,
    )
    # Uvicorn raises the captured signal again after run(). The absorber lets
    # the application runtime record the completed shutdown first.
    signal.signal(signal.SIGTERM, _absorb_signal)
    _run_uvicorn(server, bound_socket)
