# Copyright (c) 2026 Zhambyl Yermagambet
"""Check native process and file change notices."""

from __future__ import annotations

import subprocess  # noqa: S404 -- Test exit notices with a fixed local Python child process.
import sys
from contextlib import ExitStack, closing
from threading import Event
from typing import TYPE_CHECKING

import pytest

from core.input_events import InputEvents
from core.kernel_events import KernelEvents
from tests import native_event_support

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

TEXT_ENCODING = "utf-8"


@pytest.fixture
def child_process() -> Iterator[subprocess.Popen[bytes]]:
    """Start a child that waits for input and stop it after the test.

    Yields:
        The child process with its input pipe open.

    """
    process = subprocess.Popen([sys.executable, "-c", "import sys; sys.stdin.read()"], stdin=subprocess.PIPE)
    with ExitStack() as cleanup:
        cleanup.callback(native_event_support.stop_process, process)
        yield process


def test_native_notice_for_output_replacement(tmp_path: Path) -> None:
    """Read new output and an atomic replacement through the same watch."""
    changed = Event()
    output = tmp_path / "output.log"
    watcher = InputEvents(changed.set, ())
    watcher.start()
    with closing(watcher):
        watcher.update(set(), {output})
        output.write_text("first", encoding=TEXT_ENCODING)
        assert changed.wait(5)
        changed.clear()
        replacement = tmp_path / "replacement"
        replacement.write_text("second", encoding=TEXT_ENCODING)
        replacement.replace(output)
        assert changed.wait(5)


def test_native_exit_without_final_record(child_process: subprocess.Popen[bytes]) -> None:
    """Process exit must wake the engine even when no file changes."""
    changed = Event()
    watcher = KernelEvents(changed.set)
    watcher.start()
    with closing(watcher):
        watcher.update({child_process.pid})
        assert not changed.wait(0.1)
        native_event_support.finish_process(child_process, changed)


def test_file_and_process_share_native_wait(tmp_path: Path, child_process: subprocess.Popen[bytes]) -> None:
    """Keep file notifications active after a watched process exits."""
    changed = Event()
    transcript = tmp_path / "session.jsonl"
    watcher = InputEvents(changed.set, ())
    watcher.start()
    with closing(watcher):
        native_event_support.watch_empty_transcript(watcher, transcript)
        watcher.watch_processes({child_process.pid})
        changed.clear()
        native_event_support.finish_process(child_process, changed)
        watcher.watch_processes(set())
        changed.clear()
        with transcript.open("a", encoding=TEXT_ENCODING) as stream:
            native_event_support.append_and_wait(stream, changed, "new data\n")


def test_profile_watch_observes_open_transcript(tmp_path: Path) -> None:
    """Observe appended data while the harness keeps its transcript open."""
    changed = Event()
    profile = tmp_path / "profile"
    transcript = profile / "sessions" / "session.jsonl"
    transcript.parent.mkdir(parents=True)
    watcher = InputEvents(changed.set, (profile,))
    watcher.start()
    with closing(watcher):
        watcher.update({transcript.parent}, set())
        with transcript.open("a", encoding=TEXT_ENCODING) as stream:
            native_event_support.append_and_wait(stream, changed, "first\n")
            watcher.watch_files({transcript.resolve()})
            changed.clear()
            native_event_support.append_and_wait(stream, changed, "second\n")
