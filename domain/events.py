# Copyright (c) 2026 Zhambyl Yermagambet
"""Map the closed canonical event vocabulary to stored type names."""

from collections.abc import Mapping
from types import MappingProxyType

from domain import (
    event_actor,
    event_conversation,
    event_resource,
    event_session,
    event_shell,
    event_telemetry,
    event_work,
)
from domain.event_base import EventPayload

EVENT_TYPES: Mapping[type[EventPayload], str] = MappingProxyType(
    {
        event_session.SessionStarted: "session.started",
        event_session.SessionTitleChanged: "session.title_changed",
        event_session.SessionAccountChanged: "session.account_changed",
        event_session.SessionFinished: "session.finished",
        event_session.ModelChanged: "model.changed",
        event_session.EffortChanged: "effort.changed",
        event_actor.ActorStarted: "actor.started",
        event_actor.ActorNameChanged: "actor.name_changed",
        event_actor.ActorDescriptionChanged: "actor.description_changed",
        event_actor.ActorAssignmentStarted: "actor.assignment_started",
        event_actor.ActorAssignmentFinished: "actor.assignment_finished",
        event_actor.ActorFinished: "actor.finished",
        event_conversation.TurnStarted: "turn.started",
        event_conversation.TurnFinished: "turn.finished",
        event_conversation.TurnAborted: "turn.aborted",
        event_conversation.MessageCreated: "message.created",
        event_conversation.MessageQueued: "message.queued",
        event_conversation.ReasoningCreated: "reasoning.created",
        event_shell.ShellStarted: "shell.started",
        event_shell.ShellInputProvided: "shell.input_provided",
        event_shell.ShellProgressed: "shell.progressed",
        event_shell.ShellFinished: "shell.finished",
        event_shell.ShellOutputLocated: "shell.output_located",
        event_shell.ShellBackgrounded: "shell.backgrounded",
        event_shell.ShellOutputFinished: "shell.output_finished",
        event_resource.FileAccessed: "file.accessed",
        event_resource.SearchPerformed: "search.performed",
        event_resource.SkillStarted: "skill.started",
        event_resource.SkillFinished: "skill.finished",
        event_resource.WebFetched: "web.fetched",
        event_resource.BrowserInteracted: "browser.interacted",
        event_resource.WorktreeChanged: "worktree.changed",
        event_work.TaskChanged: "task.changed",
        event_work.TaskListChanged: "task.list_changed",
        event_work.GoalChanged: "goal.changed",
        event_work.QuestionAsked: "question.asked",
        event_work.QuestionAnswered: "question.answered",
        event_work.PlanProposed: "plan.proposed",
        event_work.PlanResolved: "plan.resolved",
        event_telemetry.UsageReported: "usage.reported",
        event_telemetry.ContextReported: "context.reported",
        event_telemetry.CompactionStarted: "compaction.started",
        event_telemetry.CompactionFinished: "compaction.finished",
    },
)

PAYLOAD_TYPES: Mapping[str, type[EventPayload]] = MappingProxyType(
    {event_type: payload_type for payload_type, event_type in EVENT_TYPES.items()},
)

# Increase this value when an old stored payload cannot decode a new shape.
SCHEMA_VERSION = 19
