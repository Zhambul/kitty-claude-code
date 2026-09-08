# Copyright (c) 2026 Zhambyl Yermagambet
"""Host the deterministic frontend fixture application."""

from __future__ import annotations

import socket
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from app.injection import resolve

if TYPE_CHECKING:
    import uvicorn

    from app.injection import Instances

type FixtureSeed = Callable[[Path, int], Instances]


def fixture_server(
    temporary: str,
    port_number: int,
    seed: FixtureSeed,
) -> tuple[uvicorn.Server, socket.socket, int]:
    """Build a bound fixture server.

    Returns:
        A bound fixture server.

    """
    bound_socket = socket.create_server(("127.0.0.1", port_number))
    port = int(bound_socket.getsockname()[1])
    instances = seed(Path(temporary), port)
    from api import dependencies  # noqa: PLC0415 -- Seed the fixture port before loading the application graph.
    from api.app import build_web_application  # noqa: PLC0415 -- Load routes after the fixture environment is set.
    from api.server import build_server  # noqa: PLC0415 -- Load server defaults after the fixture environment is set.

    policy = resolve(instances, dependencies.policy)
    bound_socket.listen(policy.request_queue_size)
    server = build_server(
        build_web_application(instances, run_background_workers=False),
        policy.graceful_shutdown_seconds,
    )
    return server, bound_socket, port
