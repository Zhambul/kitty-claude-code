# Copyright (c) 2026 Zhambyl Yermagambet
"""Read a shell exit from Claude Code output."""

from domain.content import Content, content_text
from domain.outcomes import Outcome
from harness.impl.claude_code.canonical import tool_values
from harness.impl.claude_code.canonical.tool_result_models import ShellExit


def shell_exit(result: Content | None, outcome: Outcome) -> ShellExit:
    """Read a shell exit code and recognize cancellation exit codes.

    Returns:
        The optional exit code and adjusted completion outcome.

    """
    exit_match = tool_values.SHELL_EXIT_CODE.search(content_text(result))
    exit_code = None if exit_match is None else int(exit_match.group(1))
    if outcome == Outcome.FAILED and exit_code in {130, 137, 143}:
        outcome = Outcome.CANCELLED
    return ShellExit(exit_code, outcome)
