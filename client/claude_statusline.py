#!/usr/bin/env python3
# Copyright (c) 2026 Zhambyl Yermagambet
"""Run the configured Claude status line.

Existing Claude settings name this stable file. Usage now comes from Claude's
structured usage request, so this file only passes the input to the configured
status-line command.
"""

from __future__ import annotations

import subprocess  # noqa: S404 -- This entry point runs the user's configured status-line command.
import sys


def delegate(argv: list[str], stdin_bytes: bytes) -> int:
    """Delegate.

    Run the real status-line command with the same stdin, inheriting stdout
        and stderr so its output is what Claude Code renders. 0 when there is no
        delegate — a bare shim install still succeeds.

    Returns:
        Integer result.

    """
    if not argv:
        return 0
    try:
        return subprocess.run(argv, input=stdin_bytes, check=False).returncode  # noqa: S603 -- The caller supplies the configured command; stdin is data and no shell is used.
    except OSError:
        return 0  # never break the status line


def main() -> None:
    """Run the command."""
    raw = sys.stdin.buffer.read()
    sys.exit(delegate(sys.argv[1:], raw))


if __name__ == "__main__":
    main()
