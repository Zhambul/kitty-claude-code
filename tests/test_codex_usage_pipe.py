# Copyright (c) 2026 Zhambyl Yermagambet
"""Check usage replies without a live Codex process."""

import os
import time
from collections.abc import Iterator
from typing import IO
from unittest.mock import Mock

import pytest

from harness.impl.codex.usage_response import response

USAGE_REPLY = b'{"id":2,"result":{"rateLimits":{"primary":{"usedPercent":12}}}}\n'
INITIALIZE_REPLY = b'{"id":1,"result":{}}\n'
READ_TIMEOUT = 0.1
type OutputPipe = tuple[IO[str], int]


@pytest.fixture
def output_pipe() -> Iterator[OutputPipe]:
    """Open a pipe and keep its writer open while the reader waits.

    Yields:
        A text output stream and its write descriptor.

    """
    read_descriptor, write_descriptor = os.pipe()
    try:
        with os.fdopen(read_descriptor, encoding="utf-8") as stream:
            yield stream, write_descriptor
    finally:
        os.close(write_descriptor)


def test_usage_reads_two_replies_in_one_write(output_pipe: OutputPipe) -> None:
    """Read the matching reply even when both replies arrive together."""
    stream, write_descriptor = output_pipe
    os.write(write_descriptor, INITIALIZE_REPLY + USAGE_REPLY)
    result = response(Mock(stdout=stream), time.monotonic() + READ_TIMEOUT, 2)
    assert result.failure is None
    assert result.response is not None


def test_usage_partial_line_respects_deadline(output_pipe: OutputPipe) -> None:
    """Do not block past the deadline while a response line is incomplete."""
    stream, write_descriptor = output_pipe
    os.write(write_descriptor, USAGE_REPLY[:10])
    result = response(Mock(stdout=stream), time.monotonic() + READ_TIMEOUT, 2)
    assert result.failure is not None
    assert result.failure.message == "Codex usage request timed out"
