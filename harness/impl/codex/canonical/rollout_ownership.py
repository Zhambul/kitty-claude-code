# Copyright (c) 2026 Zhambyl Yermagambet
"""Identify Codex rollout files."""

from __future__ import annotations

import os
from pathlib import Path


def owns(path: str) -> bool:
    """Return whether a path is a Codex rollout file.

    Returns:
        Whether a path is a Codex rollout file.

    """
    if not path or not path.endswith(".jsonl"):
        return False
    normalized_path = Path(os.path.normpath(path))
    if not normalized_path.name.startswith("rollout-"):
        return False
    return "sessions" in normalized_path.parts[:-1]
