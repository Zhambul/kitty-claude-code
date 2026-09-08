# Copyright (c) 2026 Zhambyl Yermagambet
"""Select plan choices by their user-visible labels."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.common.models.values.plan_choice import PlanChoiceResponse


def matches(choices: tuple[PlanChoiceResponse, ...], label: str) -> list[PlanChoiceResponse]:
    """Return approval choices with a matching label.

    Returns:
        The matching approval choices.

    """
    return [choice for choice in choices if not choice.feedback and label_contains(label, choice.label)]


def label_contains(label: str, choice_label: str) -> bool:
    """Return true when a choice label contains text.

    Returns:
        True when the choice label contains the text.

    """
    return label.casefold() in choice_label.casefold()
