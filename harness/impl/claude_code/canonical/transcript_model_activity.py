# Copyright (c) 2026 Zhambyl Yermagambet
"""Define Claude transcript activity record types."""

from dataclasses import dataclass

from harness.impl.claude_code.canonical import records
from harness.impl.claude_code.canonical.transcript_model_core import TranscriptKind
from harness.impl.claude_code.ids import ClaudeCodeCallId


@dataclass(frozen=True)
class TeamMessageTranscriptRecord:
    """Represent team message transcript record."""

    sender: str
    body: str
    kind: TranscriptKind = TranscriptKind.TEAM_MESSAGE


@dataclass(frozen=True)
class TeammateIdleTranscriptRecord:
    """Represent teammate idle transcript record."""

    notifications: tuple[records.TeammateIdleNotificationDocument, ...]
    kind: TranscriptKind = TranscriptKind.ACTOR_ASSIGNMENT_FINISHED


@dataclass(frozen=True)
class ResultsTranscriptRecord:
    """Represent results transcript record."""

    blocks: tuple[records.ToolResultBlock, ...]
    tool_response: records.ToolResponse | records.ToolResponseBlocks | str | None
    texts: tuple[str, ...]
    meta: bool
    cancelled: bool
    interrupted: bool
    kind: TranscriptKind = TranscriptKind.TOOL_RESULTS


@dataclass(frozen=True)
class AssistantTranscriptRecord:
    """Represent assistant transcript record."""

    message: records.MessageObject | None
    kind: TranscriptKind = TranscriptKind.ASSISTANT


@dataclass(frozen=True)
class GoalTranscriptRecord:
    """Represent goal transcript record."""

    objective: str | None
    state: str
    reason: str | None
    kind: TranscriptKind = TranscriptKind.GOAL


@dataclass(frozen=True)
class BackgroundCommandCompletedTranscriptRecord:
    """Represent background command completed transcript record."""

    operation_id: ClaudeCodeCallId
    status: str
    output_file: str | None
    kind: TranscriptKind = TranscriptKind.BACKGROUND_COMMAND_COMPLETED
