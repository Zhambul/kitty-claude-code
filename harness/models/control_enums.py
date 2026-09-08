# Copyright (c) 2026 Zhambyl Yermagambet
"""Define control vocabulary enumerations."""

from __future__ import annotations

from enum import StrEnum


class TitleWriteOutcome(StrEnum):
    """Identify the native title write result."""

    RENAMED = "renamed"
    UNSUPPORTED = "unsupported"
    UNAVAILABLE = "unavailable"


class AnswerDecision(StrEnum):
    """Identify the requested question action."""

    ANSWER = "answer"
    DISCUSS = "discuss"


class ControlAcknowledgement(StrEnum):
    """Identify the control acknowledgement state."""

    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"
    INDETERMINATE = "indeterminate"


class MessageDeliveryStatus(StrEnum):
    """Identify where the harness delivered a message."""

    QUEUED = "queued"
    SENT = "sent"


class ConfirmationOutcome(StrEnum):
    """Identify the command confirmation result."""

    CONFIRMED = "confirmed"
    NOT_NEEDED = "not_needed"
    FAILED = "failed"


class ControlName(StrEnum):
    """Identify one supported control request."""

    SEND_TEXT = "send_text"
    INTERRUPT = "interrupt"
    BACKGROUND = "background"
    CLOSE_SESSION = "close_session"
    RENAME_SESSION = "rename_session"
    AUTO_NAME_SESSION = "auto_name_session"
    OPEN_REWIND = "open_rewind"
    APPLY_REWIND = "apply_rewind"
    COMPACT = "compact"
    SELECT_MODEL = "select_model"
    SELECT_EFFORT = "select_effort"
    ANSWER_QUESTION = "answer_question"
    READ_PLAN_CHOICES = "read_plan_choices"
    DECIDE_PLAN = "decide_plan"
