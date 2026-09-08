# Copyright (c) 2026 Zhambyl Yermagambet
"""Define GitHub Projects SDK project_values."""

from __future__ import annotations

import re

API_BASE = "https://api.github.com"


DEFAULT_OWNER = "Zhambul"


DEFAULT_REPOSITORY = "Zhambul/baqylau"


DEFAULT_PROJECT_NUMBER = 1


BACKLOG_STATUS = "Backlog"


STATUSES = (BACKLOG_STATUS, "Planning", "In Progress", "Done")


WORK_TYPES = ("Tech Debt", "Code Quality", "Feature", "Bug")


PRIORITIES = ("P0 — Critical", "P1 — High", "P2 — Medium", "P3 — Low")


AREAS = ("Frontend", "Backend", "Frontend + Backend", "Terminal", "Terminal + Backend")


STATUS_FIELD = "Status"


TYPE_FIELD = "Work Type"


PRIORITY_FIELD = "Priority"


AREA_FIELD = "Area"


PRIORITY_PATTERN = re.compile(r"^P(?P<rank>\d+)\b", re.IGNORECASE)


VIEW_LAYOUTS = ("BOARD_LAYOUT", "TABLE_LAYOUT", "ROADMAP_LAYOUT")


NUMBER_FIELD = "number"


NODES_FIELD = "nodes"


IDENTIFIER_FIELD = "id"


TITLE_FIELD = "title"


STATUS_CHOICE = "status"


AREA_CHOICE = "area"


PRIORITY_CHOICE = "priority"


PROJECT_VARIABLE = "project"


NAME_FIELD = "name"


BODY_FIELD = "body"


STATE_FIELD = "state"


ISSUE_ARGUMENT = "issue"


REQUEST_TIMEOUT_SECONDS = 30


UNRANKED_PRIORITY = 1_000_000


type JsonValue = bool | float | int | str | list[JsonValue] | dict[str, JsonValue] | None


type GraphQLVariables = dict[str, JsonValue] | None


type IssueQuery = str | int


type IssueUpdateText = str | None
