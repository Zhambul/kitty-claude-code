# Copyright (c) 2026 Zhambyl Yermagambet
"""Own dashboard output."""

import sys


class UsageError(Exception):
    """Bad argv — the one failure this CLI reports rather than absorbs."""


def _output(message: str) -> None:
    sys.stdout.write(f"{message}\n")


def _error(message: str) -> None:
    sys.stderr.write(f"{message}\n")
