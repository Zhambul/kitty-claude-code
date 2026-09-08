# Copyright (c) 2026 Zhambyl Yermagambet
"""Resolve the dashboard entry after CLI configuration."""

from pathlib import Path


def dashboard_entry() -> str:
    """Return the dashboard entry path.

    Returns:
        Dashboard entry path.

    """
    from dashboard import paths  # noqa: PLC0415 — import purity, and more: this

    return str(Path(paths.BIN_DIRECTORY) / "baqylau_dashboard.py")
