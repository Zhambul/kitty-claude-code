# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Claude Code plan controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.contract import ControlHandler
from harness.impl.claude_code.controls import plandialog
from harness.impl.claude_code.controls.plan_models import Option, PlanError
from harness.models import controls as control_models
from harness.services.terminal_driver import TerminalDriver

if TYPE_CHECKING:
    from domain.ids import WindowId

SESSION_NOT_LIVE_REASON = "session is not live"


class ReadPlanChoicesHandler(ControlHandler):
    """Read the available plan choices."""

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
        if not isinstance(request, control_models.ReadPlanChoices):
            msg = "read_plan_choices handler requires ReadPlanChoices"
            raise TypeError(msg)
        window_id = control_context.terminal_window_id
        if window_id is None:
            return control_models.PlanChoicesResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                SESSION_NOT_LIVE_REASON,
            )
        try:
            rows = plandialog.options(TerminalDriver(control_context.terminal), window_id)
        except PlanError as error:
            return control_models.PlanChoicesResult(
                request.request_id,
                control_models.ControlAcknowledgement.INDETERMINATE,
                str(error),
            )
        return control_models.PlanChoicesResult(
            request.request_id,
            control_models.ControlAcknowledgement.ACKNOWLEDGED,
            choices=_control_plan_choices(rows),
        )


def _control_plan_choices(rows: list[Option]) -> tuple[control_models.PlanChoice, ...]:
    choices: list[control_models.PlanChoice] = [
        control_models.PlanChoice(row.digit, row.label, row.feedback) for row in rows
    ]
    return tuple(choices)


class DecidePlanHandler(ControlHandler):
    """Apply a plan decision."""

    def __call__(
        self,
        request: control_models.ControlRequest,
        control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Handle a plan-decision request.

        Returns:
            The control result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        if not isinstance(request, control_models.DecidePlan):
            msg = "decide_plan handler requires DecidePlan"
            raise TypeError(msg)
        window_id = control_context.terminal_window_id
        if window_id is None:
            return control_models.ControlResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                SESSION_NOT_LIVE_REASON,
            )
        driver = TerminalDriver(control_context.terminal)
        return _decide_plan_result(request, driver, window_id)


def _decide_plan_result(
    request: control_models.DecidePlan,
    terminal_driver: TerminalDriver,
    window_id: WindowId,
) -> control_models.ControlResult:
    try:
        applied = _apply_plan_decision(request, terminal_driver, window_id)
    except PlanError as error:
        return control_models.ControlResult(
            request.request_id,
            control_models.ControlAcknowledgement.INDETERMINATE,
            str(error),
        )
    if not applied:
        return control_models.ControlResult(
            request.request_id,
            control_models.ControlAcknowledgement.REJECTED,
            "unknown plan decision",
        )
    return control_models.ControlResult(request.request_id, control_models.ControlAcknowledgement.ACKNOWLEDGED)


def _apply_plan_decision(
    request: control_models.DecidePlan,
    terminal_driver: TerminalDriver,
    window_id: WindowId,
) -> bool:
    if request.feedback is not None:
        plandialog.feedback(terminal_driver, window_id, request.feedback)
        return True
    if request.decision == "dismiss":
        plandialog.dismiss(terminal_driver, window_id)
        return True
    rows = plandialog.options(terminal_driver, window_id)
    row = next((row for row in rows if row.digit == request.decision), None)
    if row is None:
        return False
    plandialog.decide(terminal_driver, window_id, row.digit, row.label)
    return True
