# Copyright (c) 2026 Zhambyl Yermagambet
"""Find and observe named file operations in a session feed."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.sessiondata.models.entry import FileBodyResponse

if TYPE_CHECKING:
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit.references import FileOperationRef


def operation(snapshot: SessionSnapshot, reference: FileOperationRef) -> FileBodyResponse:
    """Return the one matching file operation.

    Returns:
        The matching operation body.

    Raises:
        AssertionError: If the reference does not select exactly one operation.

    """
    found = [
        entry.body
        for entry in snapshot.entries
        if entry.entry_id == reference.entry_id and isinstance(entry.body, FileBodyResponse)
    ]
    if len(found) != 1:
        message = f"file operation {reference.entry_id!r} has {len(found)} matches"
        raise AssertionError(message)
    return found[0]


def has_state(snapshot: SessionSnapshot, reference: FileOperationRef, state: str) -> bool | None:
    """Return true once an operation has the expected state.

    Returns:
        ``True`` on a match, otherwise ``None``.

    """
    return True if operation(snapshot, reference).state == state else None


def content_contains(snapshot: SessionSnapshot, reference: FileOperationRef, text: str) -> bool | None:
    """Return true once operation content contains text.

    Returns:
        ``True`` on a match, otherwise ``None``.

    """
    content = operation(snapshot, reference).content
    return True if content is not None and text in content.text else None


def has_added_lines(snapshot: SessionSnapshot, reference: FileOperationRef) -> bool | None:
    """Return true once an operation reports added lines.

    Returns:
        ``True`` on a match, otherwise ``None``.

    """
    return True if (operation(snapshot, reference).lines_added or 0) > 0 else None


def has_removed_lines(snapshot: SessionSnapshot, reference: FileOperationRef) -> bool | None:
    """Return true once an operation reports removed lines.

    Returns:
        ``True`` on a match, otherwise ``None``.

    """
    return True if (operation(snapshot, reference).lines_removed or 0) > 0 else None
