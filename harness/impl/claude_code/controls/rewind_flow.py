# Copyright (c) 2026 Zhambyl Yermagambet
"""Run the verified phases of a Claude Code rewind."""

from harness.impl.claude_code.controls import rewind_navigation, screen_driver as screen_actions, tui
from harness.impl.claude_code.controls.rewind_models import (
    MenuError,
    RewindContext,
    RewindOutcome,
    RewindRequest,
    mode_label,
)
from harness.impl.claude_code.controls.rewind_screen import (
    CODE_UNCHANGED,
    confirm_open,
    menu_open,
    menu_region,
    option_digit,
)

OPEN_TIMEOUT_SECONDS = 4.0
STEP_TIMEOUT_SECONDS = 2.0
KEY_GAP_SECONDS = 0.05
TARGET_PREVIEW_LENGTH = 80
NO_CHANGE_DETAIL = " — no code changes to revert at that checkpoint"


def open_menu(rewind_context: RewindContext) -> None:
    """Clear the composer and open its rewind menu.

    Raises:
        MenuError: If the command fails or the menu does not open.

    """
    rewind_context.screen_driver.send_key(rewind_context.window_id, "ctrl+u")
    rewind_context.screen_driver.send_key(rewind_context.window_id, "ctrl+k")
    rewind_context.sleep(rewind_navigation.POLL_SECONDS)
    delivered, _clipboard_cleared = tui.type_command(rewind_context.screen_driver, rewind_context.window_id, "/rewind")
    if not delivered:
        message = "send"
        raise MenuError(message, "/rewind not delivered")
    screen, menu_found = screen_actions.poll_until(
        rewind_context.screen_driver,
        rewind_context.window_id,
        menu_open,
        OPEN_TIMEOUT_SECONDS,
        rewind_context.sleep,
    )
    if not menu_found:
        rewind_navigation.bail(rewind_context)
        message = "open"
        raise MenuError(message, "checkpoint menu never appeared", screen)


def find_checkpoint(rewind_context: RewindContext, rewind_request: RewindRequest) -> int:
    """Use the hint, then find the target checkpoint by its text.

    Returns:
        The number of navigation steps.

    """
    rewind_navigation.apply_hint(rewind_context, rewind_request.hint_steps, KEY_GAP_SECONDS)
    found, steps = rewind_navigation.scan_both(rewind_context, rewind_request.target)
    if found:
        return steps
    return rewind_navigation.raise_missing(rewind_context, rewind_request.target, TARGET_PREVIEW_LENGTH)


def confirm_screen(rewind_context: RewindContext, requested_label: str, mode: str) -> str:
    """Open the confirmation menu and reveal the requested option.

    Returns:
        The confirmation screen text.

    Raises:
        MenuError: If the requested option does not appear.

    """
    rewind_context.screen_driver.send_key(rewind_context.window_id, "enter")
    screen, option_found = screen_actions.poll_until(
        rewind_context.screen_driver,
        rewind_context.window_id,
        confirm_open,
        STEP_TIMEOUT_SECONDS,
        rewind_context.sleep,
    )
    if option_found:
        screen, option_found = rewind_navigation.scan_confirm(rewind_context, requested_label, mode, "down")
    if not option_found and confirm_open(screen):
        screen, option_found = rewind_navigation.scan_confirm(rewind_context, requested_label, mode, "up")
    if not option_found:
        rewind_navigation.bail(rewind_context)
        message = "confirm"
        raise MenuError(message, "requested restore option never appeared", screen)
    return screen


def restore_choice(rewind_context: RewindContext, screen: str, rewind_request: RewindRequest) -> tuple[str, bool]:
    """Return the exact restore digit and whether the choice degrades.

    Returns:
        The restore digit and the degradation state.

    Raises:
        MenuError: If the requested option is not available.

    """
    requested_label = mode_label(rewind_request.mode) or ""
    digit = option_digit(screen, requested_label)
    code_unchanged = CODE_UNCHANGED in menu_region(screen)
    if digit:
        return digit, False
    if rewind_request.mode == "both" and code_unchanged:
        conversation_label = mode_label("conversation") or ""
        digit = option_digit(screen, conversation_label)
        if digit:
            return digit, True
    rewind_navigation.bail(rewind_context)
    message = "option"
    raise MenuError(
        message,
        "{!r} not offered here{}".format(
            requested_label,
            NO_CHANGE_DETAIL if code_unchanged else "",
        ),
        screen,
    )


def close_menu(rewind_context: RewindContext, digit: str) -> None:
    """Select the restore digit and verify that the menu closes.

    Raises:
        MenuError: If selection fails or the menu stays open.

    """
    rewind_navigation.select_confirm(rewind_context, digit)
    screen, menu_closed = screen_actions.poll_until(
        rewind_context.screen_driver,
        rewind_context.window_id,
        lambda screen_text: not menu_region(screen_text),
        STEP_TIMEOUT_SECONDS,
        rewind_context.sleep,
    )
    if not menu_closed:
        rewind_navigation.bail(rewind_context)
        message = "close"
        raise MenuError(message, "menu still open after selecting", screen)


def drive_menu(rewind_context: RewindContext, rewind_request: RewindRequest) -> RewindOutcome:
    """Run all verified rewind menu phases.

    Returns:
        The completed rewind result.

    Raises:
        MenuError: If the rewind mode is not valid.

    """
    requested_label = mode_label(rewind_request.mode)
    if requested_label is None:
        message = "bad-mode"
        raise MenuError(message, rewind_request.mode)
    open_menu(rewind_context)
    steps = find_checkpoint(rewind_context, rewind_request)
    return complete_rewind(rewind_context, rewind_request, requested_label, steps)


def complete_rewind(
    rewind_context: RewindContext,
    rewind_request: RewindRequest,
    requested_label: str,
    steps: int,
) -> RewindOutcome:
    """Confirm one found checkpoint and close the rewind menu.

    Returns:
        The completed rewind result.

    """
    screen = confirm_screen(rewind_context, requested_label, rewind_request.mode)
    choice = restore_choice(rewind_context, screen, rewind_request)
    close_menu(rewind_context, choice[0])
    return RewindOutcome(steps, *choice)
