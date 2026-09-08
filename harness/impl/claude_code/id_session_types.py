# Copyright (c) 2026 Zhambyl Yermagambet
"""Native Claude Code session and shell identifier types."""

from typing import NewType

ClaudeCodeSessionId = NewType("ClaudeCodeSessionId", str)
ClaudeCodeActorId = NewType("ClaudeCodeActorId", str)
ClaudeCodeCallId = NewType("ClaudeCodeCallId", str)
ClaudeCodeCompactionId = NewType("ClaudeCodeCompactionId", str)
ClaudeCodeControlRequestId = NewType("ClaudeCodeControlRequestId", str)
ClaudeCodeShellId = NewType("ClaudeCodeShellId", str)
