# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex conversation control handlers."""

from types import MappingProxyType

from harness.impl.codex.canonical import title
from harness.impl.codex.controls.controller_close_session import CloseSessionHandler
from harness.impl.codex.controls.controller_compact import CompactHandler
from harness.impl.codex.controls.controller_dependencies import DEFAULT_RUNTIME_CONFIG, rewind_continuity
from harness.impl.codex.controls.controller_interrupt import InterruptHandler
from harness.impl.codex.controls.controller_rename_session import RenameSessionHandler
from harness.impl.codex.controls.controller_send import SendTextHandler
from harness.models import controls as control_models

CONVERSATION_HANDLERS = MappingProxyType({
    control_models.ControlName.SEND_TEXT: SendTextHandler(
        DEFAULT_RUNTIME_CONFIG,
        rewind_continuity,
        title.titles,
    ),
    control_models.ControlName.INTERRUPT: InterruptHandler(),
    control_models.ControlName.CLOSE_SESSION: CloseSessionHandler(),
    control_models.ControlName.RENAME_SESSION: RenameSessionHandler(title.titles),
    control_models.ControlName.COMPACT: CompactHandler(),
})
