# Copyright (c) 2026 Zhambyl Yermagambet
"""Map Claude Code session control handlers."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from harness.impl.claude_code.controls.controller_background import BackgroundHandler
from harness.impl.claude_code.controls.controller_commands import OpenRewindHandler
from harness.impl.claude_code.controls.controller_interrupt import InterruptHandler
from harness.impl.claude_code.controls.controller_rename import AutoNameSessionHandler, RenameSessionHandler
from harness.impl.claude_code.controls.controller_send import SendTextHandler
from harness.impl.claude_code.controls.controller_session_actions import CloseSessionHandler
from harness.models import controls as control_models

if TYPE_CHECKING:
    from collections.abc import Mapping

    from harness.contract import ControlHandler

SESSION_HANDLERS: Mapping[control_models.ControlName, ControlHandler] = MappingProxyType({
    control_models.ControlName.SEND_TEXT: SendTextHandler(),
    control_models.ControlName.INTERRUPT: InterruptHandler(),
    control_models.ControlName.BACKGROUND: BackgroundHandler(),
    control_models.ControlName.CLOSE_SESSION: CloseSessionHandler(),
    control_models.ControlName.RENAME_SESSION: RenameSessionHandler(),
    control_models.ControlName.AUTO_NAME_SESSION: AutoNameSessionHandler(),
    control_models.ControlName.OPEN_REWIND: OpenRewindHandler(),
})
