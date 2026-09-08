# Copyright (c) 2026 Zhambyl Yermagambet
"""Define session configuration control request values."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from domain.ids import MessageId
from harness.models.control_context import ControlTarget
from harness.models.control_enums import ControlName


@dataclass(frozen=True)
class RenameSession(ControlTarget):
    """Request a native session rename."""

    control_name: ClassVar[ControlName] = ControlName.RENAME_SESSION
    name: str


@dataclass(frozen=True)
class AutoNameSession(ControlTarget):
    """Request automatic session naming."""

    control_name: ClassVar[ControlName] = ControlName.AUTO_NAME_SESSION


@dataclass(frozen=True)
class OpenRewind(ControlTarget):
    """Request opening the rewind dialog."""

    control_name: ClassVar[ControlName] = ControlName.OPEN_REWIND


@dataclass(frozen=True)
class ApplyRewind(ControlTarget):
    """Request applying one rewind choice."""

    control_name: ClassVar[ControlName] = ControlName.APPLY_REWIND
    target_message_id: MessageId
    target_text: str
    newer_prompt_count: int
    mode: str


@dataclass(frozen=True)
class Compact(ControlTarget):
    """Request session compaction."""

    control_name: ClassVar[ControlName] = ControlName.COMPACT


@dataclass(frozen=True)
class SelectModel(ControlTarget):
    """Request a model selection."""

    control_name: ClassVar[ControlName] = ControlName.SELECT_MODEL
    model: str


@dataclass(frozen=True)
class SelectEffort(ControlTarget):
    """Request an effort selection."""

    control_name: ClassVar[ControlName] = ControlName.SELECT_EFFORT
    effort: str
