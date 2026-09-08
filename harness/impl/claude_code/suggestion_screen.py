# Copyright (c) 2026 Zhambyl Yermagambet
"""Read the Claude Code composer box from terminal text."""

from harness.impl.claude_code import suggestion_ansi

PROMPT = "\u276f"
NBSP = "\xa0"
CONTENT_WHITESPACE = f" \t{NBSP}"
RULE = "─"
RULE_MINIMUM = 10
FRAME_RULE_COUNT = 2
EDITOR_MODE_MARKERS = ("-- INSERT --", "-- NORMAL --", "-- VISUAL --")


def is_rule(screen_line: str) -> bool:
    """Return true when a line is a composer divider.

    Returns:
        True if the line is a composer divider.

    """
    return suggestion_ansi.strip_ansi(screen_line).count(RULE) >= RULE_MINIMUM


def last_prompt_index(screen_lines: list[str]) -> int | None:
    """Return the last composer prompt line index.

    Returns:
        The prompt line index, or None.

    """
    prompt_index: int | None = None
    for line_index, screen_line in enumerate(screen_lines):
        visible_line = suggestion_ansi.strip_ansi(screen_line).lstrip()
        if visible_line.startswith(PROMPT):
            prompt_index = line_index
    return prompt_index


def framed_region(screen_lines: list[str]) -> list[str] | None:
    """Return the composer region inside its last divider frame.

    Returns:
        The framed region, or None if the frame is incomplete.

    """
    rule_indices: list[int] = []
    for line_index, screen_line in enumerate(screen_lines):
        if is_rule(screen_line):
            rule_indices.append(line_index)
    if len(rule_indices) < FRAME_RULE_COUNT:
        return None
    return screen_lines[rule_indices[-2] + 1 : rule_indices[-1]]


def region(screen_lines: list[str]) -> list[str]:
    """Return the visible composer box lines.

    Returns:
        The composer box lines.

    """
    framed_lines = framed_region(screen_lines)
    if framed_lines is not None:
        return framed_lines
    prompt_index = last_prompt_index(screen_lines)
    if prompt_index is None:
        return []
    region_end = prompt_index + 1
    while region_end < len(screen_lines) and not is_rule(screen_lines[region_end]):
        region_end += 1
    return screen_lines[prompt_index:region_end]


def input_box_visible(screen: str) -> bool:
    """Return true when the composer prompt is visible.

    Returns:
        True if the composer prompt is visible.

    """
    return any(
        suggestion_ansi.strip_ansi(screen_line).startswith(PROMPT)
        for screen_line in region((screen or "").splitlines())
    )


def composer_visible(screen: str) -> bool:
    """Return true when either supported Claude composer shape is visible.

    Returns:
        True if a command can use the composer.

    """
    if input_box_visible(screen):
        return True
    visible_lines = tuple(suggestion_ansi.strip_ansi(screen_line) for screen_line in screen.splitlines())
    return any(marker in visible_line for marker in EDITOR_MODE_MARKERS for visible_line in visible_lines)


def box_content(screen: str) -> list[suggestion_ansi.VisibleCharacter]:
    """Return the visible composer content after its prompt.

    Returns:
        The visible composer characters.

    """
    if not screen:
        return []
    region_lines = region(screen.splitlines())
    if not region_lines:
        return []
    characters = suggestion_ansi.visible_characters("\n".join(region_lines))
    visible_text = "".join(character.character for character in characters)
    if PROMPT in visible_text:
        return characters[visible_text.index(PROMPT) + 1 :]
    return characters
