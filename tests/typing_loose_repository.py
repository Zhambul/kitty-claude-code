# Copyright (c) 2026 Zhambyl Yermagambet
"""Repository scope for loose annotation checks."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOOSE_ANNOTATION_ALLOWED: frozenset[str] = frozenset()


def loose_annotation_packages() -> tuple[str, ...]:
    """Return packages scanned for loose annotations.

    Returns:
        Packages scanned for loose annotations.

    """
    package_names = {"bin", "client"}
    for package_init in ROOT.glob("*/__init__.py"):
        package_name = package_init.parent.name
        if package_name != "tests":
            package_names.add(package_name)
    return tuple(sorted(package_names))


def loose_annotation_paths() -> list[Path]:
    """Return production Python paths for the loose annotation check.

    Returns:
        Production Python paths for the loose annotation check.

    """
    paths: list[Path] = []
    for package in loose_annotation_packages():
        package_paths = sorted((ROOT / package).rglob("*.py"))
        paths.extend(path for path in package_paths if "__pycache__" not in path.parts)
    return paths
