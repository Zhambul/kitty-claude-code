# Copyright (c) 2026 Zhambyl Yermagambet
"""Build structured Claude Code file patches."""

from dataclasses import dataclass, field

from harness.impl.claude_code.canonical import records


@dataclass(frozen=True)
class _PatchSection:
    lines: tuple[str, ...]
    added: int
    removed: int


@dataclass
class _StructuredPatchBuilder:
    path: str
    lines: list[str] = field(init=False)
    added: int = 0
    removed: int = 0

    def __post_init__(self) -> None:
        self.lines = [f"--- {self.path}", f"+++ {self.path}"]

    def add(self, patch: records.PatchHunk) -> None:
        section = _patch_section(patch)
        self.lines.extend(section.lines)
        self.added += section.added
        self.removed += section.removed

    def result(self) -> tuple[str, int, int]:
        rendered = "\n".join(self.lines)
        return f"{rendered}\n", self.added, self.removed


def _patch_section(patch: records.PatchHunk) -> _PatchSection:
    content_lines = tuple(str(line) for line in patch.lines or ())
    old_range = _patch_range(patch.old_start, patch.old_lines)
    new_range = _patch_range(patch.new_start, patch.new_lines)
    header = f"@@ -{old_range} +{new_range} @@"
    return _PatchSection(
        (header, *content_lines),
        sum(line.startswith("+") for line in content_lines),
        sum(line.startswith("-") for line in content_lines),
    )


def _patch_range(start: int | None, line_count: int | None) -> str:
    start_value, line_count_value = start or 0, line_count or 0
    return f"{start_value},{line_count_value}"


def structured_patch(
    path: str,
    tool_response: records.ToolResponse,
) -> tuple[str | None, int | None, int | None]:
    """Return a structured patch.

    Returns:
        The patch and line counts.

    """
    patches = tool_response.structured_patch
    if not patches:
        return None, None, None
    builder = _StructuredPatchBuilder(path)
    for patch in patches:
        builder.add(patch)
    return builder.result()
