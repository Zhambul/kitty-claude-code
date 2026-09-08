# Copyright (c) 2026 Zhambyl Yermagambet
"""Expose common and tool-input record foundations."""

from harness.impl.claude_code.canonical.record_common import (
    FOREIGN as FOREIGN,
    OPEN_FOREIGN as OPEN_FOREIGN,
    ForeignMetadata as ForeignMetadata,
    ImageSource as ImageSource,
    PermissionRule as PermissionRule,
    PermissionUpdate as PermissionUpdate,
    TranscriptRecordHeader as TranscriptRecordHeader,
)
from harness.impl.claude_code.canonical.record_questions import (
    Question as Question,
    QuestionAnswers as QuestionAnswers,
    QuestionOption as QuestionOption,
    ShellArguments as ShellArguments,
    ToolArguments as ToolArguments,
)
