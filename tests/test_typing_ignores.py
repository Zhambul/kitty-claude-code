# Copyright (c) 2026 Zhambyl Yermagambet
"""Tests for typed ignore comments."""

from __future__ import annotations

from tests.typing_ignore_policy import ROOT, is_type_ignore_source, unnamed_type_ignore_locations


def test_type_ignore_names_error_it_silences() -> None:
    """Require an error code on each typed ignore comment."""
    blanket = [
        location
        for path in ROOT.rglob("*.py")
        if is_type_ignore_source(path)
        for location in unnamed_type_ignore_locations(path)
    ]
    assert not blanket
