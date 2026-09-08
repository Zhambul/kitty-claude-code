# Copyright (c) 2026 Zhambyl Yermagambet
"""List owned packages without loading architecture checks."""

from pathlib import Path


def owned_packages() -> tuple[str, ...]:
    """Return the package and script directory names.

    Returns:
        The sorted names of owned packages and script directories.

    """
    root = Path(__file__).resolve().parents[1]
    names = {"bin", "client"}
    names.update(
        path.parent.name
        for path in root.glob("*/__init__.py")
        if path.parent.name != "tests"
    )
    return tuple(sorted(names))
