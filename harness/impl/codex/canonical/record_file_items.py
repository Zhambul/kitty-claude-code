# Copyright (c) 2026 Zhambyl Yermagambet
"""Own file items models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, RootModel

from harness.impl.codex.canonical.record_config import FOREIGN, ForeignMetadata
from harness.impl.codex.ids_session_types import CodexShellId


class FileChangeEntry(BaseModel):
    """Represent file change entry."""

    model_config = FOREIGN
    type: str | None = None
    content: str | None = None
    unified_diff: str | None = None
    move_path: str | None = None


class FileChanges(RootModel[Mapping[str, FileChangeEntry]]):
    """Represent file changes."""


class FileChangeItem(BaseModel):
    """Represent file change item."""

    model_config = FOREIGN
    type: Literal["FileChange"]
    id: str | None = None
    status: str | None = None
    changes: FileChanges | None = None
    stdout: str | None = None
    stderr: str | None = None


class DurationBlock(BaseModel):
    """Represent duration block."""

    model_config = FOREIGN
    secs: int | None = None
    nanos: int | None = None


class CommandExecutionItem(BaseModel):
    """Represent command execution item."""

    model_config = FOREIGN
    type: Literal["CommandExecution"]
    id: str | None = None
    status: str | None = None
    process_id: CodexShellId | int | None = None
    aggregated_output: str | None = None
    formatted_output: str | None = None
    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | None = None
    command: list[str] | None = None
    cwd: str | None = None
    duration: DurationBlock | None = None
    source: str | None = None
    # The parser's own guess at the command's shell-builtin shape — never
    # read here (the raw `command`/`aggregated_output` are); a real vendor
    # field, still open (module header): its element shape varies by guess.
    parsed_cmd: list[ForeignMetadata | str] | None = None
