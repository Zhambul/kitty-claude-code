#!/usr/bin/env python3
# Copyright (c) 2026 Zhambyl Yermagambet
"""Ship one Codex hook delivery to the daemon.

~/.codex/hooks.json names THIS FILE, once per hook event, and the path is cached
for the session's lifetime — the same published-API rule as its Claude Code twin
(`claude_hook.py`).

Codex has no accounts and no launch-time selections to observe, so the delivery
carries only the window this process runs in and its own pid; there is no reply
channel either. Everything the delivery means is decided daemon-side in
`harness/impl/codex/hooks/gateway.py`.
"""

from __future__ import annotations

import contextlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # my own directory

import _daemon
import _http

HARNESS = "codex"


def main() -> None:
    """Run the command."""
    if os.environ.get(_http.INTERNAL_MODEL_VARIABLE):
        return
    payload = sys.stdin.buffer.read()
    reply = _daemon.post(
        _http.HOOK_PATH % HARNESS,
        payload,
        {
            _http.TERMINAL_WINDOW_HEADER: _http.window_id(os.environ),
            _http.CLIENT_PROCESS_HEADER: str(os.getpid()),
        },
    )
    if reply:
        sys.stdout.buffer.write(reply)


if __name__ == "__main__":
    with contextlib.suppress(Exception):
        main()
