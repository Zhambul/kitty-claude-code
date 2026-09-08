# Copyright (c) 2026 Zhambyl Yermagambet
"""Repository policy for raw-record architecture checks."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests.raw_record_types import Violation

ROOT = Path(__file__).resolve().parent.parent
RAW_RECORD_ALLOWED: frozenset[str] = frozenset()


def production_packages() -> tuple[str, ...]:
    """Return packages that production code can import from.

    Returns:
        Packages that production code can import from.

    """
    package_names = {"bin", "client"}
    for package_init in ROOT.glob("*/__init__.py"):
        package_name = package_init.parent.name
        if package_name != "tests":
            package_names.add(package_name)
    return tuple(sorted(package_names))


def production_python_paths() -> list[Path]:
    """Return production Python source paths.

    Returns:
        Production Python source paths.

    """
    return [
        path
        for package in production_packages()
        for path in sorted((ROOT / package).rglob("*.py"))
        if "__pycache__" not in path.parts
    ]


def is_allowed_raw_record(relative_path: str, source_lines: list[str], violation: Violation) -> bool:
    """Return true when one marked violation is allowed.

    Returns:
        True when one marked violation is allowed.

    """
    location = f"{relative_path}:{violation[1]}"
    if location not in RAW_RECORD_ALLOWED:
        return False
    return "# raw-record:" in source_lines[violation[0] - 1]
