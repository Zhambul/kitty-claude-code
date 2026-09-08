# Copyright (c) 2026 Zhambyl Yermagambet
"""Read Claude Code injected skill prompts."""

import pathlib

from harness.impl.claude_code.canonical import message_skill_values as skill_values


def _loaded_skill(text: str) -> tuple[str, str] | None:
    if "\n" not in text:
        return None
    first_line = text.partition("\n")[0]
    name = _skill_name(first_line)
    if name is None:
        return None
    marker = text.rfind(skill_values.SKILL_ARGUMENTS_MARKER)
    output = text.rstrip()
    if marker >= 0:
        output = text[:marker].rstrip()
    return name, output


def _skill_name(first_line: str) -> str | None:
    if not first_line.startswith(skill_values.SKILL_OUTPUT_PREFIX):
        return None
    directory = first_line[len(skill_values.SKILL_OUTPUT_PREFIX) :].strip().rstrip("/")
    if "/.claude/skills/" not in directory:
        return None
    name = pathlib.Path(directory).name
    return name or None
