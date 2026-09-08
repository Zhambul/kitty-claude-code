# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert generic control outcomes to non-message results."""

from __future__ import annotations

from harness.models import controls as control_models


def control_result(outcome: control_models.ControlOutcome) -> control_models.ControlResult:
    """Return a non-message result or fail for a message result.

    Returns:
        The non-message control result.

    Raises:
        TypeError: If the outcome is a message delivery result.

    """
    if isinstance(outcome, control_models.MessageDeliveryResult):
        message = "non-message control returned a message delivery result"
        raise TypeError(message)
    return outcome
