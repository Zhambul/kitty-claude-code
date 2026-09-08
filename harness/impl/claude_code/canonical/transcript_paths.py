# Copyright (c) 2026 Zhambyl Yermagambet
"""Identify Claude transcript paths."""

from pathlib import Path

from pydantic import ValidationError

from harness.impl.claude_code.canonical import records
from harness.impl.claude_code.canonical.transcript_model_core import TranscriptKind

PROJECTS_DIRECTORY_NAME = "projects"
AGENT_DIRECTORY_NAME = "subagents"
CLAIM_HEAD_BYTES = 8192
RECORD_TYPES = frozenset(
    (
        "summary",
        "user",
        TranscriptKind.ASSISTANT.value,
        "system",
        "attachment",
        "queue-operation",
        "agent-name",
        "ai-title",
        "file-history-snapshot",
    ),
)


def jsonl_file(path: str) -> bool:
    """Return whether the path names an existing JSONL file.

    Returns:
        Whether the path names an existing JSONL file.

    """
    transcript_path = Path(path)
    return bool(path) and transcript_path.suffix == ".jsonl" and transcript_path.is_file()


def session_transcript(path: str) -> bool:
    """Return whether the path names a Claude session transcript.

    Returns:
        Whether the path names a Claude session transcript.

    """
    transcript_path = Path(path)
    return jsonl_file(path) and transcript_path.parent.parent.name == PROJECTS_DIRECTORY_NAME


def agent_transcript(path: str) -> bool:
    """Return whether the path names a Claude agent transcript.

    Returns:
        Whether the path names a Claude agent transcript.

    """
    transcript_directory = Path(path).parent
    return (
        jsonl_file(path)
        and transcript_directory.name == AGENT_DIRECTORY_NAME
        and transcript_directory.parents[2].name == PROJECTS_DIRECTORY_NAME
    )


def claude_head(path: str) -> bool:
    """Return whether the file head contains a Claude transcript record.

    Returns:
        Whether the file head contains a Claude transcript record.

    """
    try:
        with Path(path).open("rb") as source:
            head = source.read(CLAIM_HEAD_BYTES)
    except OSError:
        return False
    for raw_line in head.split(b"\n"):
        if not raw_line.strip():
            continue
        try:
            header = records.TranscriptRecordHeader.model_validate_json(raw_line)
        except ValidationError:
            continue
        if header.type in RECORD_TYPES:
            return True
    return False


def owns(path: str) -> bool:
    """Return whether the Claude plugin owns the path.

    Returns:
        Whether the Claude plugin owns the path.

    """
    if session_transcript(path) or agent_transcript(path):
        return True
    return jsonl_file(path) and claude_head(path)


def renameable(path: str) -> bool:
    """Return whether the path is a renameable Claude transcript.

    Returns:
        Whether the path is a renameable Claude transcript.

    """
    return session_transcript(path)
