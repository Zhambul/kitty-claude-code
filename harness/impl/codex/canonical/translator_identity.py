# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from harness.impl.codex.canonical import translator_dependencies as dependencies
from harness.impl.codex.ids_session_types import CodexCallId


class CodexToolKind(StrEnum):
    """Represent codex tool kind."""

    SEARCH = "search"
    WEB = "web"
    FILE = "file"
    IGNORED = "ignored"


@dataclass(frozen=True)
class ToolMeaning:
    """Represent tool meaning."""

    kind: CodexToolKind
    native_name: str


@dataclass(frozen=True)
class SourceShellKey:
    """Identify one shell inside one source."""

    source_key: str
    shell_id: dependencies.translator_type_dependencies.ids.ShellId


@dataclass(frozen=True)
class FinishedShellKey:
    """Identify one finished shell and its outcome."""

    source_key: str
    shell_id: dependencies.translator_type_dependencies.ids.ShellId
    outcome: dependencies.translator_domain_values.outcomes.Outcome


@dataclass(frozen=True)
class SourceSkillKey:
    """Identify one skill inside one source."""

    source_key: str
    skill_id: dependencies.translator_type_dependencies.ids.SkillId


@dataclass(frozen=True)
class SourceCallKey:
    """Identify one tool call inside one source."""

    source_key: str
    call_id: CodexCallId


@dataclass(frozen=True)
class TurnExecCall:
    """Join an exec call identifier to its record."""

    native_call_id: CodexCallId
    record: dependencies.record_canonical_namespaces.record_tool_records.ExecRecord
