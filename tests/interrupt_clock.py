# Copyright (c) 2026 Zhambyl Yermagambet
"""Set the interrupt source clock without changing stored marks."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

from engine.interpret.interrupts import GRACE_SECONDS

if TYPE_CHECKING:
    import pytest

    from domain.ids import SessionId
    from harness.models.interrupts import InterruptRegistry


def advance_past_grace(
    monkeypatch: pytest.MonkeyPatch,
    registry: InterruptRegistry,
    session_id: SessionId,
) -> None:
    """Advance the source clock past a stored mark's grace period."""
    marked_at = registry.pending(session_id)
    assert marked_at is not None
    monkeypatch.setattr(
        "engine.interpret.interrupts.time",
        SimpleNamespace(time=lambda: marked_at + GRACE_SECONDS + 1),
    )


def mark_expired(
    monkeypatch: pytest.MonkeyPatch,
    registry: InterruptRegistry,
    session_id: SessionId,
) -> None:
    """Mark an interrupt and advance the source clock past its grace period."""
    registry.mark(session_id)
    advance_past_grace(monkeypatch, registry, session_id)
