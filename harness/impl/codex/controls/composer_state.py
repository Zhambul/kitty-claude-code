# Copyright (c) 2026 Zhambyl Yermagambet
"""Parse the visible Codex prompt composer state."""

EMPTY_PROMPT = "Ask Codex to do anything"


def empty(screen: str | None) -> bool:
    """Return whether the last visible composer is empty.

    Returns:
        Whether the last visible composer is empty.

    """
    lines = (screen or "").splitlines()
    marker = last_prompt_marker(lines)
    if marker is None:
        return False
    return EMPTY_PROMPT in " ".join(lines[marker].split())


def typed(screen: str | None) -> str | None:
    """Return text from the last visible Codex composer.

    Returns:
        Text from the last visible Codex composer.

    """
    lines = (screen or "").splitlines()
    marker = last_prompt_marker(lines)
    if marker is None:
        return None
    first_line = lines[marker].lstrip()[1:].strip()
    if EMPTY_PROMPT in first_line:
        return ""
    body = [first_line]
    for line in lines[marker + 1 :]:
        if not line.strip():
            break
        body.append(line.strip())
    return "\n".join(body).strip()


def last_prompt_marker(lines: list[str]) -> int | None:
    """Return the last visible prompt marker line index.

    Returns:
        The last visible prompt marker line index.

    """
    for index in range(len(lines) - 1, -1, -1):
        if lines[index].lstrip().startswith(("\u203a", "\u276f")):
            return index
    return None
