# Copyright (c) 2026 Zhambyl Yermagambet
"""Resolve and rank available model providers."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

from inference import commands, provider_state
from inference.capacity import remaining_capacity

if TYPE_CHECKING:
    from collections.abc import Callable

    from harness.models.usage import (
        UsageRow,
    )
    from harness.runtime import HarnessRuntimeConfigs


class UsageReader(Protocol):
    """Read current model usage from all harnesses."""

    def usage_rows(self) -> tuple[UsageRow, ...]:
        """Return current usage rows."""
        ...


@dataclass(frozen=True)
class RankedCandidate:
    """Hold one candidate with its ranking fields."""

    capacity: Decimal
    order: int
    candidate: commands.ProviderCandidate


@dataclass(frozen=True)
class CandidateAssessment:
    """Hold the audit state and optional rank of one candidate."""

    state: provider_state.ProviderState
    ranked_candidate: RankedCandidate | None


@dataclass(frozen=True)
class CandidateSelection:
    """Hold ranked candidates and the state of every provider."""

    candidates: tuple[commands.ProviderCandidate, ...]
    provider_states: tuple[provider_state.ProviderState, ...]


class ProviderSelector:
    """Resolve providers and rank them by remaining capacity."""

    def __init__(
        self,
        usage_reader: UsageReader,
        runtime_configs: HarnessRuntimeConfigs,
        executable_resolver: Callable[[str], str | None],
    ) -> None:
        """Create a selector with usage and executable sources."""
        self.usage = usage_reader
        self.runtime_configs = runtime_configs
        self.executable_resolver = executable_resolver

    def select(self) -> CandidateSelection:
        """Return available providers in preferred order.

        Returns:
            Available providers in preferred order.

        """
        rows = self.usage.usage_rows()
        assessments = tuple(
            self._assess(candidate, order, rows) for order, candidate in enumerate(commands.PROVIDER_CANDIDATES)
        )
        ranked = _ranked_candidates(assessments)
        ranked.sort(reverse=True, key=_ranking_key)
        return CandidateSelection(
            tuple(entry.candidate for entry in ranked),
            tuple(assessment.state for assessment in assessments),
        )

    def _assess(
        self,
        candidate: commands.ProviderCandidate,
        order: int,
        rows: tuple[UsageRow, ...],
    ) -> CandidateAssessment:
        executable = self.executable_resolver(candidate.executable)
        if executable is None:
            configured = self.runtime_configs.for_harness(candidate.harness)
            return CandidateAssessment(
                provider_state.ExecutableUnavailable(
                    provider=candidate.harness,
                    status="executable unavailable",
                    configuration=configured.executable,
                ),
                None,
            )
        capacity = remaining_capacity(candidate.harness, rows)
        if capacity <= 0:
            return CandidateAssessment(
                provider_state.CapacityUnavailable(
                    provider=candidate.harness,
                    status="capacity unavailable",
                    remaining_capacity_percent=capacity,
                ),
                None,
            )
        state = provider_state.AvailableProvider(
            provider=candidate.harness,
            status="available",
            remaining_capacity_percent=capacity,
        )
        ranked = RankedCandidate(
            capacity,
            -order,
            replace(candidate, executable=executable),
        )
        return CandidateAssessment(state, ranked)


def _ranking_key(candidate: RankedCandidate) -> tuple[Decimal, int]:
    return candidate.capacity, candidate.order


def _ranked_candidates(
    assessments: tuple[CandidateAssessment, ...],
) -> list[RankedCandidate]:
    return [assessment.ranked_candidate for assessment in assessments if assessment.ranked_candidate is not None]
