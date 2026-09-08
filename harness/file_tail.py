# Copyright (c) 2026 Zhambyl Yermagambet
"""Read complete appended lines without reopening an unchanged file."""

from __future__ import annotations

import os
import pathlib
from contextlib import ExitStack
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import BinaryIO


@dataclass(frozen=True)
class FileMarker:
    """The file values that change when an append-only feed changes."""

    inode: int
    modified_at: int
    size: int


@dataclass(frozen=True)
class CompleteLine:
    """One complete line and the byte position where it starts."""

    position: int
    content: bytes


def _next_line(source: BinaryIO) -> CompleteLine | None:
    line_position = source.tell()
    line = source.readline()
    if not line or not line.endswith(b"\n"):
        return None
    return CompleteLine(line_position, line)


def _marker(status: os.stat_result) -> FileMarker:
    return FileMarker(status.st_ino, status.st_mtime_ns, status.st_size)


def _file_marker(descriptor: int) -> FileMarker:
    return _marker(os.fstat(descriptor))


def _complete_lines(
    source: BinaryIO,
    after_position: str | None,
    limit: int,
) -> tuple[list[CompleteLine], FileMarker]:
    if after_position is not None:
        source.seek(int(after_position))
        skipped = source.readline()
        if not skipped.endswith(b"\n"):
            return [], _file_marker(source.fileno())
    lines: list[CompleteLine] = []
    for _ in range(limit):
        complete_line = _next_line(source)
        if complete_line is None:
            break
        lines.append(complete_line)
    return lines, _file_marker(source.fileno())


class CompleteLineTail:
    """A stat-gated reader for one append-only line feed.

    The durable database position remains the authority. The local marker is
    only an idle fast path. A new object, a changed position, or a changed file
    always reads from the durable position again.
    """

    def __init__(self, path: str) -> None:
        """Initialize the object."""
        self.path = os.path.realpath(path)
        self._idle_position: str | None = None
        self._idle_marker: FileMarker | None = None
        self._idle_known = False

    def read(
        self,
        after_position: str | None,
        limit: int,
    ) -> tuple[CompleteLine, ...]:
        """Return read.

        Returns:
            Read.

        Raises:
            ValueError: If an input value is not valid.

        """
        if limit <= 0:
            message = "line limit must be positive"
            raise ValueError(message)
        marker = self._path_marker()
        if self._idle_known and after_position == self._idle_position and marker == self._idle_marker:
            return ()
        lines: list[CompleteLine] = []
        with ExitStack() as resources:
            try:
                source = resources.enter_context(pathlib.Path(self.path).open("rb"))
            except FileNotFoundError:
                self._remember_idle(after_position, None)
                return ()
            lines, marker = _complete_lines(source, after_position, limit)
        if lines:
            self._idle_known = False
        else:
            self._remember_idle(after_position, marker)
        return tuple(lines)

    def _path_marker(self) -> FileMarker | None:
        try:
            status = pathlib.Path(self.path).stat()
        except FileNotFoundError:
            return None
        return _marker(status)

    def _remember_idle(
        self,
        after_position: str | None,
        file_marker: FileMarker | None,
    ) -> None:
        self._idle_position = after_position
        self._idle_marker = file_marker
        self._idle_known = True
