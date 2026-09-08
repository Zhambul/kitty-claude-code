# Copyright (c) 2026 Zhambyl Yermagambet
"""Report loose annotation violations."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from tests.typing_loose_annotations import LooseAnnotationVisitor, LooseViolation
from tests.typing_loose_repository import LOOSE_ANNOTATION_ALLOWED, ROOT

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

TEXT_ENCODING = "utf-8"
LOOSE_MARKER = "# loose:"


def loose_annotation_message(
    relative_path: str,
    source_lines: list[str],
    violation: LooseViolation,
) -> str | None:
    """Return a message for one unapproved loose annotation.

    Returns:
        A message for one unapproved loose annotation.

    """
    line_number, key, annotation_text = violation
    if f"{relative_path}:{key}" in LOOSE_ANNOTATION_ALLOWED and LOOSE_MARKER in source_lines[line_number - 1]:
        return None
    return f"{relative_path}:{line_number} {key}: {annotation_text} - declare the real shape"


def loose_annotation_violations(path: Path) -> Iterator[str]:
    """Check a file for unapproved loose type annotations.

    Yields:
        Each violation with its location and annotation text.

    """
    relative_path = str(path.relative_to(ROOT))
    source_lines = path.read_text(encoding=TEXT_ENCODING).splitlines()
    visitor = LooseAnnotationVisitor()
    visitor.visit(ast.parse("\n".join(source_lines)))
    for violation in visitor.violations:
        message = loose_annotation_message(relative_path, source_lines, violation)
        if message is not None:
            yield message


def marked_loose_annotation_keys(path: Path) -> set[str]:
    """Return marked loose annotation keys from one file.

    Returns:
        Marked loose annotation keys from one file.

    """
    relative_path = str(path.relative_to(ROOT))
    source_lines = path.read_text(encoding=TEXT_ENCODING).splitlines()
    visitor = LooseAnnotationVisitor()
    visitor.visit(ast.parse("\n".join(source_lines)))
    return {
        f"{relative_path}:{violation[1]}"
        for violation in visitor.violations
        if LOOSE_MARKER in source_lines[violation[0] - 1]
    }
