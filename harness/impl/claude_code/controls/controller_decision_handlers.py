# Copyright (c) 2026 Zhambyl Yermagambet
"""Map Claude Code decision control handlers."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from harness.impl.claude_code.controls.controller_commands import (
    CompactHandler,
    SelectEffortHandler,
    SelectModelHandler,
)
from harness.impl.claude_code.controls.controller_plans import DecidePlanHandler, ReadPlanChoicesHandler
from harness.impl.claude_code.controls.controller_questions import AnswerQuestionHandler
from harness.impl.claude_code.controls.controller_session_actions import ApplyRewindHandler
from harness.models import controls as control_models

if TYPE_CHECKING:
    from collections.abc import Mapping

    from harness.contract import ControlHandler

DECISION_HANDLERS: Mapping[control_models.ControlName, ControlHandler] = MappingProxyType({
    control_models.ControlName.APPLY_REWIND: ApplyRewindHandler(),
    control_models.ControlName.COMPACT: CompactHandler(),
    control_models.ControlName.SELECT_MODEL: SelectModelHandler(),
    control_models.ControlName.SELECT_EFFORT: SelectEffortHandler(),
    control_models.ControlName.ANSWER_QUESTION: AnswerQuestionHandler(),
    control_models.ControlName.READ_PLAN_CHOICES: ReadPlanChoicesHandler(),
    control_models.ControlName.DECIDE_PLAN: DecidePlanHandler(),
})
