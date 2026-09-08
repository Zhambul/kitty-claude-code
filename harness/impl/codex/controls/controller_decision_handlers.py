# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex decision control handlers."""

from types import MappingProxyType

from harness.impl.codex.controls.controller_dependencies import rewind_continuity
from harness.impl.codex.controls.controller_plans import DecidePlanHandler, ReadPlanChoicesHandler
from harness.impl.codex.controls.controller_questions import AnswerQuestionHandler
from harness.impl.codex.controls.controller_selections import (
    ApplyRewindHandler,
    SelectEffortHandler,
    SelectModelHandler,
)
from harness.models import controls as control_models

DECISION_HANDLERS = MappingProxyType({
    control_models.ControlName.APPLY_REWIND: ApplyRewindHandler(rewind_continuity),
    control_models.ControlName.SELECT_MODEL: SelectModelHandler(),
    control_models.ControlName.SELECT_EFFORT: SelectEffortHandler(),
    control_models.ControlName.ANSWER_QUESTION: AnswerQuestionHandler(),
    control_models.ControlName.READ_PLAN_CHOICES: ReadPlanChoicesHandler(),
    control_models.ControlName.DECIDE_PLAN: DecidePlanHandler(),
})
