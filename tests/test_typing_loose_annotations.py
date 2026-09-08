# Copyright (c) 2026 Zhambyl Yermagambet
"""Tests for loose annotation policy."""

from __future__ import annotations

from tests.typing_loose_reporting import loose_annotation_violations, marked_loose_annotation_keys
from tests.typing_loose_repository import LOOSE_ANNOTATION_ALLOWED, loose_annotation_paths


def test_no_loose_annotation_outside_seeded() -> None:
    """Reject loose annotations outside the allowlist."""
    violations = [violation for path in loose_annotation_paths() for violation in loose_annotation_violations(path)]
    assert not violations


def test_loose_annotation_allowlist_has_no_dead() -> None:
    """Require removal of dead loose annotation entries."""
    live_keys = {key for path in loose_annotation_paths() for key in marked_loose_annotation_keys(path)}
    dead_keys = LOOSE_ANNOTATION_ALLOWED - live_keys
    assert dead_keys == set(), f"remove dead loose annotation entries: {sorted(dead_keys)}"
