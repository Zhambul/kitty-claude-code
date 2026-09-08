# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert Claude usage values into canonical scalar values."""

from datetime import datetime
from decimal import Decimal

MODEL_WINDOW_PREFIX = "seven_day_"
MAX_MODEL_KEY_LENGTH = 24


def epoch_seconds(timestamp_text: str | None) -> float | None:
    """Convert an ISO timestamp into epoch seconds.

    Returns:
        Epoch seconds, or None for an invalid value.

    """
    if not timestamp_text or not timestamp_text.strip():
        return None
    try:
        return datetime.fromisoformat(timestamp_text).timestamp()
    except ValueError:
        return None


def percent(percent_value: float | None) -> Decimal | None:
    """Convert a usage percentage into a bounded decimal.

    Returns:
        A percentage from zero to 100, or None.

    """
    if percent_value is None or isinstance(percent_value, bool):
        return None
    return Decimal(max(0, min(100, round(percent_value))))


def model_key(display_name: str | None) -> str | None:
    """Build the usage-window key for a model name.

    Returns:
        The model window key, or None for an invalid name.

    """
    if not display_name:
        return None
    slug = "".join(slug_character(character) for character in display_name.lower())
    slug = "_".join(part for part in slug.split("_") if part)
    if not slug or not slug.isascii() or len(slug) > MAX_MODEL_KEY_LENGTH:
        return None
    return MODEL_WINDOW_PREFIX + slug


def slug_character(character: str) -> str:
    """Return a key character or an underscore.

    Returns:
        A key-safe character.

    """
    return character if character.isalnum() else "_"
