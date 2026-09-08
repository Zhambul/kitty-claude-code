# Copyright (c) 2026 Zhambyl Yermagambet
"""Define common context and basic control request values."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from domain.event_work import PlanProposed, QuestionAsked
from domain.ids import RequestId, SessionId, WindowId
from harness.models.control_enums import ControlName
from harness.models.session import Session
from terminal.contract import TerminalPlugin


@dataclass(frozen=True)
class ControlContext:
    """Represent the state available for one control."""

    session: Session
    terminal: TerminalPlugin
    terminal_window_id: WindowId | None
    current_effort: str | None
    lead_active: bool
    pending_attention: QuestionAsked | PlanProposed | None


@dataclass(frozen=True)
class ControlTarget:
    """Identify the session and request for one control."""

    session_id: SessionId
    request_id: RequestId


@dataclass(frozen=True)
class AttachmentReference:
    """Describe one local attachment."""

    local_path: str
    display_name: str
    media_type: str | None = None


@dataclass(frozen=True)
class SendText(ControlTarget):
    """Request text delivery to one session."""

    control_name: ClassVar[ControlName] = ControlName.SEND_TEXT
    text: str
    attachments: tuple[AttachmentReference, ...] = ()
    replace_terminal_draft: bool = False


@dataclass(frozen=True)
class Interrupt(ControlTarget):
    """Request interruption of the active turn."""

    control_name: ClassVar[ControlName] = ControlName.INTERRUPT


@dataclass(frozen=True)
class Background(ControlTarget):
    """Request backgrounding of the active command."""

    control_name: ClassVar[ControlName] = ControlName.BACKGROUND


@dataclass(frozen=True)
class CloseSession(ControlTarget):
    """Request closure of one session."""

    control_name: ClassVar[ControlName] = ControlName.CLOSE_SESSION
