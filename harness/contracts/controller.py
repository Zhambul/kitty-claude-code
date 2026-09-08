# Copyright (c) 2026 Zhambyl Yermagambet
"""Define harness control-handler contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from harness.models import controls as control_models


class ControlHandler(Protocol):
    """Handle one named harness control request."""

    def __call__(
        self,
        request: control_models.ControlRequest,
        control_context: control_models.ControlContext,
    ) -> control_models.ControlOutcome:
        """Handle one control request."""
        ...


@dataclass(frozen=True)
class HarnessController:
    """Dispatch control requests to named handlers."""

    handlers: Mapping[control_models.ControlName, ControlHandler]

    def execute(
        self,
        request: control_models.ControlRequest,
        control_context: control_models.ControlContext,
    ) -> control_models.ControlOutcome:
        """Execute one control request.

        Returns:
            The control outcome.

        """
        control_handler = self.handlers.get(request.control_name)
        if control_handler is None:
            return control_models.ControlResult(
                request_id=request.request_id,
                status=control_models.ControlAcknowledgement.REJECTED,
                reason="unsupported control",
            )
        return control_handler(request, control_context)
