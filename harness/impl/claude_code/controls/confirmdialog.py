# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the confirmdialog module."""

# harness/impl/claude_code/controls/confirmdialog.py — auto-answer the switch-confirm menu that
# /model and /effort can open.
# Sibling of rewindmenu.py/askdialog.py in philosophy — every key press is
# preceded by READING THE SCREEN back — but deliberately not unified with
# either: this dialog is a bare two-option Yes/No menu with none of their
# anatomy.
#
# Newer Claude Code builds (observed live 2026-07-18, after the v2.1.214
# measurements) no longer always apply `/effort <level>` / `/model <arg>`
# outright: when switching would invalidate the conversation's prompt cache
# the TUI opens a numbered are-you-sure menu ("Change effort level?" …
# "> 1. Yes, switch to low / 2. No, go back") and the command does NOTHING
# until it is answered — so a web quick-command click looked dead. The web
# button IS the user's consent, so the server presses the menu's own Yes.
#
# Detection is by SHAPE, not header text: a >-cursored numbered option list
# in the screen TAIL whose labels lead with Yes/No. Anchoring on the measured
# effort header would silently miss the model variant (unmeasured wording) —
# and the cursor-on-a-numbered-row + Yes-and-No pair never matches scrollback
# prose or the bare composer prompt (a column-0 `>` with no `N.` after it).
import time
from collections.abc import Callable
from dataclasses import dataclass

from domain.ids import WindowId
from harness.impl.claude_code.controls import numberedmenu, screen_driver as screendrive
from harness.impl.claude_code.controls.screen_protocols import ScreenDriver

OPEN_TIMEOUT_S = 4.0  # paste delivered → menu visible (slash-cmd latency);
#                        no menu inside this window = the switch applied
#                        silently (same level, no cache — a clean non-event)
STEP_TIMEOUT_S = 2.0  # Yes digit pressed → menu gone
TAIL_LINES = 20  # the live menu sits at the screen bottom; anything
#                        higher is scrollback and must not match


class ConfirmError(screendrive.StepError):
    """Represent confirm error.

    The confirm menu appeared but would not close after Yes. .step names
        the failed step for the audit row; the menu is left as-is (it is the
        user's decision surface — never Escape it away).
    """


@dataclass(frozen=True)
class ConfirmOutcome:
    """confirm()'s report: whether a menu appeared, and which digit said Yes."""

    dialog: bool
    digit: str | None = None


def find_menu(screen: str) -> str | None:
    """Return the Yes digit when the screen contains a confirmation menu.

    Returns:
        The Yes digit when the screen contains a confirmation menu.

    """
    tail = "\n".join((screen or "").splitlines()[-TAIL_LINES:])
    options = numberedmenu.rows(tail)
    affirmative_digit = next(
        (row.digit for row in options if row.label.casefold().startswith("yes")),
        None,
    )
    negative_digit = next(
        (row.digit for row in options if row.label.casefold().startswith("no")),
        None,
    )
    cursor_digit = next((row.digit for row in options if row.cursor), None)
    if not affirmative_digit or not negative_digit or not cursor_digit:
        return None
    return affirmative_digit


def confirm(screen_driver: ScreenDriver, win: WindowId, sleep: Callable[[float], None] = time.sleep) -> ConfirmOutcome:
    """Return the confirm.

    Watch window `win` for the switch-confirm menu a just-pasted /model or
        /effort may open; press its own Yes digit, verified. Returns
        {"dialog": False} when no menu appeared (the switch applied outright) or
        {"dialog": True, "digit": d} once the answered menu closes; raises
        ConfirmError when the menu stays open after Yes.

    Returns:
        Confirm.

    """
    screen, menu_found = screendrive.poll_until(screen_driver, win, find_menu, OPEN_TIMEOUT_S, sleep)
    if not menu_found:
        return ConfirmOutcome(dialog=False)
    menu_digit = find_menu(screen)
    if menu_digit is None:
        # The menu closed between the poll that saw it and this re-read —
        # the switch applied on its own. Pressing a key here would land in
        # the composer.
        return ConfirmOutcome(dialog=False)
    _select_menu(screen_driver, win, screen, menu_digit, sleep)
    _ensure_menu_closed(screen_driver, win, sleep)
    return ConfirmOutcome(dialog=True, digit=menu_digit)


def _select_menu(
    screen_driver: ScreenDriver,
    win: WindowId,
    screen: str,
    menu_digit: str,
    sleep: Callable[[float], None],
) -> None:
    try:
        numberedmenu.select(
            numberedmenu.SelectionContext(
                screen_driver,
                win,
                lambda: numberedmenu.rows(
                    "\n".join(
                        (screen_driver.read_text(win) or "").splitlines()[-TAIL_LINES:],
                    ),
                ),
                sleep,
                screendrive.POLL_SECONDS,
            ),
            menu_digit,
        )
    except numberedmenu.SelectionError as error:
        message = "select"
        raise ConfirmError(message, str(error), screen) from error


def _ensure_menu_closed(
    screen_driver: ScreenDriver,
    win: WindowId,
    sleep: Callable[[float], None],
) -> None:
    closed_screen, menu_closed = screendrive.poll_until(
        screen_driver,
        win,
        lambda screen_text: not find_menu(screen_text),
        STEP_TIMEOUT_S,
        sleep,
    )
    if not menu_closed:
        message = "close"
        raise ConfirmError(message, "confirm menu still open after Yes", closed_screen)
