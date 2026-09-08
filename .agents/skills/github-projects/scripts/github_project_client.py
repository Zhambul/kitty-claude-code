# Copyright (c) 2026 Zhambyl Yermagambet
"""Split GitHub Projects SDK implementation."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Self

import github_project_values_data as project_values
from github_project_errors import GitHubProjectError
from github_project_pages import (
    filter_issues,
    issues_from_connection,
    new_issue_from_document,
    next_page_cursor,
    project_item_connection,
    updated_view,
    validate_new_issue,
)
from github_project_support import (
    backlog_order,
    is_exact_issue_match,
    is_exact_view_match,
    is_open_issue_duplicate,
    is_partial_issue_match,
    project_schema,
    validate_issue_filters,
)
from github_project_transport import (
    HttpTransport,
    Transport,
)
from github_project_values import (
    json_object,
    json_objects,
    only_selection,
    require_choice,
    text_field,
)
from github_project_view_mutation import ViewMutation, parse_project_view

if TYPE_CHECKING:
    from github_project_models import (
        Issue,
        IssuePage,
        NewIssue,
        ProjectSchema,
        ProjectView,
    )


class _GitHubProjectState:
    """Store GitHub project connection state."""

    def __init__(
        self,
        transport: Transport,
        *,
        owner: str = project_values.DEFAULT_OWNER,
        repository: str = project_values.DEFAULT_REPOSITORY,
        project_number: int = project_values.DEFAULT_PROJECT_NUMBER,
    ) -> None:
        """Initialize the object."""
        self._transport = transport
        self.owner = owner
        self.repository = repository
        self.project_number = project_number

    @classmethod
    def from_environment(cls) -> Self:
        """Create the object from environment.

        Returns:
            The object from environment.

        """
        return cls(
            HttpTransport.from_environment(),
            owner=os.environ.get("GITHUB_PROJECT_OWNER", project_values.DEFAULT_OWNER),
            repository=os.environ.get("GITHUB_REPOSITORY", project_values.DEFAULT_REPOSITORY),
            project_number=int(os.environ.get("GITHUB_PROJECT_NUMBER", project_values.DEFAULT_PROJECT_NUMBER)),
        )

    def rest(
        self,
        method: str,
        path: str,
        request_document: dict[str, project_values.JsonValue] | None = None,
    ) -> project_values.JsonValue:
        """Send a REST request to GitHub.

        Returns:
            The decoded response document.

        """
        return self._transport.request(method, path, request_document)

    def graphql(
        self, query: str, variables: project_values.GraphQLVariables = None,
    ) -> dict[str, project_values.JsonValue]:
        """Send a GraphQL request to GitHub.

        Returns:
            The data object from the response.

        Raises:
            GitHubProjectError: If GitHub returns GraphQL errors.

        """
        payload = json_object(self._graphql_response(query, variables), "GraphQL response")
        errors = payload.get("errors")
        if errors:
            detail = json.JSONEncoder(ensure_ascii=False).encode(errors)
            msg = f"GitHub GraphQL error: {detail}"
            raise GitHubProjectError(msg)
        return json_object(payload.get("data"), "GraphQL data")

    def schema(self) -> ProjectSchema:
        """Read the configured project's field schema.

        Returns:
            The validated project schema.

        """
        query = """
        query($owner: String!, $number: Int!) {
          user(login: $owner) {
            projectV2(number: $number) {
              id title url
              fields(first: 50) {
                nodes {
                  ... on ProjectV2FieldCommon { id name }
                  ... on ProjectV2SingleSelectField { options { id name } }
                }
              }
            }
          }
        }
        """
        return project_schema(
            self.graphql(
                query,
                {"owner": self.owner, project_values.NUMBER_FIELD: self.project_number},
            ),
            self.owner,
            self.project_number,
        )

    def _graphql_response(self, query: str, variables: project_values.GraphQLVariables) -> project_values.JsonValue:
        """Send one GraphQL request.

        Returns:
            The decoded response, including any GraphQL errors.

        """
        request_variables: dict[str, project_values.JsonValue] = {} if variables is None else variables
        request_document: dict[str, project_values.JsonValue] = {"query": query, "variables": request_variables}
        return self.rest("POST", "/graphql", request_document)


class _GitHubProjectRead(_GitHubProjectState):
    """Read GitHub project issues."""

    def issues(
        self,
        *,
        status: str | None = None,
        area: str | None = None,
        work_type: str | None = None,
        priority: str | None = None,
    ) -> list[Issue]:
        """Read all project issue pages and apply the supplied filters.

        Returns:
            The matching repository issues in project order.

        """
        validate_issue_filters(status, area, work_type, priority)
        query = """
        query($owner: String!, $number: Int!, $cursor: String) {
          user(login: $owner) {
            projectV2(number: $number) {
              items(first: 100, after: $cursor) {
                pageInfo { hasNextPage endCursor }
                nodes {
                  id
                  fieldValues(first: 30) {
                    nodes {
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        name
                        field { ... on ProjectV2FieldCommon { name } }
                      }
                    }
                  }
                  content {
                    ... on Issue {
                      id number title body url state
                      repository { nameWithOwner }
                    }
                  }
                }
              }
            }
          }
        }
        """
        cursor: str | None = None
        result: list[Issue] = []
        while True:
            page_issues, next_cursor = self._issue_page(query, cursor)
            result.extend(page_issues)
            if next_cursor is None:
                break
            cursor = next_cursor
        return filter_issues(result, status, area, work_type, priority)

    def find_issue(self, query: project_values.IssueQuery) -> Issue:
        """Return issue.

        Returns:
            Issue.

        """
        text = str(query)
        exact = [issue for issue in self.issues() if is_exact_issue_match(issue, text)]
        if exact:
            return only_selection(exact, f"issue matching {text!r}")
        return only_selection(
            [issue for issue in self.issues() if is_partial_issue_match(issue, text)],
            f"issue matching {text!r}",
        )

    def _issue_page(self, query: str, cursor: str | None) -> IssuePage:
        response_document = self.graphql(
            query,
            {"owner": self.owner, project_values.NUMBER_FIELD: self.project_number, "cursor": cursor},
        )
        connection = project_item_connection(response_document)
        issues = issues_from_connection(connection, self.repository)
        next_cursor = next_page_cursor(connection)
        return issues, next_cursor


class _GitHubProjectViews(_GitHubProjectRead):
    """Create and update project views."""

    def views(self) -> list[ProjectView]:
        """Read the project's first page of views.

        Returns:
            Up to 50 project views.

        """
        query = """
        query($owner: String!, $number: Int!) {
          user(login: $owner) {
            projectV2(number: $number) {
              views(first: 50) {
                nodes { id number name layout filter }
              }
            }
          }
        }
        """
        response_document = self.graphql(query, {"owner": self.owner, project_values.NUMBER_FIELD: self.project_number})
        project = json_object(
            json_object(response_document.get("user"), "GitHub user").get("projectV2"),
            project_values.PROJECT_VARIABLE,
        )
        connection = json_object(project.get("views"), "project view connection")
        return [
            parse_project_view(view_document)
            for view_document in json_objects(connection.get(project_values.NODES_FIELD), "project views")
        ]

    def create_view(
        self,
        name: str,
        *,
        filter_query: str = "",
        layout: str = "BOARD_LAYOUT",
        visible_fields: tuple[str, ...] = (
            project_values.AREA_FIELD,
            project_values.TYPE_FIELD,
            project_values.PRIORITY_FIELD,
        ),
    ) -> ProjectView:
        """Create a project view with the requested display settings.

        Returns:
            The created view, after any requested filter update.

        Raises:
            GitHubProjectError: If the name is empty or already used.

        """
        if not name.strip():
            msg = "View name must not be empty"
            raise GitHubProjectError(msg)
        require_choice(layout, project_values.VIEW_LAYOUTS, "view layout")
        normalized_name = name.casefold()
        duplicates = [view for view in self.views() if view.name.casefold() == normalized_name]
        if duplicates:
            msg = f"Project view already exists: {duplicates[0].name}"
            raise GitHubProjectError(msg)
        view = self._create_view(name, layout, visible_fields)
        if filter_query:
            return self.update_view(view.id, filter_query=filter_query)
        return view

    def update_view(
        self,
        query: str,
        *,
        name: str | None = None,
        filter_query: str | None = None,
        layout: str | None = None,
        visible_fields: tuple[str, ...] | None = None,
    ) -> ProjectView:
        """Change the supplied settings of a project view.

        Returns:
            The updated view.

        Raises:
            GitHubProjectError: If no setting is supplied.

        """
        if layout is not None:
            require_choice(layout, project_values.VIEW_LAYOUTS, "view layout")
        view = self._find_view(query)
        mutation = ViewMutation.for_view(view.id)
        if name is not None:
            mutation.add(project_values.NAME_FIELD, name, "$name: String", "name: $name")
        if filter_query is not None:
            mutation.add("filter", filter_query, "$filter: String", "filter: $filter")
        if layout is not None:
            mutation.add("layout", layout, "$layout: ProjectV2ViewLayout", "layout: $layout")
        if visible_fields is not None:
            self._add_visible_fields(visible_fields, mutation)
        if len(mutation.assignments) == 1:
            msg = "No view update was provided"
            raise GitHubProjectError(msg)
        response_document = self.graphql(mutation.query(), mutation.variables)
        return updated_view(response_document)

    def _add_visible_fields(
        self,
        visible_fields: tuple[str, ...],
        mutation: ViewMutation,
    ) -> None:
        """Add visible fields to a view mutation."""
        schema = self.schema()
        field_ids: list[project_values.JsonValue] = [schema.field(field_name).id for field_name in visible_fields]
        mutation.add(
            "fields",
            field_ids,
            "$fields: [ID!]",
            "configuration: {visibleFieldIds: $fields}",
        )

    def _find_view(self, query: str) -> ProjectView:
        matches = [view for view in self.views() if is_exact_view_match(view, query)]
        return only_selection(matches, f"project view matching {query!r}")

    def _create_view(
        self,
        name: str,
        layout: str,
        visible_fields: tuple[str, ...],
    ) -> ProjectView:
        schema = self.schema()
        visible_ids: list[project_values.JsonValue] = [schema.field(field_name).id for field_name in visible_fields]
        mutation = """
        mutation($project: ID!, $name: String!, $layout: ProjectV2ViewLayout!, $fields: [ID!]) {
          createProjectV2View(input: {
            projectId: $project,
            name: $name,
            layout: $layout,
            configuration: {visibleFieldIds: $fields}
          }) { projectV2View { id number name layout filter } }
        }
        """
        response_document = self.graphql(
            mutation,
            {
                project_values.PROJECT_VARIABLE: schema.id,
                project_values.NAME_FIELD: name,
                "layout": layout,
                "fields": visible_ids,
            },
        )
        result = json_object(response_document.get("createProjectV2View"), "create view result")
        return parse_project_view(json_object(result.get("projectV2View"), "project view"))


class _GitHubProjectInteraction(_GitHubProjectViews):
    """Manage comments and backlog order."""

    def add_comment(self, query: str | int, body: str) -> dict[str, project_values.JsonValue]:
        """Add a comment to the selected issue.

        Returns:
            The comment document from GitHub.

        Raises:
            GitHubProjectError: If the comment text is empty.

        """
        if not body.strip():
            msg = "Comment must not be empty"
            raise GitHubProjectError(msg)
        issue = self.find_issue(query)
        return json_object(
            self.rest(
                "POST",
                f"/repos/{self.repository}/issues/{issue.number}/comments",
                {project_values.BODY_FIELD: body},
            ),
            "comment",
        )

    def comments(self, query: str | int) -> list[dict[str, project_values.JsonValue]]:
        """Read the first page of comments for an issue.

        Returns:
            Up to 100 comment documents.

        """
        issue = self.find_issue(query)
        return json_objects(
            self.rest("GET", f"/repos/{self.repository}/issues/{issue.number}/comments?per_page=100"),
            "comments",
        )

    def backlog(self) -> list[Issue]:
        """Read backlog issues in priority order.

        Returns:
            The backlog sorted by priority and then issue number.

        """
        return sorted(self.issues(status=project_values.BACKLOG_STATUS), key=backlog_order)

    def sort_backlog(self, *, apply: bool = False) -> list[Issue]:
        """Calculate backlog order and optionally save it to GitHub.

        Returns:
            The sorted backlog, read again after changes are applied.

        """
        ordered = self.backlog()
        if not apply:
            return ordered
        schema = self.schema()
        mutation = """
        mutation($project: ID!, $item: ID!, $after: ID) {
          updateProjectV2ItemPosition(input: {
            projectId: $project,
            itemId: $item,
            afterId: $after
          }) { items(first: 1) { nodes { id } } }
        }
        """
        previous: str | None = None
        for issue in ordered:
            self.graphql(
                mutation,
                {project_values.PROJECT_VARIABLE: schema.id, "item": issue.item_id, "after": previous},
            )
            previous = issue.item_id
        return self.backlog()


class _GitHubProjectCreation(_GitHubProjectInteraction):
    """Create repository issues and project items."""

    def create_issue(
        self,
        new_issue: NewIssue,
        *,
        allow_duplicate: bool = False,
    ) -> Issue:
        """Create a repository issue and set its project fields.

        Returns:
            The new issue with its project fields.

        """
        validate_new_issue(new_issue)
        self._check_issue_is_new(new_issue, allow_duplicate=allow_duplicate)
        created = self._create_repository_issue(new_issue)
        schema = self.schema()
        item_id = self._add_project_item(schema.id, text_field(created, "node_id"))
        issue = new_issue_from_document(created, item_id, new_issue)
        self._set_issue_fields(item_id, schema, issue)
        if new_issue.status == project_values.BACKLOG_STATUS:
            self.sort_backlog(apply=True)
        return issue

    def _check_issue_is_new(self, new_issue: NewIssue, *, allow_duplicate: bool) -> None:
        duplicates = [issue for issue in self.issues() if is_open_issue_duplicate(issue, new_issue)]
        if duplicates and not allow_duplicate:
            msg = f"Open issue already exists: {duplicates[0].url}"
            raise GitHubProjectError(msg)

    def _create_repository_issue(self, new_issue: NewIssue) -> dict[str, project_values.JsonValue]:
        return json_object(
            self.rest(
                "POST",
                f"/repos/{self.repository}/issues",
                {project_values.TITLE_FIELD: new_issue.title, project_values.BODY_FIELD: new_issue.body},
            ),
            "created issue",
        )

    def _add_project_item(self, project_id: str, content_id: str) -> str:
        mutation = """
        mutation($project: ID!, $content: ID!) {
          addProjectV2ItemById(input: {projectId: $project, contentId: $content}) {
            item { id }
          }
        }
        """
        response_document = self.graphql(
            mutation,
            {project_values.PROJECT_VARIABLE: project_id, "content": content_id},
        )
        add_result = json_object(response_document.get("addProjectV2ItemById"), "add item result")
        return text_field(json_object(add_result.get("item"), "project item"), project_values.IDENTIFIER_FIELD)

    def _set_issue_fields(
        self,
        item_id: str,
        schema: ProjectSchema,
        issue: Issue,
    ) -> None:
        """Set the required project fields for a new issue.

        Raises:
            GitHubProjectError: If a required field has no value.

        """
        for field_name, option_name in (
            (project_values.STATUS_FIELD, issue.status),
            (project_values.AREA_FIELD, issue.area),
            (project_values.TYPE_FIELD, issue.work_type),
            (project_values.PRIORITY_FIELD, issue.priority),
        ):
            if option_name is None:
                message = f"new issue has no {field_name} value"
                raise GitHubProjectError(message)
            self._set_field(item_id, schema, field_name, option_name)

    def _set_issue_field(self, query: str | int, field_name: str, option_name: str) -> Issue:
        issue = self.find_issue(query)
        self._set_field(issue.item_id, self.schema(), field_name, option_name)
        return self.find_issue(issue.number)

    def _set_field(self, item_id: str, schema: ProjectSchema, field_name: str, option_name: str) -> None:
        field = schema.field(field_name)
        option = only_selection(
            [field_option for field_option in field.options if field_option.name == option_name],
            f"{field_name} option {option_name!r}",
        )
        mutation = """
        mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $project,
            itemId: $item,
            fieldId: $field,
            value: {singleSelectOptionId: $option}
          }) { projectV2Item { id } }
        }
        """
        variables: dict[str, project_values.JsonValue] = {
            project_values.PROJECT_VARIABLE: schema.id,
            "item": item_id,
            "field": field.id,
            "option": option.id,
        }
        self.graphql(mutation, variables)


class _GitHubProjectUpdates(_GitHubProjectCreation):
    """Update issue fields and lifecycle state."""

    def update_issue(
        self,
        query: project_values.IssueQuery,
        *,
        title: project_values.IssueUpdateText = None,
        body: project_values.IssueUpdateText = None,
    ) -> Issue:
        """Change the supplied title or body of an issue.

        Returns:
            The issue read after the update.

        Raises:
            GitHubProjectError: If neither title nor body is supplied.

        """
        if title is None and body is None:
            msg = "No issue update was provided"
            raise GitHubProjectError(msg)
        issue = self.find_issue(query)
        update_document: dict[str, project_values.JsonValue] = {}
        if title is not None:
            update_document[project_values.TITLE_FIELD] = title
        if body is not None:
            update_document[project_values.BODY_FIELD] = body
        self.rest("PATCH", f"/repos/{self.repository}/issues/{issue.number}", update_document)
        return self.find_issue(issue.number)

    def set_status(self, query: str | int, status: str) -> Issue:
        """Set the issue's project status.

        Returns:
            The issue with its updated status.

        """
        require_choice(status, project_values.STATUSES, project_values.STATUS_CHOICE)
        return self._set_issue_field(query, project_values.STATUS_FIELD, status)

    def set_work_type(self, query: str | int, work_type: str) -> Issue:
        """Set the issue's work type.

        Returns:
            The issue with its updated work type.

        """
        require_choice(work_type, project_values.WORK_TYPES, "work type")
        return self._set_issue_field(query, project_values.TYPE_FIELD, work_type)

    def set_area(self, query: str | int, area: str) -> Issue:
        """Set the issue's project area.

        Returns:
            The issue with its updated area.

        """
        require_choice(area, project_values.AREAS, project_values.AREA_CHOICE)
        return self._set_issue_field(query, project_values.AREA_FIELD, area)

    def set_priority(self, query: str | int, priority: str) -> Issue:
        """Set the issue's project priority.

        Returns:
            The issue with its updated priority.

        """
        require_choice(priority, project_values.PRIORITIES, project_values.PRIORITY_CHOICE)
        return self._set_issue_field(query, project_values.PRIORITY_FIELD, priority)

    def close_issue(self, query: str | int) -> Issue:
        """Close the selected repository issue.

        Returns:
            The issue read after it is closed.

        """
        issue = self.find_issue(query)
        issue_path = f"/repos/{self.repository}/issues/{issue.number}"
        request_document: dict[str, project_values.JsonValue] = {project_values.STATE_FIELD: "closed"}
        self.rest("PATCH", issue_path, request_document)
        return self.find_issue(issue.number)

    def reopen_issue(self, query: str | int) -> Issue:
        """Reopen the selected repository issue.

        Returns:
            The issue read after it is reopened.

        """
        issue = self.find_issue(query)
        issue_path = f"/repos/{self.repository}/issues/{issue.number}"
        request_document: dict[str, project_values.JsonValue] = {project_values.STATE_FIELD: "open"}
        self.rest("PATCH", issue_path, request_document)
        return self.find_issue(issue.number)


class GitHubProjectClient(_GitHubProjectUpdates):
    """Manage Baqylau issues and their GitHub Project fields."""
