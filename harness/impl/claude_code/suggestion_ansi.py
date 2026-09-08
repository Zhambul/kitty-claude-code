# Copyright (c) 2026 Zhambyl Yermagambet
"""Read visible characters and intensity from ANSI text."""

import re
from typing import NamedTuple

CONTROL_SEQUENCE = re.compile(
    r"\x1b\[[0-9;:?]*[ -/]*[@-~]"
    r"|\x1b\][^\x1b\x07]*(?:\x07|\x1b\\)"
    r"|\x1b[@-Z\\-_]",
)
SGR_SEQUENCE = re.compile(r"\x1b\[([0-9;:]*)m")


class VisibleCharacter(NamedTuple):
    """Describe one visible character and its intensity."""

    character: str
    faint: bool


def strip_ansi(text: str) -> str:
    """Remove ANSI control sequences.

    Returns:
        The visible text.

    """
    return CONTROL_SEQUENCE.sub("", text)


def apply_sgr(sgr_parameters: str, *, faint: bool) -> bool:
    """Apply one SGR intensity change.

    Returns:
        The new faint state.

    """
    if not sgr_parameters:
        return False
    for parameter_field in sgr_parameters.split(";"):
        code = parameter_field.split(":", 1)[0]
        if code in {"", "0", "22"}:
            faint = False
        elif code == "2":
            faint = True
    return faint


def consume_control(text: str, start_index: int, *, faint: bool) -> tuple[int, bool]:
    """Consume one control sequence.

    Returns:
        The next text index and faint state.

    """
    control_match = CONTROL_SEQUENCE.match(text, start_index)
    if control_match is None:
        return start_index + 1, faint
    sgr_match = SGR_SEQUENCE.fullmatch(control_match.group(0))
    if sgr_match is not None:
        faint = apply_sgr(sgr_match.group(1), faint=faint)
    return control_match.end(), faint


def visible_characters(text: str) -> list[VisibleCharacter]:
    """Return visible characters with their faint state.

    Returns:
        The visible characters.

    """
    characters: list[VisibleCharacter] = []
    character_index = 0
    faint = False
    while character_index < len(text):
        if text[character_index] == "\x1b":
            character_index, faint = consume_control(text, character_index, faint=faint)
            continue
        characters.append(VisibleCharacter(text[character_index], faint))
        character_index += 1
    return characters
