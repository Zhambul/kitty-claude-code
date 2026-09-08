# Copyright (c) 2026 Zhambyl Yermagambet
"""Durable jobs, title safety, and generic naming semantics."""

import pytest

from inference.errors import ModelUnavailableError
from naming.titles import normalize_title
from tests.automatic_naming_values import TITLE_CHARACTER_LIMIT

NORMALIZED_WORD_COUNT = 8


def test_title_normalization_selects_one_safe() -> None:
    """Verify title normalization selects one safe bounded line."""
    title = normalize_title(
        "**Plan the reliable database schema migration with extra ignored words**\nhttps://example.invalid/output",
    )

    assert title == "Plan the reliable database schema migration with extra"
    assert len(title) <= TITLE_CHARACTER_LIMIT
    assert len(title.split()) == NORMALIZED_WORD_COUNT


@pytest.mark.parametrize("title", ["", "one", "two words", "\n\t"])
def test_title_normalization_rejects_empty_or_too(title: str) -> None:
    """Verify title normalization rejects empty or too short results."""
    with pytest.raises(ModelUnavailableError):
        normalize_title(title)
