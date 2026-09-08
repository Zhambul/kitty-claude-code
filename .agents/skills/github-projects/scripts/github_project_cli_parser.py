# Copyright (c) 2026 Zhambyl Yermagambet
"""Split GitHub Projects SDK implementation."""

from __future__ import annotations

import argparse

import github_project_values_data as project_values
from github_project_cli_commands import (
    add_create_command,
    add_discussion_commands,
    add_project_choice_commands,
    add_project_field_commands,
    add_query_commands,
    add_update_commands,
)


def _add_create_view_command(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add the view creation command."""
    create_view = commands.add_parser("create-view")
    create_view.add_argument(project_values.NAME_FIELD)
    create_view.add_argument("--filter", default="")
    create_view.add_argument("--layout", default="BOARD_LAYOUT", choices=project_values.VIEW_LAYOUTS)


def build_parser() -> argparse.ArgumentParser:
    """Build the project command parser.

    Returns:
        The parser with all supported commands.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    add_query_commands(commands)
    add_create_command(commands)
    add_update_commands(commands)
    add_project_field_commands(commands)
    add_project_choice_commands(commands)
    add_discussion_commands(commands)
    _add_create_view_command(commands)
    return parser
