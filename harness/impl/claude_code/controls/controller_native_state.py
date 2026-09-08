# Copyright (c) 2026 Zhambyl Yermagambet
"""Read native Claude Code message delivery state."""

import pathlib

from pydantic import ValidationError

from harness.impl.claude_code.canonical import records, transcript
from harness.impl.claude_code.controls import controller_values as control_values
from harness.impl.claude_code.controls.controller_prompt_matching import (
    _same_native_prompt,
    _sent_prompt_record,
    _user_line_matches,
)


def native_text_state(source_reference: str, after_position: int, expected: str) -> str | None:
    """Read the delivery state of a prompt from new transcript records.

    Returns:
        The latest matching state, or None if no state can be read.

    """
    if after_position < 0:
        return None
    lines = _added_transcript_lines(source_reference, after_position)
    if lines is None:
        return None
    state = None
    for line in lines:
        state = _native_line_state(line, expected, state)
    return state


def _added_transcript_lines(source_reference: str, after_position: int) -> tuple[bytes, ...] | None:
    try:
        with pathlib.Path(source_reference).open("rb") as source:
            source.seek(after_position)
            return tuple(source.read().splitlines())
    except OSError:
        return None


def _native_line_state(line: bytes, expected: str, current_state: str | None) -> str | None:
    try:
        header = records.TranscriptRecordHeader.model_validate_json(line)
    except ValidationError:
        return current_state
    if header.type == "queue-operation":
        return _queue_line_state(line, expected, current_state)
    return _transcript_line_state(line, expected, current_state, header.type)


def _transcript_line_state(
    line: bytes,
    expected: str,
    current_state: str | None,
    record_type: str | None,
) -> str | None:
    if record_type == "user" and _user_line_matches(line, expected):
        return control_values.NATIVE_TEXT_SENT
    try:
        parsed = transcript.parse_line(line.decode("utf-8", errors="replace"))
    except (UnicodeError, ValidationError):
        return current_state
    if _sent_prompt_record(parsed, expected):
        return control_values.NATIVE_TEXT_SENT
    return current_state


def _queue_line_state(line: bytes, expected: str, current_state: str | None) -> str | None:
    try:
        operation = records.QueueOperationRecord.model_validate_json(line)
    except ValidationError:
        return current_state
    if not isinstance(operation.content, str) or not _same_native_prompt(expected, operation.content):
        return current_state
    return _queue_operation_state(operation.operation, current_state)


def _queue_operation_state(operation: str | None, current_state: str | None) -> str | None:
    if operation == "enqueue":
        return control_values.NATIVE_TEXT_QUEUED
    if operation == "remove":
        return control_values.NATIVE_TEXT_SENT
    return current_state
