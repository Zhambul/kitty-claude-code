# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

import ast
import os
import pathlib
import re
import shlex

from harness.impl.codex.canonical.translator_tool_models import (
    _NODE_READ_CWD_SUFFIX,
    _NODE_READ_FILE,
    _NODE_READ_TEMPLATE_EXPRESSION,
)

_SKILL_DIRECTORY_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SKILL_READ_WORD_COUNT = 2
MINIMUM_SKILL_PATH_PARTS = 4


def _node_read_path(arguments: str | None) -> str:
    source = arguments or ""
    cwd_match = _NODE_READ_CWD_SUFFIX.search(source)
    match = cwd_match or _NODE_READ_TEMPLATE_EXPRESSION.search(source) or _NODE_READ_FILE.search(source)
    if match is None:
        return ""
    try:
        path = ast.literal_eval(match.group(1))
    except (SyntaxError, ValueError):
        return ""
    found = str(path)
    return found if cwd_match is None else found.lstrip("/")


def read_skill_name(command: str) -> str | None:
    """Return the name from one direct read of a Codex skill file.

    Returns:
        Name from one direct read of a Codex skill file.

    """
    try:
        words = shlex.split(command)
    except ValueError:
        return None
    if len(words) != SKILL_READ_WORD_COUNT or words[0] != "cat":
        return None
    skill_parts = pathlib.Path(os.path.normpath(words[1])).parts
    if len(skill_parts) < MINIMUM_SKILL_PATH_PARTS:
        return None
    if skill_parts[-4:-2] != (".agents", "skills"):
        return None
    name, filename = skill_parts[-2:]
    valid_skill = filename == "SKILL.md" and _SKILL_DIRECTORY_NAME.fullmatch(name) is not None
    return name if valid_skill else None


def source_position(raw_position: str) -> int | None:
    """Read the byte position stored with a source record.

    Returns:
        The integer position, or None if the text is not an integer.

    """
    try:
        return int(raw_position)
    except ValueError:
        return None
