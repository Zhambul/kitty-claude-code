# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex control plans."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.contract import ControlHandler
from harness.impl.codex.controls import plandialog
from harness.impl.codex.controls.controller_values import SESSION_NOT_LIVE_REASON
from harness.models import controls as control_models
from harness.services.terminal_driver import TerminalDriver

if TYPE_CHECKING:
    from domain.ids import WindowId


class ReadPlanChoicesHandler(ControlHandler):
    """Represent read plan choices handler."""

    def __call__(
        self,
        request: control_models.ControlRequest,
        control_context: control_models.ControlContext,
    ) -> control_models.PlanChoicesResult:
        """Handle a plan-choice read request.

        Returns:
            The plan choices result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        terminal = control_context.terminal
        if not isinstance(request, control_models.ReadPlanChoices):
            msg = "read_plan_choices handler requires ReadPlanChoices"
            raise TypeError(msg)
        window_id = control_context.terminal_window_id
        if window_id is None:
            return control_models.PlanChoicesResult(
                request.request_id, control_models.ControlAcknowledgement.REJECTED, SESSION_NOT_LIVE_REASON,
            )
        try:
            rows = plandialog.options(TerminalDriver(terminal), window_id)
        except plandialog.CodexPlanError as error:
            return control_models.PlanChoicesResult(
                request.request_id, control_models.ControlAcknowledgement.INDETERMINATE, str(error),
            )
        return control_models.PlanChoicesResult(
            request.request_id,
            control_models.ControlAcknowledgement.ACKNOWLEDGED,
            choices=tuple(control_models.PlanChoice(row.digit, row.label) for row in rows),
        )


class DecidePlanHandler(ControlHandler):
    """Represent decide plan handler."""

    def __call__(
        self, request: control_models.ControlRequest, control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Handle a plan-decision request.

        Returns:
            The control result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        terminal = control_context.terminal
        if not isinstance(request, control_models.DecidePlan):
            msg = "decide_plan handler requires DecidePlan"
            raise TypeError(msg)
        if request.feedback is not None:
            return control_models.ControlResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                "Codex plan decisions do not accept feedback",
            )
        window_id = control_context.terminal_window_id
        if window_id is None:
            return control_models.ControlResult(
                request.request_id, control_models.ControlAcknowledgement.REJECTED, SESSION_NOT_LIVE_REASON,
            )
        driver = TerminalDriver(terminal)
        return _decide_plan_result(request, driver, window_id)


def _decide_plan_result(
    request: control_models.DecidePlan,
    terminal_driver: TerminalDriver,
    window_id: WindowId,
) -> control_models.ControlResult:
    try:
        return _apply_plan_decision(request, terminal_driver, window_id)
    except plandialog.CodexPlanError as error:
        return control_models.ControlResult(
            request.request_id, control_models.ControlAcknowledgement.INDETERMINATE, str(error),
        )


def _apply_plan_decision(
    request: control_models.DecidePlan,
    terminal_driver: TerminalDriver,
    window_id: WindowId,
) -> control_models.ControlResult:
    if request.decision == "dismiss":
        plandialog.dismiss(terminal_driver, window_id)
    else:
        rows = plandialog.options(terminal_driver, window_id)
        row = next((row for row in rows if row.digit == request.decision), None)
        if row is None:
            return control_models.ControlResult(
                request.request_id, control_models.ControlAcknowledgement.REJECTED, "unknown plan decision",
            )
        plandialog.decide(terminal_driver, window_id, row.digit, row.label)
    return control_models.ControlResult(request.request_id, control_models.ControlAcknowledgement.ACKNOWLEDGED)
