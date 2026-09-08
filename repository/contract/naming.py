# Copyright (c) 2026 Zhambyl Yermagambet
"""Storage contract for idempotent automatic-title work."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from domain.naming import NamingJob


class NamingJobRepository(Protocol):
    """Represent naming job repository."""

    def enqueue(self, naming_job: NamingJob) -> bool:
        """Return the enqueue."""
        ...

    def register_running(self, naming_job: NamingJob) -> tuple[NamingJob, bool]:
        """Register running."""
        ...

    def claim_next(self) -> NamingJob | None:
        """Return the claim next."""
        ...

    def complete(self, key: str, title: str) -> None:
        """Return the complete."""
        ...

    def fail(self, key: str, reason: str) -> None:
        """Return the fail."""
        ...

    def find(self, key: str) -> NamingJob | None:
        """Return find."""
        ...
