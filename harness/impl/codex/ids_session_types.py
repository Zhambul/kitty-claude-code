# Copyright (c) 2026 Zhambyl Yermagambet
"""Native Codex identifiers for sessions and shell calls."""

from typing import NewType

CodexSessionId = NewType("CodexSessionId", str)
CodexActorId = NewType("CodexActorId", str)
CodexCallId = NewType("CodexCallId", str)
CodexShellId = NewType("CodexShellId", str)
