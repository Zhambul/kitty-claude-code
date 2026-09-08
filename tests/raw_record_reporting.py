# Copyright (c) 2026 Zhambyl Yermagambet
"""Report repository raw-record violations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.raw_record_analysis import source_violations
from tests.raw_record_policy import ROOT, is_allowed_raw_record

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from tests.raw_record_types import Violation

TEXT_ENCODING = "utf-8"
RAW_RECORD_MARKER = "# raw-record:"


def raw_record_violations(path: Path) -> Iterator[str]:
    """Check a file for unapproved raw-record use.

    Yields:
        Each violation with its location and required model change.

    """
    relative_path = str(path.relative_to(ROOT))
    source_lines = path.read_text(encoding=TEXT_ENCODING).splitlines()
    for violation in source_violations("\n".join(source_lines)):
        if not is_allowed_raw_record(relative_path, source_lines, violation):
            yield raw_record_message(relative_path, violation)


def raw_record_message(relative_path: str, violation: Violation) -> str:
    """Return the message for one raw-record violation.

    Returns:
        The message for one raw-record violation.

    """
    line_number, item_kind, item_name = violation
    return f"{relative_path}:{line_number} {item_kind}: {item_name} - use a named immutable model"


def marked_raw_record_items(path: Path) -> set[str]:
    """Return marked raw-record item names from one file.

    Returns:
        Marked raw-record item names from one file.

    """
    relative_path = str(path.relative_to(ROOT))
    source_lines = path.read_text(encoding=TEXT_ENCODING).splitlines()
    return {
        f"{relative_path}:{violation[1]}"
        for violation in source_violations("\n".join(source_lines))
        if RAW_RECORD_MARKER in source_lines[violation[0] - 1]
    }
