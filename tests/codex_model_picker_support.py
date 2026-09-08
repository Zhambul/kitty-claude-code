# Copyright (c) 2026 Zhambyl Yermagambet
"""Fake Codex model picker for picker-driver tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from domain.ids import WindowId
from harness.impl.codex.controls import modeldialog

if TYPE_CHECKING:
    from harness.contract import ComposerDriver

type PickerStep = tuple[str, tuple[str, ...], int]

MODEL_ROWS = (
    "gpt-5.6-sol (default)   Latest frontier agentic coding model.",
    "gpt-5.6-terra           Balanced agentic coding model for everyday work.",
    "gpt-5.6-luna (current)  Fast and affordable agentic coding model.",
    "gpt-5.5                 Frontier model for complex coding, research, and real work.",
    "gpt-5.4                 Strong model for everyday coding.",
    "gpt-5.4-mini            Small, fast, and cost-efficient model for simpler tasks.",
    "gpt-5.3-codex-spark     Ultra-fast coding model.",
    "gpt-6-astra            Model for complex coding tasks.",
)
LEVEL_ROWS = (
    "Low               Fast responses with lighter reasoning",
    "Medium (default)  Balances speed and reasoning depth for everyday tasks",
    "High (current)    Greater reasoning depth for complex problems",
    "Extra high        Extra high reasoning depth for complex problems",
    "More reasoning…   Max consumes usage limits faster",
)
ADVANCED_ROWS = ("Max  For difficult problems when quality matters more than speed",)
STEPS: tuple[PickerStep, ...] = (
    ("Select Model and Effort", MODEL_ROWS, 2),
    ("Select Reasoning Level for gpt-5.6-luna", LEVEL_ROWS, 2),
)
ADVANCED = ("Advanced Reasoning", ADVANCED_ROWS, 0)


def _picker_row(number: int, label: str, cursor: int) -> str:
    selection_marker = "\u203a " if number - 1 == cursor else "  "
    return f"{selection_marker}{number}. {label}"


class FakePicker:
    """Represent a Codex model picker."""

    def __init__(self, steps: list[PickerStep] | None = None) -> None:
        """Initialize the object."""
        self.steps = list(STEPS if steps is None else steps)
        self.index = -1
        self.cursor = 0
        self.chosen: list[str] = []
        self._read_options: list[tuple[str, bool]] = []

    def paste_text(self, _window: WindowId, text: str) -> bool:
        """Open the picker with its command.

        Returns:
            True after the picker opens.

        Raises:
            AssertionError: If the command is not the model command.

        """
        if text != "/model":
            message = "the fake picker only opens the model command"
            raise AssertionError(message)
        self.index = 0
        self.cursor = self.steps[0][2]
        return True

    def read_text(self, _window: WindowId, extent: str = "screen", *, ansi: bool = False) -> str:
        """Return the current picker screen.

        Returns:
            The picker screen text.

        """
        self._read_options.append((extent, ansi))
        if self.index < 0 or self.index >= len(self.steps):
            return "  gpt-5.6-luna high · ~/code/personal/baqylau"
        header, rows, _ = self.steps[self.index]
        lines = ["", f"  {header}", " ", *_picker_rows(rows, self.cursor)]
        lines += [" ", "  Press enter to confirm or esc to go back"]
        return "\n".join(lines)

    def send_key(self, _window: WindowId, *keys: str) -> bool:
        """Send picker keys.

        Returns:
            True after the keys are processed.

        """
        for key in keys:
            rows = self._current_rows()
            cursor = _moved_cursor(key, rows, self.cursor)
            if cursor is not None:
                self.cursor = cursor
            elif key == "enter":
                _confirm_picker_choice(self, rows)
        return True

    def append_advanced_reasoning(self, rows: tuple[str, ...]) -> None:
        """Add the advanced step when its row is selected."""
        header = self.steps[self.index][0]
        if header.startswith("Select Reasoning") and "More reasoning" in rows[self.cursor]:
            self.steps.append(ADVANCED)

    def _current_rows(self) -> tuple[str, ...]:
        if self.index < 0 or self.index >= len(self.steps):
            return ()
        return self.steps[self.index][1]


def _moved_cursor(key: str, rows: tuple[str, ...], cursor: int) -> int | None:
    if key == "down":
        return min(cursor + 1, len(rows) - 1)
    if key == "up":
        return max(cursor - 1, 0)
    return None


def _confirm_picker_choice(picker: FakePicker, rows: tuple[str, ...]) -> None:
    chosen_row = rows[picker.cursor]
    chosen_label = chosen_row.split("  ")[0].strip()
    picker.chosen.append(chosen_label)
    picker.append_advanced_reasoning(rows)
    picker.index += 1
    if picker.index < len(picker.steps):
        picker.cursor = picker.steps[picker.index][2]
        return
    picker.cursor = 0


def _picker_rows(rows: tuple[str, ...], cursor: int) -> tuple[str, ...]:
    """Render the rows for one picker screen.

    Returns:
        The rendered rows.

    """
    rendered_rows = []
    for number, label in enumerate(rows, start=1):
        rendered_rows.append(_picker_row(number, label, cursor))
    return tuple(rendered_rows)


def run_picker(
    model: str = "",
    effort: str | None = "",
) -> tuple[FakePicker, modeldialog.ModelSelectionOutcome]:
    """Run the model picker driver.

    Returns:
        The picker and its outcome.

    """
    picker = FakePicker()
    result = modeldialog.set_model_effort(
        cast("ComposerDriver", picker),
        WindowId("win"),
        model=model,
        effort=effort,
        sleep=lambda _seconds: None,
    )
    return picker, result
