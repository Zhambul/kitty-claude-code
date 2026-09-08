# Copyright (c) 2026 Zhambyl Yermagambet
"""Split GitHub Projects SDK implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import github_project_values_data as project_values

if TYPE_CHECKING:
    import argparse


def add_query_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add read-only project commands."""
    commands.add_parser("schema")
    issues = commands.add_parser("issues")
    issues.add_argument("--status", choices=project_values.STATUSES)
    issues.add_argument("--area", choices=project_values.AREAS)
    issues.add_argument("--type", choices=project_values.WORK_TYPES)
    issues.add_argument("--priority", choices=project_values.PRIORITIES)
    commands.add_parser("backlog")
    commands.add_parser("views")


def add_create_command(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add the issue creation command."""
    create = commands.add_parser("create")
    create.add_argument(project_values.TITLE_FIELD)
    create.add_argument("--area", required=True, choices=project_values.AREAS)
    create.add_argument("--type", required=True, choices=project_values.WORK_TYPES)
    create.add_argument("--priority", required=True, choices=project_values.PRIORITIES)
    create.add_argument("--status", default=project_values.BACKLOG_STATUS, choices=project_values.STATUSES)
    create.add_argument("--body", default="")
    create.add_argument("--allow-duplicate", action="store_true")


def add_update_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add issue update commands."""
    update = commands.add_parser("update")
    update.add_argument(project_values.ISSUE_ARGUMENT)
    update.add_argument("--title")
    update.add_argument("--body")
    sort_backlog = commands.add_parser("sort-backlog")
    sort_backlog.add_argument("--apply", action="store_true")
    show = commands.add_parser("show")
    show.add_argument(project_values.ISSUE_ARGUMENT)


def add_project_field_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add status and type field commands."""
    move = commands.add_parser("move")
    move.add_argument(project_values.ISSUE_ARGUMENT)
    move.add_argument(project_values.STATUS_CHOICE, choices=project_values.STATUSES)
    set_type = commands.add_parser("set-type")
    set_type.add_argument(project_values.ISSUE_ARGUMENT)
    set_type.add_argument("work_type", choices=project_values.WORK_TYPES)


def add_project_choice_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add area and priority field commands."""
    set_area = commands.add_parser("set-area")
    set_area.add_argument(project_values.ISSUE_ARGUMENT)
    set_area.add_argument(project_values.AREA_CHOICE, choices=project_values.AREAS)
    set_priority = commands.add_parser("set-priority")
    set_priority.add_argument(project_values.ISSUE_ARGUMENT)
    set_priority.add_argument(project_values.PRIORITY_CHOICE, choices=project_values.PRIORITIES)


def add_discussion_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add issue state and discussion commands."""
    close = commands.add_parser("close")
    close.add_argument(project_values.ISSUE_ARGUMENT)
    reopen = commands.add_parser("reopen")
    reopen.add_argument(project_values.ISSUE_ARGUMENT)
    comment = commands.add_parser("comment")
    comment.add_argument(project_values.ISSUE_ARGUMENT)
    comment.add_argument(project_values.BODY_FIELD)
    comments = commands.add_parser("comments")
    comments.add_argument(project_values.ISSUE_ARGUMENT)
