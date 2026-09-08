# Copyright (c) 2026 Zhambyl Yermagambet
"""Native Claude Code conversation and work identifier types."""

from typing import NewType

ClaudeCodeMessageId = NewType("ClaudeCodeMessageId", str)
ClaudeCodeQuestionId = NewType("ClaudeCodeQuestionId", str)
ClaudeCodeReasoningId = NewType("ClaudeCodeReasoningId", str)
ClaudeCodeTaskId = NewType("ClaudeCodeTaskId", str)
ClaudeCodeTaskListId = NewType("ClaudeCodeTaskListId", str)
ClaudeCodeTurnId = NewType("ClaudeCodeTurnId", str)
