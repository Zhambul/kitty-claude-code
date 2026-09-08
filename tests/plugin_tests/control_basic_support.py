# Copyright (c) 2026 Zhambyl Yermagambet
"""Cross-harness canonical translation tests from native fixture shapes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Never

from harness.impl.claude_code.controls import (
    controller as claudecontroller,
    rewind_models,
)
from harness.models import controls as control_models
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.control_state_values import _BACKTRACK_STATE_TRANSITIONS

if TYPE_CHECKING:
    from pathlib import Path

    from harness.impl.codex.controls import controller as codexcontroller


def raise_confirm_menu_error(
    context: rewind_models.RewindContext,
    request: rewind_models.RewindRequest,
) -> Never:
    """Simulate a rewind confirmation failure.

    Raises:
        MenuError: Always, with the requested mode and window identity.

    """
    detail = f"{request.mode} in window {context.window_id}"
    msg = "confirm"
    raise rewind_models.MenuError(msg, detail)


def acknowledge_interrupt(
    calls: list[control_models.Interrupt],
    _interrupt_handler: claudecontroller.InterruptHandler | codexcontroller.InterruptHandler,
    request: control_models.Interrupt,
    _context: control_models.ControlContext,
) -> control_models.InterruptResult:
    """Record and acknowledge an interrupt request.

    Returns:
        An acknowledged result with corroboration set to True.

    """
    calls.append(request)
    return control_models.InterruptResult(
        request.request_id,
        control_models.ControlAcknowledgement.ACKNOWLEDGED,
        corroborated=True,
    )


def backtrack_next_state(state: str, pressed: tuple[str, ...]) -> str:
    """Return the state after a backtrack key press.

    Returns:
        The state after a backtrack key press.

    """
    for current_state, key, next_state in _BACKTRACK_STATE_TRANSITIONS:
        if state == current_state and pressed == (key,):
            return next_state
    return state


def clear_event_source(event_source: Path) -> None:
    """Write an empty event source file."""
    event_source.write_text("", encoding=fixture.TEXT_ENCODING)


def assert_acknowledged(
    response: control_models.ControlResult | control_models.MessageDeliveryResult,
) -> None:
    """Verify that one control response is acknowledged."""
    assert response.status == fixture.ACKNOWLEDGED


def session_event_source(temporary_directory: Path) -> Path:
    """Return the Claude session event source path.

    Returns:
        The Claude session event source path.

    """
    return temporary_directory / fixture.SESSION_JSONL_PATH


def source_name(event_source: Path) -> str:
    """Return the source name for one fixture event file.

    Returns:
        The source name for one fixture event file.

    """
    return str(event_source)
