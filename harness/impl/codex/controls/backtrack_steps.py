# Copyright (c) 2026 Zhambyl Yermagambet
"""Codex transcript backtrack steps."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from harness.impl.codex.controls import (
    backtrack_errors,
    backtrack_screen,
    backtrack_waiters,
    composer,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from domain.ids import WindowId
    from harness.impl.codex.controls.composer import ComposerControlDriver as Driver

SCREEN_TAIL_CHARACTER_LIMIT = 1_200
TARGET_STEP = "target"
CLEAR_STEP = "clear"
SELECT_STEP = "select"
RESTORE_STEP = "restore"


def drive(
    driver: Driver,
    window_id: WindowId,
    target: str,
    *,
    newer_prompt_count: int,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    """Select one named prompt in Codex's native transcript and edit it.

    Raises:
        BacktrackError: If a required backtrack step fails.

    """
    if newer_prompt_count < 0:
        raise backtrack_errors.BacktrackError(TARGET_STEP, "newer prompt count must not be negative")
    _open_transcript(driver, window_id, sleep)
    _select_target(driver, window_id, target, newer_prompt_count, sleep)
    _restore_target(driver, window_id, target, sleep)


def _open_transcript(driver: Driver, window_id: WindowId, sleep: Callable[[float], None]) -> None:
    _clear_composer(driver, window_id, sleep)
    backtrack_waiters.send_escape(driver, window_id, "the first escape was not delivered")
    backtrack_waiters.require_screen(
        lambda: driver.read_text(window_id),
        lambda screen: backtrack_screen.ESCAPE_HINT in (screen or ""),
        sleep,
        "the edit hint did not appear",
    )
    backtrack_waiters.send_escape(driver, window_id, "the second escape was not delivered")
    backtrack_waiters.require_screen(
        lambda: driver.read_text(window_id),
        backtrack_screen.transcript_open,
        sleep,
        "the transcript did not appear",
    )


def _clear_composer(driver: Driver, window_id: WindowId, sleep: Callable[[float], None]) -> None:
    try:
        composer.clear(driver, window_id, sleep=sleep)
    except composer.ComposerError as error:
        raise backtrack_errors.BacktrackError(CLEAR_STEP, str(error)) from error


def _select_target(
    driver: Driver,
    window_id: WindowId,
    target: str,
    newer_prompt_count: int,
    sleep: Callable[[float], None],
) -> None:
    for _ in range(newer_prompt_count):
        if not driver.send_key(window_id, "left"):
            raise backtrack_errors.BacktrackError(SELECT_STEP, "a left arrow was not delivered")
        sleep(backtrack_waiters.POLL_SECONDS)
    selected = backtrack_waiters.wait_for(
        lambda: backtrack_waiters.selection_screen(driver, window_id),
        lambda screen: backtrack_screen.selected_prompt(screen, target),
        sleep,
    )
    if selected is None:
        observed = backtrack_screen.plain_screen(
            backtrack_waiters.selection_screen(driver, window_id) or "",
        )
        transcript_tail = observed[-SCREEN_TAIL_CHARACTER_LIMIT:]
        raise backtrack_errors.BacktrackError(
            SELECT_STEP,
            f"the named prompt is not selected; transcript={transcript_tail!r}",
        )


def _restore_target(
    driver: Driver,
    window_id: WindowId,
    target: str,
    sleep: Callable[[float], None],
) -> None:
    if not driver.send_key(window_id, "enter"):
        raise backtrack_errors.BacktrackError(RESTORE_STEP, "enter was not delivered")
    restored = backtrack_waiters.wait_for(
        lambda: driver.read_text(window_id),
        lambda screen: backtrack_screen.restored_draft(screen, target),
        sleep,
        timeout_seconds=backtrack_waiters.RESTORE_TIMEOUT_SECONDS,
    )
    if restored is None:
        raise backtrack_errors.BacktrackError(RESTORE_STEP, "the named prompt did not become the draft")
