# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide process and file actions for native event tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path
    from threading import Event
    from typing import TextIO

    from core.input_events import InputEvents


def stop_process(process: subprocess.Popen[bytes]) -> None:
    """Stop a test child if it is still running."""
    if process.poll() is None:
        process.kill()
        process.wait()


def finish_process(process: subprocess.Popen[bytes], changed: Event) -> None:
    """Close child input and check that its exit sends a notice."""
    assert process.stdin is not None
    process.stdin.close()
    assert changed.wait(5)
    process.wait(5)


def append_and_wait(stream: TextIO, changed: Event, text: str) -> None:
    """Append and flush text, then check for a native change notice."""
    stream.write(text)
    stream.flush()
    assert changed.wait(5)


def watch_empty_transcript(watcher: InputEvents, transcript: Path) -> None:
    """Create an empty transcript and watch its directory and file."""
    transcript.write_text("", encoding="utf-8")
    watcher.update({transcript.parent}, set())
    watcher.watch_files({transcript.resolve()})
