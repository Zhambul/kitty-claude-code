# Copyright (c) 2026 Zhambyl Yermagambet
"""Tests for the Codex model picker driver."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest

from domain.ids import WindowId
from harness.impl.codex.controls import modeldialog, modeldialog_steps
from tests.codex_model_picker_support import MODEL_ROWS, STEPS, FakePicker, run_picker

if TYPE_CHECKING:
    from harness.contract import ComposerDriver


def test_picker_opens_straight_on_model_step() -> None:
    """Verify the picker opens on the model step."""
    picker, result = run_picker(model="gpt-5.6-sol")

    assert result is modeldialog.ModelSelectionOutcome.SET
    assert picker.chosen == ["gpt-5.6-sol (default)", "High (current)"]
    assert picker.index >= len(STEPS)


def test_model_switch_preserves_current_level() -> None:
    """Verify a model switch preserves the current level."""
    picker, _ = run_picker(model="gpt-5.4", effort="low")

    assert picker.chosen == ["gpt-5.4", "Low"]


def test_an_effort_change_keeps_the_current_model() -> None:
    """Verify an effort change keeps the current model."""
    picker, _ = run_picker(effort="xhigh")

    assert picker.chosen == ["gpt-5.6-luna (current)", "Extra high"]


def test_top_level_is_reached_through_more() -> None:
    """Verify the top level uses the more-reasoning substep."""
    picker, _ = run_picker(effort="max")

    assert picker.chosen == ["gpt-5.6-luna (current)", "More reasoning…", "Max"]


def test_every_offered_model_is_row_picker() -> None:
    """Verify every offered model has a picker row."""
    model_names = [label.split("  ")[0] for label in MODEL_ROWS]
    listed = {name.replace(" (default)", "").replace(" (current)", "") for name in model_names}
    assert set(modeldialog.MODEL_CHOICES) == listed


def test_the_step_names_stay_mutually_disjoint() -> None:
    """Verify the step names do not overlap."""
    assert modeldialog_steps.MODEL_STEP not in modeldialog_steps.LEVEL_STEP
    assert modeldialog_steps.LEVEL_STEP not in modeldialog_steps.MODEL_STEP


def test_missing_level_is_named_rather() -> None:
    """Verify a missing level is named rather than guessed."""
    picker = FakePicker()
    with pytest.raises(modeldialog_steps.CodexModelError) as caught:
        modeldialog.set_model_effort(
            cast("ComposerDriver", picker),
            window_id=WindowId("win"),
            effort="ultra",
            sleep=lambda _seconds: None,
        )
    assert caught.value.step == "row"
