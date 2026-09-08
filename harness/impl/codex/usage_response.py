# Copyright (c) 2026 Zhambyl Yermagambet
"""Read the matching Codex rate limit RPC response."""

from __future__ import annotations

import os
import select
import time
from dataclasses import dataclass
from typing import IO, TYPE_CHECKING

from harness.impl.codex import usage_decoder
from harness.impl.codex.usage_models import ProbeFailure, ProbeResult

if TYPE_CHECKING:
    import subprocess

READ_SIZE = 65536
TIMEOUT_MESSAGE = "Codex usage request timed out"


@dataclass(frozen=True)
class _ReadLine:
    """Store one app-server output line or its failure."""

    line: str | None
    failure: ProbeFailure | None


class _ResponseLines:
    """Keep complete lines from each pipe read until they are consumed."""

    def __init__(self, output: IO[str], deadline: float) -> None:
        self.descriptor = output.fileno()
        self.deadline = deadline
        self.pending = b""

    def next_line(self) -> _ReadLine:
        """Read one line without waiting on bytes already in memory.

        Returns:
            One response line, or a read failure.

        """
        while b"\n" not in self.pending:
            chunk = _read_chunk(self.descriptor, self.deadline)
            if isinstance(chunk, ProbeFailure):
                return _ReadLine(None, chunk)
            if not chunk:
                return self._end_of_stream()
            self.pending += chunk
        line, _separator, remaining = self.pending.partition(b"\n")
        self.pending = remaining
        return _ReadLine(line.decode("utf-8", errors="replace"), None)

    def _end_of_stream(self) -> _ReadLine:
        if not self.pending:
            return _ReadLine(None, ProbeFailure(message="Codex app server ended early", recoverable=True))
        line = self.pending.decode("utf-8", errors="replace")
        self.pending = b""
        return _ReadLine(line, None)


def response(process: subprocess.Popen[str], deadline: float, response_id: int) -> ProbeResult:
    """Return the matching response before the deadline.

    Returns:
        The matching response before the deadline.

    """
    if process.stdout is None:
        return ProbeResult(None, ProbeFailure(message="Codex app server has no output", recoverable=True))
    lines = _ResponseLines(process.stdout, deadline)
    while True:
        read = lines.next_line()
        if read.failure is not None:
            return ProbeResult(None, read.failure)
        decoded = usage_decoder.decode_response(read.line or "", response_id)
        if decoded is not None:
            return decoded


def _read_chunk(descriptor: int, deadline: float) -> bytes | ProbeFailure:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        return ProbeFailure(message=TIMEOUT_MESSAGE, recoverable=True)
    readable = select.select((descriptor,), (), (), remaining)[0]
    if not readable:
        return ProbeFailure(message=TIMEOUT_MESSAGE, recoverable=True)
    return os.read(descriptor, READ_SIZE)
