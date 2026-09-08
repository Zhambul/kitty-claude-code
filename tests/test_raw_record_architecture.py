# Copyright (c) 2026 Zhambyl Yermagambet
"""Reject collections that use tuples as unnamed records."""

from __future__ import annotations

from tests.raw_record_analysis import source_violations
from tests.raw_record_policy import RAW_RECORD_ALLOWED, production_python_paths
from tests.raw_record_reporting import marked_raw_record_items, raw_record_violations


def test_raw_record_check_resolves_aliases() -> None:
    """Verify the check resolves aliases and wrapper forms."""
    source = """
from collections.abc import Iterable, Sequence as Rows
from typing import List, Tuple

Pair = tuple[str, int]
Pairs = Rows[Pair]
LegacyPair = Tuple[str, int]
LegacyPairs = List[LegacyPair]

def bad(values: Iterable[Pair]) -> Pairs:
    return ()

def good(values: tuple[str, ...]) -> list[str]:
    return list(values)
"""
    keys = {key for _line, key, _text in source_violations(source)}
    assert keys == {"LegacyPair", "LegacyPairs", "Pair", "Pairs", "bad.return", "bad.values"}


def test_production_boundaries_do_not_use_raw() -> None:
    """Verify production boundaries do not use raw tuple records."""
    violations = [violation for path in production_python_paths() for violation in raw_record_violations(path)]
    assert not violations


def test_raw_record_allowlist_has_no_dead_items() -> None:
    """Verify the raw-record allowlist has no dead items."""
    live_items = {
        raw_record_item for path in production_python_paths() for raw_record_item in marked_raw_record_items(path)
    }
    dead_items = RAW_RECORD_ALLOWED - live_items
    assert dead_items == set(), f"remove dead raw record items: {sorted(dead_items)}"
