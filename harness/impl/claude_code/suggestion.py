# Copyright (c) 2026 Zhambyl Yermagambet
"""Read suggested and typed text from the Claude Code composer."""

import re

from harness.impl.claude_code import suggestion_screen


def norm(text: str) -> str:
    """Normalize composer whitespace.

    Returns:
        The normalized text.

    """
    return re.sub(r"\s+", " ", text).strip()


def parse(screen: str) -> str | None:
    """Return the faint composer suggestion.

    Returns:
        The normalized suggestion, or None.

    """
    characters = suggestion_screen.box_content(screen)
    content_characters = [
        character
        for character in characters
        if character.character not in suggestion_screen.CONTENT_WHITESPACE and character.character != "\n"
    ]
    if not content_characters:
        return None
    if not all(character.faint for character in content_characters):
        return None
    raw_text = "".join(character.character for character in characters)
    return norm(raw_text.replace(suggestion_screen.NBSP, " ")) or None


def typed(screen: str) -> str | None:
    """Return the real non-faint composer text.

    Returns:
        The normalized typed text, or None.

    """
    characters = suggestion_screen.box_content(screen)
    raw_text = "".join(
        character.character for character in characters if not character.faint and character.character != "\n"
    )
    return norm(raw_text.replace(suggestion_screen.NBSP, " ")) or None
