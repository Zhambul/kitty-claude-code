# Copyright (c) 2026 Zhambyl Yermagambet
"""Split GitHub Projects SDK implementation."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from github_project_errors import GitHubProjectError

if TYPE_CHECKING:
    import github_project_values_data as project_values


def optional_text_field(document: dict[str, project_values.JsonValue], field: str) -> str | None:
    """Read an optional text field.

    Returns:
        The text value, or None for an absent or null field.

    Raises:
        GitHubProjectError: If a non-null field is not text.

    """
    field_content = document.get(field)
    if field_content is not None and not isinstance(field_content, str):
        msg = f"GitHub field is not text: {field}"
        raise GitHubProjectError(msg)
    return field_content


def integer_field(document: dict[str, project_values.JsonValue], field: str) -> int:
    """Read a required integer field.

    Returns:
        The integer field value.

    Raises:
        GitHubProjectError: If the field is absent or is not an integer.

    """
    field_content = document.get(field)
    if not isinstance(field_content, int):
        msg = f"GitHub field is not an integer: {field}"
        raise GitHubProjectError(msg)
    return field_content


def emit_document(json_content: object) -> None:
    """Write an indented JSON document to standard output."""
    json.dump(json_content, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
