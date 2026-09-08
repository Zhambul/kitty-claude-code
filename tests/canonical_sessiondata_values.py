# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared values for canonical session data tests."""

from __future__ import annotations

from tests import canonical_sessiondata_components as sessiondata_components
from tests.canonical_sessiondata_components import domain as session_domain

SESSION = session_domain.ids.SessionId("session-one")
LEAD = session_domain.ids.ActorId("session-one:lead")
CHILD = session_domain.ids.ActorId("child-one")
CHILD_ACTOR_NAME = "Verifier"
WORKING_DIRECTORY = "/work"
CLAUDE_ACTOR_NAME = "claude"
RUNNING_STATE = "running"
FIRST_MESSAGE_ID = session_domain.ids.MessageId("message-one")
CHOSEN_ANSWER = "Chosen"
SHIP_PROMPT = "ship it"
FINISHED_STATE = "finished"
FIRST_TASK_ID = session_domain.ids.TaskId("task-one")
FIRST_TASK_TEXT = "Read it"
SECOND_TASK_ID = session_domain.ids.TaskId("task-two")
TASK_LIST_ID = session_domain.ids.TaskListId("task-list")
EXPLORE_TASK_TEXT = "Explore"
OPUS_MODEL_ID = "claude-opus-5"
OPUS_MODEL_NAME = "Opus 5"
HIGH_EFFORT = "high"
SONNET_MODEL_ID = "sonnet"
SONNET_MODEL_NAME = "sonnet-5"
GO_PROMPT = "go"
WORKING_STATE = "working"
PRIMARY_SHELL_ID = session_domain.ids.ShellId("shell-one")
SHELL_COMMAND = "make test"
SHELL_COMMAND_CONTENT = session_domain.content.TextContent(SHELL_COMMAND)
EXECUTING_STATE = "executing"
UPDATED_FILE_PATH = "/work/a.py"
AWAITING_RESPONSE_STATE = "awaiting_response"
QUESTION_ATTENTION_ID = session_domain.ids.AttentionId("attention-one")
BACKGROUND_SHELL_ID = session_domain.ids.ShellId("background-shell")
FIRST_ASSIGNMENT_ID = session_domain.ids.AssignmentId("assignment-one")
ASSIGNMENT_PROMPT = "Verify it"
LEAD_ACTOR_LABEL = "lead"
MESSAGE_ENTRY_TYPE = "message"
TERMINAL_SHELL_ID = session_domain.ids.ShellId("terminal-shell")
LOW_EFFORT = "low"
PAINT_TOOL_NAME = "paint"
SESSION_FINISH_TIME = 500.0
ACTOR_FINISH_TIME = 9.0
UNKNOWN_ACTOR_CONTEXT_WINDOW_TOKENS = 200
ASSIGNMENT_RESULT_CURSOR = 11
ASSIGNMENT_START_CURSOR = 10
REPLACEMENT_INPUT_TOKENS = 30
COMBINED_INPUT_TOKENS = 40
CONTEXT_USED_TOKENS = 61_000
CONTEXT_WINDOW_TOKENS = 200_000
COMPACTION_RESULT_TOKENS = 4_000
UPDATED_FILE_LINE_COUNT = 12
FIRST_TURN_FINISH_TIME = 130.0
SECOND_TURN_START_TIME = 200.0
FIRST_ACTIVE_INTERVAL_SECONDS = 30.0
ACCEPTED_TURN_FINISH_TIME = 142.0
ACCEPTED_ACTIVE_INTERVAL_SECONDS = 42.0
ENTRY_OCCURRED_AT = 1_755_590_100.0

WRITERS = (
    sessiondata_components.engine.session.SessionWriter(),
    sessiondata_components.engine.session.GoalWriter(),
    sessiondata_components.engine.session.TaskWriter(),
    sessiondata_components.engine.actors.ActorWriter(),
    sessiondata_components.engine.actors.StatusWriter(),
    sessiondata_components.engine.actors.UsageWriter(),
    sessiondata_components.engine.actors.ContextWriter(),
    sessiondata_components.engine.actors.StatisticsWriter(),
)

A_START = session_domain.event_session.SessionStarted(
    working_directory=WORKING_DIRECTORY,
    source_reference="transcript",
    resumed_from=None,
    title=None,
    model=None,
    effort=None,
    account=None,
)
