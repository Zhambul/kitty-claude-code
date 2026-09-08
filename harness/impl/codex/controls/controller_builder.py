# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex control builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.contract import ControlHandler, HarnessController
from harness.impl.codex.controls.controller_dependencies import rewind_continuity
from harness.impl.codex.controls.controller_handler_registry import HANDLERS
from harness.impl.codex.controls.controller_rename_session import RenameSessionHandler
from harness.impl.codex.controls.controller_send import SendTextHandler
from harness.models import controls as control_models

if TYPE_CHECKING:
    from collections.abc import Mapping

    from harness.impl.codex.canonical import title
    from harness.runtime import HarnessRuntimeConfig


def build_controller(
    title_repository: title.CodexThreadTitleRepository,
    harness_runtime_config: HarnessRuntimeConfig,
) -> HarnessController:
    """Build controller.

    Returns:
        The harness controller.

    """
    handlers: Mapping[control_models.ControlName, ControlHandler] = {
        **HANDLERS,
        control_models.ControlName.SEND_TEXT: SendTextHandler(
            harness_runtime_config,
            rewind_continuity,
            title_repository,
        ),
        control_models.ControlName.RENAME_SESSION: RenameSessionHandler(title_repository),
    }
    return HarnessController(handlers)


controller = HarnessController(HANDLERS)
