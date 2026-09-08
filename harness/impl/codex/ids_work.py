# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert Codex work identifiers to domain identifiers."""

from domain import ids as domain_ids
from harness.impl.codex.ids_work_types import CodexSkillId, CodexTaskId, CodexTaskListId


def skill_id_from_codex(codex_skill_id: CodexSkillId) -> domain_ids.SkillId:
    """Return the domain skill identifier.

    Returns:
        The domain skill identifier.

    """
    return domain_ids.SkillId(codex_skill_id)


def task_id_from_codex(codex_task_id: CodexTaskId) -> domain_ids.TaskId:
    """Return the domain task identifier.

    Returns:
        The domain task identifier.

    """
    return domain_ids.TaskId(codex_task_id)


def task_list_id_from_codex(codex_task_list_id: CodexTaskListId) -> domain_ids.TaskListId:
    """Return the domain task-list identifier.

    Returns:
        The domain task-list identifier.

    """
    return domain_ids.TaskListId(codex_task_list_id)
