# Copyright (c) 2026 Zhambyl Yermagambet
"""Own the complete Codex control handler registry."""

from collections.abc import Mapping
from types import MappingProxyType

from harness.contract import ControlHandler
from harness.impl.codex.controls.controller_conversation_handlers import CONVERSATION_HANDLERS
from harness.impl.codex.controls.controller_decision_handlers import DECISION_HANDLERS
from harness.models import controls as control_models

HANDLERS: Mapping[control_models.ControlName, ControlHandler] = MappingProxyType({
    **CONVERSATION_HANDLERS,
    **DECISION_HANDLERS,
})
