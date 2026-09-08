# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.impl.codex.canonical import translator_dependencies as dependencies
from harness.impl.codex.canonical.translator_identity import SourceShellKey
from harness.impl.codex.canonical.translator_tool_paths import read_skill_name

if TYPE_CHECKING:
    from harness.impl.codex.canonical.translator_core_values import SourceIndexValue


def drop_source_keys[SourceIndexValue](
    index: dependencies.translator_type_dependencies.MutableMapping[tuple[str, str], SourceIndexValue],
    source_keys: set[str],
) -> None:
    """Remove keys that belong to a finished session's source files."""
    for source_key, native_id in tuple(index):
        if source_key in source_keys:
            index.pop((source_key, native_id), None)


def is_pending_exec_candidate(
    known_source: str,
    call_record: (
        dependencies.record_canonical_namespaces.record_tool_records.ExecRecord
        | dependencies.record_canonical_namespaces.record_tool_records.ToolRecord
        | dependencies.record_canonical_namespaces.record_actor_records.ToolBatchRecord
        | dependencies.record_canonical_namespaces.record_interaction_records.AskRecord
        | None
    ),
    source_key: str,
    command_texts: set[str],
) -> bool:
    """Check whether a source record can match a pending shell command.

    Returns:
        True for a matching command that does not read a skill file.

    """
    if known_source != source_key:
        return False
    if not isinstance(call_record, dependencies.record_canonical_namespaces.record_tool_records.ExecRecord):
        return False
    if read_skill_name(call_record.cmd) is not None:
        return False
    return call_record.cmd in command_texts


def has_shell(
    shells: set[SourceShellKey],
    source_key: str,
    shell_id: dependencies.translator_type_dependencies.ids.ShellId,
) -> bool:
    """Return whether a source contains the shell.

    Returns:
        Whether a source contains the shell.

    """
    return SourceShellKey(source_key, shell_id) in shells
