# Copyright (c) 2026 Zhambyl Yermagambet
"""Read bounded output from a client test process."""

from __future__ import annotations

import io
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import subprocess

PROCESS_READ_BYTES = 65_536
TEXT_ENCODING = "utf-8"


def read_until_marker(
    process: subprocess.Popen[bytes],
    marker: str,
    timeout: float = 20.0,
) -> str:
    """Read process output until a marker, end of output, or the time limit.

    Use read1 so a read does not wait for the entire buffer to fill.

    Returns:
        The decoded output collected by the reads.

    Raises:
        TypeError: If process output is not a buffered byte stream.

    """
    painted = ""
    deadline = time.monotonic() + timeout
    if not isinstance(process.stdout, io.BufferedReader):
        message = "pane process stdout is not a byte buffer"
        raise TypeError(message)
    while marker not in painted and time.monotonic() < deadline:
        chunk = process.stdout.read1(PROCESS_READ_BYTES)
        if not chunk:
            break
        painted += chunk.decode(TEXT_ENCODING, "replace")
    return painted
