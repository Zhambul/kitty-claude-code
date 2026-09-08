# Copyright (c) 2026 Zhambyl Yermagambet
"""Policy for typed ignore comments."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_ENCODING = "utf-8"


def is_type_ignore_source(path: Path) -> bool:
    """Return whether a path can contain an unnamed type ignore.

    Returns:
        Whether a path can contain an unnamed type ignore.

    """
    excluded_directories = {"__pycache__", ".claude", ".venv"}
    if any(part in excluded_directories for part in path.parts):
        return False
    return path.resolve() != Path(__file__).resolve()


def unnamed_type_ignore_locations(path: Path) -> list[str]:
    """Return unnamed type-ignore locations from one source file.

    Returns:
        Unnamed type-ignore locations from one source file.

    """
    return [
        f"{path.relative_to(ROOT)}:{number}"
        for number, line in enumerate(path.read_text(encoding=TEXT_ENCODING).splitlines(), 1)
        if re.search(r"#\s*type:\s*ignore(?!\[)", line)
    ]
