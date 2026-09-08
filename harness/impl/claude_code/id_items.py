# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert Claude Code item identifiers."""

from domain import ids as domain_ids
from harness.impl.claude_code.id_item_types import (
    ClaudeCodeMessageId,
    ClaudeCodeQuestionId,
    ClaudeCodeReasoningId,
    ClaudeCodeTaskId,
    ClaudeCodeTaskListId,
    ClaudeCodeTurnId,
)
from harness.impl.claude_code.id_session_types import ClaudeCodeShellId


def message_id_from_claude_code(claude_code_message_id: ClaudeCodeMessageId) -> domain_ids.MessageId:
    """Return the domain message identifier.

    Returns:
        The domain message identifier.

    """
    return domain_ids.MessageId(claude_code_message_id)


def reasoning_id_from_claude_code(claude_code_reasoning_id: ClaudeCodeReasoningId) -> domain_ids.ReasoningId:
    """Return the domain reasoning identifier.

    Returns:
        The domain reasoning identifier.

    """
    return domain_ids.ReasoningId(claude_code_reasoning_id)


def shell_id_from_claude_code(claude_code_shell_id: ClaudeCodeShellId) -> domain_ids.ShellId:
    """Return the domain shell identifier.

    Returns:
        The domain shell identifier.

    """
    return domain_ids.ShellId(claude_code_shell_id)


def task_id_from_claude_code(claude_code_task_id: ClaudeCodeTaskId) -> domain_ids.TaskId:
    """Return the domain task identifier.

    Returns:
        The domain task identifier.

    """
    return domain_ids.TaskId(claude_code_task_id)


def task_list_id_from_claude_code(claude_code_task_list_id: ClaudeCodeTaskListId) -> domain_ids.TaskListId:
    """Return the domain task-list identifier.

    Returns:
        The domain task-list identifier.

    """
    return domain_ids.TaskListId(claude_code_task_list_id)


def turn_id_from_claude_code(claude_code_turn_id: ClaudeCodeTurnId) -> domain_ids.TurnId:
    """Return the domain turn identifier.

    Returns:
        The domain turn identifier.

    """
    return domain_ids.TurnId(claude_code_turn_id)


def question_id_from_claude_code(claude_code_question_id: ClaudeCodeQuestionId) -> domain_ids.QuestionId:
    """Return the domain question identifier.

    Returns:
        The domain question identifier.

    """
    return domain_ids.QuestionId(claude_code_question_id)
