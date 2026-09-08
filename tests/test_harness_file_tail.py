# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the test harness file tail module."""

from collections.abc import Callable
from functools import partialmethod
from pathlib import Path
from typing import IO

import pytest

from harness.file_tail import CompleteLine, CompleteLineTail


def _record_file_open(
    file_path: Path,
    opened_paths: list[str],
    native_open: Callable[..., IO[str] | IO[bytes]],
    *open_arguments: object,
    **open_options: object,
) -> IO[str] | IO[bytes]:
    mode = open_arguments[0] if open_arguments else open_options.get("mode", "r")
    if mode == "rb":
        opened_paths.append(str(file_path))
    return native_open(file_path, *open_arguments, **open_options)


def _assert_tail_has_no_update(tail: CompleteLineTail, position: str) -> None:
    assert tail.read(position, 100) == ()


def _assert_line_content(
    lines: tuple[CompleteLine, ...],
    expected_content: bytes,
) -> None:
    assert [line.content for line in lines] == [expected_content]


def test_unchanged_tail_does_not_reopen_the_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify unchanged tail does not reopen the file."""
    path = tmp_path / "events.jsonl"
    path.write_bytes(b'{"type":"first"}\n')
    tail = CompleteLineTail(str(path))

    first = tail.read(None, 100)
    assert len(first) == 1
    _assert_tail_has_no_update(tail, str(first[0].position))

    opened: list[str] = []
    monkeypatch.setattr(Path, "open", partialmethod(_record_file_open, opened, Path.open))

    _assert_tail_has_no_update(tail, str(first[0].position))
    assert opened == []

    with path.open("ab") as destination:
        destination.write(b'{"type":"second"}\n')

    _assert_line_content(
        tail.read(str(first[0].position), 100),
        b'{"type":"second"}\n',
    )
    assert opened == [str(path)]


def test_tail_waits_for_a_complete_appended_line(tmp_path: Path) -> None:
    """Verify tail waits for a complete appended line."""
    path = tmp_path / "events.jsonl"
    path.write_bytes(b'{"type":"first"}\n')
    tail = CompleteLineTail(str(path))
    first = tail.read(None, 100)

    with path.open("ab") as destination:
        destination.write(b'{"type":"second"}')
    assert tail.read(str(first[0].position), 100) == ()

    with path.open("ab") as destination:
        destination.write(b"\n")
    changed = tail.read(str(first[0].position), 100)

    assert [line.content for line in changed] == [b'{"type":"second"}\n']
