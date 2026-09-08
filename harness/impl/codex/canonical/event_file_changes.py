
# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert completed Codex file changes."""

from dataclasses import dataclass

from harness.impl.codex.canonical import record_context_records, record_file_items


@dataclass(frozen=True)
class FileDestination:
    """Describe the destination of one completed file change."""

    path: str
    change: str | None
    previous_path: str | None


def diff_delta(unified_diff: str) -> tuple[int, int]:
    """Count added and removed lines in a unified diff.

    Returns:
        The added and removed line counts.

    """
    added = 0
    removed = 0
    for diff_line in unified_diff.splitlines():
        if diff_line.startswith("+") and not diff_line.startswith("+++"):
            added += 1
        elif diff_line.startswith("-") and not diff_line.startswith("---"):
            removed += 1
    return added, removed


def patch_delta(change: record_file_items.FileChangeEntry) -> tuple[int, int]:
    """Count changed lines for one file entry.

    Returns:
        The added and removed line counts.

    """
    if change.type == "add":
        return len((change.content or "").splitlines()), 0
    if change.type == "delete":
        return 0, len((change.content or "").splitlines())
    return diff_delta(change.unified_diff or "")


def destination(path: str, change: record_file_items.FileChangeEntry) -> FileDestination:
    """Return the final path and change type.

    Returns:
        The final path, change type, and previous path.

    """
    if change.move_path:
        return FileDestination(change.move_path, "move", path)
    return FileDestination(path, change.type, None)


def patch_file(path: str, change: record_file_items.FileChangeEntry) -> record_context_records.PatchFile:
    """Build one canonical patch file.

    Returns:
        The canonical patch file.

    """
    line_delta = patch_delta(change)
    file_destination = destination(path, change)
    return record_context_records.PatchFile(
        path=file_destination.path,
        change=file_destination.change,
        added=line_delta[0],
        removed=line_delta[1],
        previous_path=file_destination.previous_path,
        diff=change.unified_diff or "" if file_destination.change in {"update", "move"} else None,
        content=change.content or "" if file_destination.change in {"add", "delete"} else None,
    )


def file_change(file_change_item: record_file_items.FileChangeItem) -> record_context_records.PatchRecord:
    """Convert one authoritative file-change item.

    Returns:
        The canonical patch record.

    """
    changes = file_change_item.changes.root.items() if file_change_item.changes else ()
    files: list[record_context_records.PatchFile] = []
    for path, change in changes:
        files.append(patch_file(path, change))
    return record_context_records.PatchRecord(success=file_change_item.status == "completed", files=tuple(files))
