# Copyright (c) 2026 Zhambyl Yermagambet
"""Drive the verified steps of the Codex model picker."""

from collections.abc import Callable, Mapping
from types import MappingProxyType

from domain.ids import WindowId
from harness.impl.codex.controls.dialog import (
    STEP_TIMEOUT_SECONDS,
    Driver,
    OptionRow,
    _cursor_to,
    _poll,
    rows,
)

FOOT = "to confirm"
MODEL_STEP = "Select Model and Effort"
LEVEL_STEP = "Select Reasoning Level"
ADVANCED = "Advanced Reasoning"
MORE = "more reasoning"
CURRENT = "(current)"
ENTER_KEY = "enter"

EFFORT_LABEL: Mapping[str, str] = MappingProxyType({
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "xhigh": "Extra high",
    "extra_high": "Extra high",
    "extra-high": "Extra high",
    "max": "Max",
    "ultra": "Ultra",
})


class CodexModelError(Exception):
    """Report a failed model picker step."""

    def __init__(self, step: str, detail: str = "") -> None:
        """Initialize the error."""
        super().__init__(f"{step}: {detail}" if detail else step)
        self.step = step
        self.detail = detail


def _normalized_label(label: str) -> str:
    normalized_label = (label or "").lower()
    for marker in ("(current)", "(default)"):
        normalized_label = normalized_label.replace(marker, "")
    return normalized_label.strip()


def _await_step(
    driver: Driver,
    window_id: WindowId,
    marker: str,
    sleep: Callable[[float], None],
) -> str:
    screen, marker_visible = _poll(
        driver,
        window_id,
        lambda current_screen: marker in (current_screen or ""),
        STEP_TIMEOUT_SECONDS,
        sleep,
    )
    if not marker_visible:
        message = "step"
        raise CodexModelError(message, f"{marker!r} never appeared")
    return screen


def _select_option(
    driver: Driver,
    window_id: WindowId,
    target_number: str,
    sleep: Callable[[float], None],
) -> None:
    try:
        _cursor_to(driver, window_id, target_number, sleep)
    except Exception as error:
        message = "cursor"
        raise CodexModelError(message, str(error)) from error
    driver.send_key(window_id, ENTER_KEY)


def pick(
    driver: Driver,
    window_id: WindowId,
    header: str,
    wanted_label: str,
    sleep: Callable[[float], None],
) -> None:
    """Select one row from a picker step.

    Raises:
        CodexModelError: If the expected step or row is not available.

    """
    _await_step(driver, window_id, header, sleep)
    if wanted_label:
        screen = driver.read_text(window_id) or ""
        normalized_wanted = wanted_label.lower()
        option_row = next(
            (
                option_row
                for option_row in rows(screen)
                if _normalized_label(option_row.label) == normalized_wanted
                or normalized_wanted in option_row.label.lower()
            ),
            None,
        )
        if option_row is None:
            message = "row"
            raise CodexModelError(message, f"no {wanted_label!r} under {header!r}")
        _select_option(driver, window_id, option_row.num, sleep)
    else:
        driver.send_key(window_id, ENTER_KEY)


def pick_level(
    driver: Driver,
    window_id: WindowId,
    wanted_label: str,
    sleep: Callable[[float], None],
    *,
    strict: bool = True,
) -> None:
    """Select a reasoning level from the direct or advanced step.

    Raises:
        CodexModelError: If the expected step or row is not available.

    """
    _await_step(driver, window_id, LEVEL_STEP, sleep)
    if not wanted_label:
        driver.send_key(window_id, ENTER_KEY)
        return
    normalized_wanted = wanted_label.lower()
    screen = driver.read_text(window_id) or ""
    option_row = next(
        (option_row for option_row in rows(screen) if _normalized_label(option_row.label) == normalized_wanted),
        None,
    )
    if option_row is not None:
        _select_option(driver, window_id, option_row.num, sleep)
        return
    more_row = _more_reasoning_row(screen)
    if more_row is None:
        if not strict:
            driver.send_key(window_id, ENTER_KEY)
            return
        message = "row"
        raise CodexModelError(
            message,
            f"no {wanted_label!r} (nor a More-reasoning row) under {LEVEL_STEP!r}",
        )
    _select_option(driver, window_id, more_row.num, sleep)
    _await_step(driver, window_id, ADVANCED, sleep)
    screen = driver.read_text(window_id) or ""
    option_row = next(
        (option_row for option_row in rows(screen) if _normalized_label(option_row.label) == normalized_wanted),
        None,
    )
    if option_row is None:
        message = "row"
        raise CodexModelError(message, f"no {wanted_label!r} under {ADVANCED!r}")
    _select_option(driver, window_id, option_row.num, sleep)


def _more_reasoning_row(screen: str) -> OptionRow | None:
    for option_row in rows(screen):
        if MORE in option_row.label.lower():
            return option_row
    return None
