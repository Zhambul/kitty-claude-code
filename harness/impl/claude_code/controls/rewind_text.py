# Copyright (c) 2026 Zhambyl Yermagambet
"""Compare Claude Code rewind prompt text."""


def first_line(text: str) -> str:
    """Return the first line that contains text.

    Returns:
        The first line that contains text.

    """
    for text_line in (text or "").splitlines():
        if text_line.strip():
            return text_line.strip()
    return ""


def entry_matches(entry: str, target: str) -> bool:
    """Return true when a rewind entry identifies the target prompt.

    Returns:
        True if the rewind entry identifies the target prompt.

    """
    normalized_entry = (entry or "").strip()
    target_first_line = first_line(target)
    if not normalized_entry or not target_first_line:
        return False
    if normalized_entry.endswith("…"):
        return target_first_line.startswith(normalized_entry[:-1].rstrip())
    return normalized_entry == target_first_line
