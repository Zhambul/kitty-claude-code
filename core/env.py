# Copyright (c) 2026 Zhambyl Yermagambet
"""Typed environment configuration reads."""

from __future__ import annotations

import os


def env_float(name: str, default: float) -> float:
    """Read a float from the environment.

    Returns:
        Numeric result.

    """
    configured_value = os.environ.get(name)
    if configured_value in {None, ""}:
        return float(default)
    return float(configured_value)


def env_int(name: str, default: int) -> int:
    """Read an integer from the environment.

    Returns:
        Integer result.

    """
    configured_value = os.environ.get(name)
    if configured_value in {None, ""}:
        return int(default)
    return int(configured_value)
