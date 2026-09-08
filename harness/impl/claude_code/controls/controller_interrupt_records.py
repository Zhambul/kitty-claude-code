# Copyright (c) 2026 Zhambyl Yermagambet
"""Read Claude Code interrupt state from a transcript."""

import pathlib
import time

from harness.impl.claude_code.canonical import transcript

INTERRUPT_CONFIRMATION_TIMEOUT_SECONDS = 5.0


def _transcript_has_interrupt(source_reference: str, after_position: int) -> bool:
    try:
        with pathlib.Path(source_reference).open("rb") as source:
            source.seek(max(after_position, 0))
            added = source.read()
    except OSError:
        return False
    for line in added.splitlines():
        record = transcript.parse_line(line.decode("utf-8", errors="replace"))
        if (
            isinstance(record, (transcript.PromptTranscriptRecord, transcript.ResultsTranscriptRecord))
            and record.interrupted
        ):
            return True
    return False


def _transcript_position(source_reference: str) -> int:
    try:
        return pathlib.Path(source_reference).stat().st_size
    except OSError:
        return -1


def _interrupt_corroborated(source_reference: str, position: int) -> bool:
    deadline = time.monotonic() + INTERRUPT_CONFIRMATION_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        time.sleep(0.1)
        if position >= 0 and _transcript_has_interrupt(source_reference, position):
            return True
    return False
