# Copyright (c) 2026 Zhambyl Yermagambet
"""Tests for the Baqylau GitHub Projects SDK."""

from __future__ import annotations

import unittest

import pytest
from github_projects_sdk import (
    GitHubProjectClient,
    GitHubProjectError,
    Issue,
    JsonValue,
    NewIssue,
    ProjectSchema,
    priority_rank,
)

INVALID_TITLE = "Invalid"
MEDIUM_PRIORITY = "P2 — Medium"
FRONTEND_AREA = "Frontend"
BUG_WORK_TYPE = "Bug"
CREATED_ISSUE_NUMBER = 42
LOW_PRIORITY_RANK = 3


class NoRequestTransport:
    """Represent no request transport."""

    def request(
        self,
        method: str,
        path: str,
        request_document: dict[str, JsonValue] | None = None,
    ) -> JsonValue:
        """Reject every request from a test that must not use the network.

        Raises:
            AssertionError: For every request.

        """
        raise AssertionError((method, path, request_document))


class GitHubProjectsSdkTests(unittest.TestCase):
    """Represent git hub projects SDK tests."""

    def test_priority_rank(self) -> None:
        """Verify priority rank."""
        assert priority_rank("P0 — Critical") == 0
        assert priority_rank("P3 — Low") == LOW_PRIORITY_RANK
        assert priority_rank(None) > LOW_PRIORITY_RANK

    def test_create_rejects_unknown_work_type(self) -> None:
        """Verify create rejects unknown work type before request."""
        client = GitHubProjectClient(NoRequestTransport())
        with pytest.raises(GitHubProjectError, match="Invalid work type"):
            client.create_issue(NewIssue(INVALID_TITLE, "Backend", "Chore", MEDIUM_PRIORITY))

    def test_create_rejects_unknown_priority(self) -> None:
        """Verify create rejects unknown priority before request."""
        client = GitHubProjectClient(NoRequestTransport())
        with pytest.raises(GitHubProjectError, match="Invalid priority"):
            client.create_issue(NewIssue(INVALID_TITLE, "Backend", "Feature", "Medium"))

    def test_create_rejects_unknown_status(self) -> None:
        """Verify create rejects unknown status before request."""
        client = GitHubProjectClient(NoRequestTransport())
        with pytest.raises(GitHubProjectError, match="Invalid status"):
            client.create_issue(
                NewIssue(INVALID_TITLE, "Backend", "Feature", MEDIUM_PRIORITY, status="Todo"),
            )

    def test_create_rejects_unknown_area(self) -> None:
        """Verify create rejects unknown area before request."""
        client = GitHubProjectClient(NoRequestTransport())
        with pytest.raises(GitHubProjectError, match="Invalid area"):
            client.create_issue(NewIssue(INVALID_TITLE, "Fullstack", "Feature", MEDIUM_PRIORITY))

    def test_create_backlog_issue_sorts_backlog(self) -> None:
        """Verify create backlog issue sorts backlog."""
        client = GitHubProjectClient(NoRequestTransport())
        client.issues = lambda **_kwargs: []  # type: ignore[method-assign]
        client.rest = lambda _method, _path, _request_document=None: {  # type: ignore[method-assign]
            "node_id": "content-1",
            "number": 42,
            "title": "New issue",
            "body": "",
            "html_url": "https://example.test/issues/42",
            "state": "open",
        }
        client.schema = lambda: ProjectSchema("project-1", "Project", "https://example.test", ())  # type: ignore[method-assign]
        client.graphql = lambda _query, _variables=None: {  # type: ignore[method-assign]
            "addProjectV2ItemById": {"item": {"id": "item-1"}},
        }
        sort_calls: list[bool] = []
        client.sort_backlog = lambda *, apply=False: sort_calls.append(apply) or []  # type: ignore[method-assign]

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(client, "_set_field", lambda *_args: None)
            issue = client.create_issue(
                NewIssue("New issue", FRONTEND_AREA, BUG_WORK_TYPE, MEDIUM_PRIORITY),
            )

        assert issue.number == CREATED_ISSUE_NUMBER
        assert sort_calls == [True]

    def test_backlog_sorts_by_priority_then_issue(self) -> None:
        """Verify backlog sorts by priority then issue number."""
        client = GitHubProjectClient(NoRequestTransport())
        issues = [
            Issue("i3", "c3", 3, "low", "", "u3", "OPEN", "Backlog", FRONTEND_AREA, BUG_WORK_TYPE, "P3 — Low"),
            Issue("i2", "c2", 2, "high-b", "", "u2", "OPEN", "Backlog", FRONTEND_AREA, BUG_WORK_TYPE, "P1 — High"),
            Issue("i1", "c1", 1, "high-a", "", "u1", "OPEN", "Backlog", FRONTEND_AREA, BUG_WORK_TYPE, "P1 — High"),
        ]
        client.issues = lambda **_kwargs: issues  # type: ignore[method-assign]
        backlog = client.backlog()
        numbers = [issue.number for issue in backlog]
        assert numbers == [1, 2, 3]


if __name__ == "__main__":
    unittest.main()
