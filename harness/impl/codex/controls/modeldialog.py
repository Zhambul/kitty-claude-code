# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the modeldialog module."""

# harness/impl/codex/controls/modeldialog.py — drive codex's interactive /model picker.
#
# codex has NO `/model <arg>` and NO `/effort` — model AND reasoning effort are
# both set through ONE interactive 3-step picker (`/model`), so the dashboard's
# ✦ model / ✧ effort buttons are driven here rather than by a slash-command
# paste. The sibling of harness/impl/codex/controls/dialog.py (ask) and plandialog.py (plan):
# the same numbered-row / `>`-cursor / `enter to confirm` geometry, every step
# screen-verified. It lives in the PLUGIN because codex's `model`/`effort`
# HostControl gestures drive it and the layering rule forbids a plugin importing
# the dashboard.
#
# The picker (verified live, codex-cli 0.147.0):
#   Step 1  "Select Model and Effort"            → the numbered model list
#                                                   (gpt-5.6-sol … gpt-5.3-codex-spark)
#   Step 2  "Select Reasoning Level for <model>" → Low/Medium/High/Extra high +
#                                                   a "More reasoning…" row
#   Step 2a "Advanced Reasoning"                 → what that row opens (Max)
#
# 0.144.1 opened on a THIRD screen in front of these — a "Select Model" step
# whose 'All models' row browsed the full list — and this driver waited for it.
# 0.147.0 removed it, and the wait SUCCEEDED anyway: "Select Model" is a
# substring of "Select Model and Effort", and the step detector tests
# `needle in screen`. So the driver matched the model list, believed it was one
# screen earlier, looked for an 'All models' row that no longer exists, and
# raised in 379ms with the picker left open on screen (measured, session
# 01a0038a: `control` audit row, status indeterminate, reason "row: no 'all
# models' under 'Select Model'"). The lesson is the one docs/styleguide.md
# already states about screen markers: a detector that is a PREFIX of the next
# step's cannot fail safe, so the step names here must stay mutually disjoint —
# "Select Model and Effort" and "Select Reasoning Level" are.
#
# Every step's footer is "Press enter to confirm or esc to go back". codex
# couples the two axes: switching MODEL lands on step 3 at that model's DEFAULT
# effort, so the ✦ button changes model + accepts the default (codex's own
# behaviour), and the ✧ button keeps the CURRENT model (its `(current)` row) and
# changes only the level.
import time
from collections.abc import Callable
from enum import StrEnum

from domain.ids import WindowId
from harness.impl.codex.controls import modeldialog_steps
from harness.impl.codex.controls.dialog import STEP_TIMEOUT_SECONDS, Driver, _poll
from harness.impl.codex.model import CODEX_MODELS, CodexEffort

LEVEL_STEP = modeldialog_steps.LEVEL_STEP

# step headers + the shared footer (disjoint from the ask "to submit" / plan
# "Implement this plan?" detectors)
# the ✧ effort tokens the dashboard sends → the on-screen reasoning-level LABEL
# (matched EXACTLY, not as a substring, so 'high' can't hit 'Extra high'). Also
# the map the ✦ model gesture runs the CURRENT effort (from read.context) through
# to PRESERVE it across a model switch, so a few spelling aliases for the higher
# levels are included defensively (the config token codex records for them is
# less certain than low/medium/high) — an unmapped token falls back to the
# picker default, never a wrong level.
# the codex models the ✦ menu offers, in the picker's own order (label == the
# picker row + the -m arg). Read off 0.147.0's model step.
MODEL_CHOICES = CODEX_MODELS
EFFORT_CHOICES = tuple(CodexEffort)


class ModelSelectionOutcome(StrEnum):
    """Represent model selection outcome."""

    SET = "set"


def set_model_effort(
    driver: Driver,
    window_id: WindowId,
    model: str = "",
    effort: str | None = "",
    sleep: Callable[[float], None] = time.sleep,
) -> ModelSelectionOutcome:
    """Set model effort.

    Drive the /model picker. `model` = a codex model id (✦ — changes model,
        accepts that model's DEFAULT effort); `effort` = a token in EFFORT_CHOICES
        (✧ — keeps the CURRENT model, changes only the level). Exactly one is set by
        a given gesture. Opens the picker itself (paste `/model`), which lands
        STRAIGHT on the model step, then model→level, verified. Returns
        {"set": True}; raises CodexModelError on any unverified step.

    Returns:
        The model selection outcome.

    Raises:
        CodexModelError: If the Codex model dialog fails.

    """
    if not driver.paste_text(window_id, "/model"):
        message = "open"
        raise modeldialog_steps.CodexModelError(message, "/model paste refused")
    # Step 1 — the model: the chosen one (✦), else keep the current (✧).
    modeldialog_steps.pick(
        driver,
        window_id,
        modeldialog_steps.MODEL_STEP,
        model or modeldialog_steps.CURRENT,
        sleep,
    )
    # Step 2 — the reasoning level: the chosen one (✧), else the model's default
    # (✦ accepts the pre-selected row with a bare Enter). Handles the `More
    # reasoning…` sub-step the top level sits behind. When a MODEL is
    # being set the effort is a PRESERVE (best-effort — strict=False: a target
    # model that lacks the old level gets its default, never a failed switch);
    # when only the effort is set it is an EXPLICIT ✧ choice (strict).
    wanted_label = modeldialog_steps.EFFORT_LABEL.get(effort, "") if effort else ""
    modeldialog_steps.pick_level(driver, window_id, wanted_label, sleep, strict=not model)
    _, picker_closed = _poll(
        driver,
        window_id,
        lambda current_screen: modeldialog_steps.FOOT not in (current_screen or ""),
        STEP_TIMEOUT_SECONDS,
        sleep,
    )
    if not picker_closed:
        message = "submit"
        raise modeldialog_steps.CodexModelError(message, "picker still open after the level")
    return ModelSelectionOutcome.SET
