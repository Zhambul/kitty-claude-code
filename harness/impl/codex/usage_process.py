# Copyright (c) 2026 Zhambyl Yermagambet
"""Run one Codex app-server rate limit request."""

from __future__ import annotations

import subprocess  # noqa: S404 -- Run the configured Codex app server for one usage request.
import time
from typing import TYPE_CHECKING

from harness.impl.codex import usage_requests, usage_response
from harness.impl.codex.usage_models import ProbeFailure, ProbeResult

if TYPE_CHECKING:
    from types import TracebackType

    from harness.runtime import HarnessRuntimeConfig


class ManagedAppServerProcess:
    """Close a Codex app-server process after one request."""

    def __init__(self, process: subprocess.Popen[str]) -> None:
        """Store the process."""
        self.process = process

    def __enter__(self) -> subprocess.Popen[str]:
        """Return the managed process.

        Returns:
            The managed process.

        """
        return self.process

    def __exit__(
        self,
        _exception_type: type[BaseException] | None,
        _exception: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        """Close the managed process."""
        close(self.process)


def start(
    harness_runtime_config: HarnessRuntimeConfig, environment: dict[str, str],
) -> subprocess.Popen[str] | ProbeResult:
    """Start the Codex app server, or return its startup failure.

    Returns:
        The child process, or a failure result if the process cannot start.

    """
    try:
        return subprocess.Popen(  # noqa: S603 -- Use the configured executable with a fixed app-server argument, without a shell.
            [harness_runtime_config.executable, "app-server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            env=environment,
        )
    except FileNotFoundError:
        return ProbeResult(None, ProbeFailure(message="Codex is not installed", recoverable=False))
    except OSError:
        return ProbeResult(None, ProbeFailure(message="Codex app server could not start", recoverable=True))


def stop(process: subprocess.Popen[str]) -> None:
    """Stop one app-server process."""
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=1.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=1.0)


def close(process: subprocess.Popen[str]) -> None:
    """Close app-server input and stop its process."""
    _close_input(process)
    stop(process)


def _close_input(process: subprocess.Popen[str]) -> None:
    if process.stdin is None:
        return
    try:
        process.stdin.close()
    except OSError:
        return


def send_rate_limit_request(process: subprocess.Popen[str], timeout: float, response_id: int) -> ProbeResult:
    """Send initialization and rate limit RPC requests.

    Returns:
        The rate limit response or a failure result for an unavailable response or input stream.

    """
    if process.stdin is None:
        return ProbeResult(None, ProbeFailure(message="Codex app server has no input", recoverable=True))
    initialize = usage_requests.InitializeRequest(
        initialization_details=usage_requests.InitializeParams(
            client_info=usage_requests.ClientInfo(name="baqylau", version="1"),
        ),
    )
    request = usage_requests.RateLimitsRequest(request_options=usage_requests.EmptyParams())
    try:
        return _exchange(process, initialize, request, timeout, response_id)
    except OSError:
        return ProbeResult(None, ProbeFailure(message="Codex usage request failed", recoverable=True))


def _exchange(
    process: subprocess.Popen[str],
    initialize: usage_requests.InitializeRequest,
    request: usage_requests.RateLimitsRequest,
    timeout: float,
    response_id: int,
) -> ProbeResult:
    input_stream = process.stdin
    if input_stream is None:
        return ProbeResult(None, ProbeFailure(message="Codex app server has no input", recoverable=True))
    input_stream.write(f"{initialize.request_json()}\n")
    input_stream.write(f"{request.request_json()}\n")
    input_stream.flush()
    return usage_response.response(process, time.monotonic() + timeout, response_id)
