# Copyright (c) 2026 Zhambyl Yermagambet
"""Build the Claude Code control handler registry."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from harness.impl.claude_code.controls.controller_decision_handlers import DECISION_HANDLERS
from harness.impl.claude_code.controls.controller_session_handlers import SESSION_HANDLERS

if TYPE_CHECKING:
    from collections.abc import Mapping

    from harness.contract import ControlHandler
    from harness.models import controls as control_models

HANDLERS: Mapping[control_models.ControlName, ControlHandler] = MappingProxyType({
    **SESSION_HANDLERS,
    **DECISION_HANDLERS,
})
