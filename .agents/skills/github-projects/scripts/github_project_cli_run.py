# Copyright (c) 2026 Zhambyl Yermagambet
"""Split GitHub Projects SDK implementation."""

from __future__ import annotations

import sys
from dataclasses import asdict
from typing import TYPE_CHECKING

from github_project_cli_parser import build_parser
from github_project_client import GitHubProjectClient
from github_project_errors import GitHubProjectError
from github_project_models import NewIssue
from github_project_output import emit_document

if TYPE_CHECKING:
    import argparse


def _run_query_command(client: GitHubProjectClient, args: argparse.Namespace) -> bool:
    if args.command == "schema":
        emit_document(asdict(client.schema()))
        return True
    if args.command == "issues":
        emit_document(
            [
                asdict(issue)
                for issue in client.issues(
                    status=args.status,
                    area=args.area,
                    work_type=args.type,
                    priority=args.priority,
                )
            ],
        )
        return True
    if args.command == "backlog":
        emit_document([asdict(issue) for issue in client.backlog()])
        return True
    if args.command == "sort-backlog":
        emit_document([asdict(issue) for issue in client.sort_backlog(apply=args.apply)])
        return True
    return False


def _run_issue_write_command(client: GitHubProjectClient, args: argparse.Namespace) -> bool:
    if args.command == "create":
        emit_document(
            asdict(
                client.create_issue(
                    NewIssue(
                        title=args.title,
                        area=args.area,
                        work_type=args.type,
                        priority=args.priority,
                        status=args.status,
                        body=args.body,
                    ),
                    allow_duplicate=args.allow_duplicate,
                ),
            ),
        )
        return True
    if args.command == "update":
        updated_issue = client.update_issue(args.issue, title=args.title, body=args.body)
        emit_document(asdict(updated_issue))
        return True
    if args.command == "comment":
        emit_document(client.add_comment(args.issue, args.body))
        return True
    if args.command == "comments":
        emit_document(client.comments(args.issue))
        return True
    return False


def _run_issue_field_command(client: GitHubProjectClient, args: argparse.Namespace) -> bool:
    if args.command == "move":
        emit_document(asdict(client.set_status(args.issue, args.status)))
        return True
    if args.command == "set-type":
        emit_document(asdict(client.set_work_type(args.issue, args.work_type)))
        return True
    if args.command == "set-area":
        emit_document(asdict(client.set_area(args.issue, args.area)))
        return True
    if args.command == "set-priority":
        emit_document(asdict(client.set_priority(args.issue, args.priority)))
        return True
    return False


def _run_state_command(client: GitHubProjectClient, args: argparse.Namespace) -> bool:
    if args.command == "close":
        emit_document(asdict(client.close_issue(args.issue)))
        return True
    if args.command == "reopen":
        emit_document(asdict(client.reopen_issue(args.issue)))
        return True
    return False


def _run_view_command(client: GitHubProjectClient, args: argparse.Namespace) -> bool:
    if args.command == "views":
        emit_document([asdict(view) for view in client.views()])
        return True
    if args.command == "show":
        emit_document(asdict(client.find_issue(args.issue)))
        return True
    if args.command == "create-view":
        created_view = client.create_view(args.name, filter_query=args.filter, layout=args.layout)
        emit_document(asdict(created_view))
        return True
    return False


def _run(args: argparse.Namespace) -> int:
    client = GitHubProjectClient.from_environment()
    command_groups = (
        _run_query_command,
        _run_issue_write_command,
        _run_issue_field_command,
        _run_state_command,
        _run_view_command,
    )
    if any(command_group(client, args) for command_group in command_groups):
        return 0
    message = f"Unsupported command: {args.command}"
    raise GitHubProjectError(message)


def main() -> int:
    """Run the selected project command and report project errors.

    Returns:
        Zero on success, or one if a project error occurs.

    """
    try:
        return _run(build_parser().parse_args())
    except GitHubProjectError as error:
        sys.stderr.write(f"error: {error}\n")
        return 1
