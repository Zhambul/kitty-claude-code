# Copyright (c) 2026 Zhambyl Yermagambet
"""Expose Claude Code controls."""

from harness.contract import HarnessController
from harness.impl.claude_code.controls import (
    askdialog as askdialog,
    confirmdialog as confirmdialog,
    plandialog as plandialog,
    tui as tui,
)
from harness.impl.claude_code.controls.controller_handler_registry import HANDLERS
from harness.impl.claude_code.controls.controller_interrupt import InterruptHandler as InterruptHandler
from harness.impl.claude_code.controls.controller_native_state import native_text_state as native_text_state
from harness.impl.claude_code.controls.controller_values import (
    NATIVE_TEXT_QUEUED as NATIVE_TEXT_QUEUED,
    NATIVE_TEXT_SENT as NATIVE_TEXT_SENT,
)

controller = HarnessController(HANDLERS)
