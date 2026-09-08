# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the plandialog module."""

# harness/impl/codex/controls/plandialog.py — drive codex's plan-mode DECISION picker.
#
# The codex analog of harness/impl/claude_code/controls/plandialog.py, and the sibling of
# harness/impl/codex/controls/dialog.py (the request_user_input driver). After codex presents
# a plan in Plan mode it shows a numbered decision picker on screen — the same
# `N. label  description` / `>` cursor geometry the /model picker uses (so this
# reuses dialog.py's `rows`/`_cursor_to`/`_poll`), but a DIFFERENT header +
# footer:
#
#     Implement this plan?
#   > 1. Yes, implement this plan          Switch to Default and start coding.
#     2. Yes, clear context and implement  Fresh thread. Context: 3% used.
#     3. No, stay in Plan mode             Continue planning with the model.
#     Press enter to confirm or esc to go back
#
# There is NO plan record for the decision itself (it is pure TUI, no rollout
# row until decided), so — like the ask driver — the ONLY way to answer from the
# web is to drive the picker, every step screen-verified. It lives in the PLUGIN
# (not beside harness/impl/claude_code/controls/plandialog.py) because codex's `plan` HostControl gesture
# drives it and the layering rule forbids a plugin importing the dashboard: the
# whole gesture, driver included, sits behind HostControl and the dashboard only
# calls host.plan (docs/codex.md *Plan mode*).
#
# Verified live (codex-cli 0.144.1) against a real plan-mode session.
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from domain.ids import WindowId
from harness.impl.codex.controls import plan_screen
from harness.impl.codex.controls.dialog import (
    STEP_TIMEOUT_SECONDS,
    CodexAskError,
    Driver,
    _cursor_to,
    _poll,
)

# the decision picker's footer + header (distinct from the ask dialog's
# "submit answer" footer / "Question N/M" header) — the detectors that tell the
# plan picker apart from every other codex screen.
# the "keep planning" row's label stem — matched case-insensitively as a
# substring so wording drift ("No, stay in Plan mode" / "keep planning") still
# resolves the dismiss row; also what options() drops from the APPROVE set.
KEEP_PLANNING = "stay in plan mode"
OPEN_STEP = "open"
OPEN_ERROR = "no plan-decision picker on screen"


# The APPROVE rows the decision picker offers (verified live, codex-cli 0.144.1).
# Only the stable LABEL is declared — the trailing description varies (`Context:
# N% used`). The web plan card shows these as its decision buttons WITHOUT a
# screen read (the plan is proven pending read-side; these are static), and
# decide() re-reads + label-verifies the LIVE screen before pressing, so a codex
# wording drift fails SAFE (no press) rather than mis-deciding.
@dataclass(frozen=True)
class PlanOption:
    """Represent plan option."""

    digit: str
    label: str


class PlanOutcome(StrEnum):
    """Represent plan outcome."""

    DECIDED = "decided"
    DISMISSED = "dismissed"


class CodexPlanError(CodexAskError):
    """Represent codex plan error.

    A plan-decision step's expected screen never appeared. Reuses the ask
        driver's error shape (`.step` names it for the audit) — the picker is left
        EXACTLY as it was (never Escape-closed: codex's Esc goes BACK a step, so a
        blind Esc could dismiss into an ambiguous state), so a re-decide normalizes.
    """


def options(driver: Driver, window_id: WindowId) -> list[PlanOption]:
    """Return the options.

    The APPROVE options on the live picker as [{digit, label}] — every
        decision row EXCEPT the keep-planning row (which the card offers as its own
        'keep planning' button, mapped to dismiss). Read-only: no key is pressed.
        Raises CodexPlanError('open') when the picker isn't up (the plan resolved in
        the terminal — the card self-heals on the next read).

    Returns:
        Options.

    Raises:
        CodexPlanError: If the Codex plan dialog fails.

    """
    screen, picker_visible = _poll(
        driver,
        window_id,
        plan_screen.picker_open,
        STEP_TIMEOUT_SECONDS,
        time.sleep,
    )
    if not picker_visible:
        raise CodexPlanError(OPEN_STEP, OPEN_ERROR)
    plan_options: list[PlanOption] = []
    for option_row in plan_screen.option_rows(screen):
        if KEEP_PLANNING in option_row.label.lower():
            continue
        plan_options.append(PlanOption(option_row.num, option_row.label))
    return plan_options


