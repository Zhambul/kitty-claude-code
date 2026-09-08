# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e context dependencies."""

from tests.e2e.testkit import (
    planning_contexts as planning_contexts,
    question_contexts as question_contexts,
    reference_contexts as reference_contexts,
    repository as _repository_testkit,
    skill_fixtures as _skill_testkit,
    work_contexts as work_contexts,
)
from tests.e2e.testkit.journeys import JourneyDriver as JourneyDriver
from tests.e2e.testkit.planning import PlanWorkDriver as PlanWorkDriver

repository_testkit = _repository_testkit
skill_testkit = _skill_testkit
