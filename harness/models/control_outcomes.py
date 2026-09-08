# Copyright (c) 2026 Zhambyl Yermagambet
"""Define control outcome values."""

from __future__ import annotations

from dataclasses import dataclass

from domain.ids import RequestId
from harness.models.control_enums import ConfirmationOutcome, ControlAcknowledgement, MessageDeliveryStatus


@dataclass(frozen=True)
class ControlResult:
    """Represent a generic control result."""

    request_id: RequestId
    status: ControlAcknowledgement
    reason: str | None = None


@dataclass(frozen=True)
class DurableTitleResult(ControlResult):
    """Represent a title written to native harness storage."""


@dataclass(frozen=True)
class InterruptResult(ControlResult):
    """Represent an interrupt result."""

    restored_text: str = ""
    corroborated: bool = False


@dataclass(frozen=True)
class MessageDeliveryResult:
    """Represent harness delivery of one message."""

    request_id: RequestId
    status: MessageDeliveryStatus


@dataclass(frozen=True)
class CommandResult(ControlResult):
    """Represent a command result."""

    confirmation: ConfirmationOutcome | None = None


@dataclass(frozen=True)
class RewindResult(ControlResult):
    """Represent a rewind result."""

    restored_text: str = ""
    degraded: bool = False