def _decide_row(
    driver: Driver,
    window_id: WindowId,
    target_number: str,
    sleep: Callable[[float], None],
) -> None:
    """Decide row.

    Move the `>` cursor onto option `num` and ENTER, then verify the picker is
        GONE (the decision took). Raises CodexPlanError otherwise.

    Raises:
        CodexPlanError: If the Codex plan dialog fails.

    """
    _screen, picker_visible = _poll(
        driver,
        window_id,
        plan_screen.picker_open,
        STEP_TIMEOUT_SECONDS,
        sleep,
    )
    if not picker_visible:
        raise CodexPlanError(OPEN_STEP, OPEN_ERROR)
    try:
        _cursor_to(driver, window_id, target_number, sleep)
    except CodexAskError as error:
        message = "cursor"
        raise CodexPlanError(message, error.detail or str(error)) from error
    driver.send_key(window_id, "enter")
    _, picker_closed = _poll(
        driver,
        window_id,
        lambda current_screen: not plan_screen.picker_open(current_screen),
        STEP_TIMEOUT_SECONDS,
        sleep,
    )
    if not picker_closed:
        message = "submit"
        raise CodexPlanError(message, "picker still on screen after enter")


def decide(
    driver: Driver,
    window_id: WindowId,
    digit: str,
    label: str,
    sleep: Callable[[float], None] = time.sleep,
) -> PlanOutcome:
    """Decide.

    APPROVE the plan: press the decision row whose LABEL matches `label` (a
        case-insensitive substring — the same label-guard Claude's plandialog.decide
        uses, but keyed on the LABEL not the digit so codex reordering the rows can't
        press the wrong one; `digit` is advisory). Label drift ⇒ CodexPlanError, and
        nothing is pressed. Returns {"decided": True}.

    Returns:
        The plan outcome.

    Raises:
        CodexPlanError: If the Codex plan dialog fails.

    """
    screen = driver.read_text(window_id) or ""
    if not plan_screen.picker_open(screen):
        raise CodexPlanError(OPEN_STEP, OPEN_ERROR)
    wanted_label = (label or "").strip().lower()
    matching_row = next(
        (
            option_row
            for option_row in plan_screen.option_rows(screen)
            if wanted_label and wanted_label in option_row.label.strip().lower()
        ),
        None,
    )
    if matching_row is None:
        message = "label"
        raise CodexPlanError(message, f"no row matching {label!r} on screen (digit {digit})")
    _decide_row(driver, window_id, matching_row.num, sleep)
    return PlanOutcome.DECIDED


def dismiss(driver: Driver, window_id: WindowId, sleep: Callable[[float], None] = time.sleep) -> PlanOutcome:
    """Return the dismiss.

    KEEP PLANNING: pick the 'No, stay in Plan mode' row (an explicit choice,
        not an Esc — Esc only steps BACK). Returns {"dismissed": True}.

    Returns:
        Dismiss.

    Raises:
        CodexPlanError: If the Codex plan dialog fails.

    """
    screen, picker_visible = _poll(
        driver,
        window_id,
        plan_screen.picker_open,
        STEP_TIMEOUT_SECONDS,
        sleep,
    )
    if not picker_visible:
        raise CodexPlanError(OPEN_STEP, OPEN_ERROR)
    matching_row = next(
        (option_row for option_row in plan_screen.option_rows(screen) if KEEP_PLANNING in option_row.label.lower()),
        None,
    )
    if matching_row is None:
        message = "dismiss"
        raise CodexPlanError(message, "no keep-planning row on screen")
    _decide_row(driver, window_id, matching_row.num, sleep)
    return PlanOutcome.DISMISSED
