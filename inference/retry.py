# Copyright (c) 2026 Zhambyl Yermagambet
"""Manage bounded retries across inference providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from inference.commands import ProviderCandidate

if TYPE_CHECKING:
    from inference.errors import ProviderUnavailableError

RETRIES_PER_PROVIDER = 1


@dataclass
class ProviderRetry:
    """Keep the remaining retries for one provider."""

    candidate: ProviderCandidate
    remaining: int = RETRIES_PER_PROVIDER


class ProviderAttemptQueue:
    """Order initial provider attempts and one retry per provider."""

    def __init__(self, candidates: tuple[ProviderCandidate, ...]) -> None:
        """Create a queue from providers in preferred order."""
        self._pending = list(candidates)
        self._retries = [ProviderRetry(candidate) for candidate in candidates]
        self.attempt = 0

    def __bool__(self) -> bool:
        """Return true while the queue has a pending attempt.

        Returns:
            True while the queue has a pending attempt.

        """
        return bool(self._pending)

    def take(self) -> ProviderCandidate:
        """Remove and return the next provider attempt.

        Returns:
            The provider candidate.

        """
        self.attempt += 1
        return self._pending.pop(0)

    def retry(
        self,
        candidate: ProviderCandidate,
        error: ProviderUnavailableError,
    ) -> None:
        """Schedule one remaining retry in the correct position."""
        retry = self._retry_for(candidate)
        if retry.remaining <= 0:
            return
        retry.remaining -= 1
        if _needs_immediate_retry(error):
            self._pending.insert(0, candidate)
            return
        self._pending.append(candidate)

    def _retry_for(self, candidate: ProviderCandidate) -> ProviderRetry:
        return next(retry for retry in self._retries if retry.candidate == candidate)


def _needs_immediate_retry(error: ProviderUnavailableError) -> bool:
    return error.stage == "parse output" and "title" in str(error)
