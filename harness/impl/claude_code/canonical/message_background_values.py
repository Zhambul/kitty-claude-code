# Copyright (c) 2026 Zhambyl Yermagambet
"""Map native background statuses to canonical outcomes."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from domain import outcomes as domain_outcomes

if TYPE_CHECKING:
    from collections.abc import Mapping

BACKGROUND_OUTCOMES: Mapping[str, domain_outcomes.Outcome] = MappingProxyType({
    "completed": domain_outcomes.Outcome.SUCCEEDED,
    "failed": domain_outcomes.Outcome.FAILED,
    "killed": domain_outcomes.Outcome.CANCELLED,
    "stopped": domain_outcomes.Outcome.CANCELLED,
})
