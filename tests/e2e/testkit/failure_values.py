# Copyright (c) 2026 Zhambyl Yermagambet
"""Format bounded values for E2E failure reports."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence

MAXIMUM_TEXT_CHARACTERS = 4_000
type JsonValue = bytes | bool | float | int | str | Sequence[JsonValue] | Mapping[str, JsonValue] | None


def compact(json_content: JsonValue) -> str:
    """Return a bounded JSON-like value.

    Returns:
        A bounded JSON-like value.

    """
    text = (
        json_content if isinstance(json_content, str)
        else json.dumps(json_content, default=str, ensure_ascii=False)
    )
    text = text.replace("\x00", "")
    if len(text) <= MAXIMUM_TEXT_CHARACTERS:
        return text
    text_prefix = text[:MAXIMUM_TEXT_CHARACTERS]
    return f"{text_prefix}…"
