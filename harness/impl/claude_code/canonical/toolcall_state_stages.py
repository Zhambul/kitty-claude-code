# Copyright (c) 2026 Zhambyl Yermagambet
"""Own tool-call state, memory, and assignments."""

from __future__ import annotations

from harness.impl.claude_code.canonical import (
    toolcall_domain_dependencies as domain_dependencies,
    toolcall_runtime_dependencies as runtime_dependencies,
)


class _ToolCallState:
    """Store transient tool call state."""

    def __init__(self) -> None:
        """Initialize the object."""
        self.calls: dict[
            tuple[domain_dependencies.ids.SessionId, runtime_dependencies.ids.ClaudeCodeCallId],
            runtime_dependencies.tool_state_models.RememberedCall,
        ] = {}
        self.loaded_skills: set[tuple[domain_dependencies.ids.SessionId, runtime_dependencies.ids.ClaudeCodeCallId]] = (
            set()
        )
        self.agent_assignments: dict[
            tuple[domain_dependencies.ids.SessionId, runtime_dependencies.ids.ClaudeCodeActorId],
            runtime_dependencies.tool_state_models.AgentAssignmentState,
        ] = {}
        # An armed Monitor's TASK id -> the shell that armed it, and how many
        # of its events have been attributed so far. A monitor's per-event
        # notification names only the task id — never the tool_use_id (measured
        # in claude-code 2.1.233) — so this is the only route from an event back
        # to the command the monitors tab lists. Its stream-ENDED notification
        # does carry the tool_use_id, so the end needs no memory and survives a
        # daemon restart that loses this.
        self.monitors: dict[
            tuple[domain_dependencies.ids.SessionId, runtime_dependencies.ids.ClaudeCodeShellId],
            runtime_dependencies.tool_state_models.MonitorState,
        ] = {}
        # A background task's native id -> the Bash shell that launched it.
        # TaskStop names only this task id, so the stop needs this link to close
        # the shell. The runtime_dependencies.transcript is the durable fallback after a restart.
        self.background_tasks: dict[
            tuple[domain_dependencies.ids.SessionId, runtime_dependencies.ids.ClaudeCodeShellId],
            runtime_dependencies.tool_state_models.BackgroundTaskState,
        ] = {}


class _ToolCallMemory(_ToolCallState):
    """Remember native tool calls across event streams."""

    def remember(
        self,
        raw_event: runtime_dependencies.raw_events.RawEvent,
        call_id: runtime_dependencies.ids.ClaudeCodeCallId,
        native_name: str,
        arguments: runtime_dependencies.records.ToolArguments,
    ) -> None:
        """Return the remember."""
        key = raw_event.session_id, call_id
        self.calls[key] = runtime_dependencies.tool_state_models.RememberedCall(
            raw_event.session_id,
            call_id,
            native_name,
            arguments,
        )

    def recall(
        self,
        raw_event: runtime_dependencies.raw_events.RawEvent,
        call_id: runtime_dependencies.ids.ClaudeCodeCallId,
        native_name: str | None,
        arguments: runtime_dependencies.records.ToolArguments | None,
    ) -> tuple[str, runtime_dependencies.records.ToolArguments]:
        """Return the recall.

        The call's name and input: what this record carries, else what the
                request said. A record that has neither is a call whose start we never
                saw — a daemon that restarted mid-call — and it cannot be classified.

        Returns:
            Recall.

        Raises:
            UnknownRawEventError: If neither the result nor stored call has a tool name.

        """
        remembered = self.calls.get((raw_event.session_id, call_id))
        remembered_name = "" if remembered is None else remembered.native_name
        name = native_name or remembered_name
        if not name:
            reported_call_id = call_id or "<missing>"
            message = f"Claude Code tool result names no call: {reported_call_id}"
            raise runtime_dependencies.raw_events.UnknownRawEventError(message)
        return name, arguments or runtime_dependencies.tool_state_models.remembered_arguments(remembered)

    def known(
        self, raw_event: runtime_dependencies.raw_events.RawEvent, call_id: runtime_dependencies.ids.ClaudeCodeCallId,
    ) -> bool:
        """Return the known.

        Returns:
            Known.

        """
        return (raw_event.session_id, call_id) in self.calls

    def is_skill(
        self, raw_event: runtime_dependencies.raw_events.RawEvent, call_id: runtime_dependencies.ids.ClaudeCodeCallId,
    ) -> bool:
        """Return true if skill.

        Returns:
            True if skill.

        """
        remembered = self.calls.get((raw_event.session_id, call_id))
        return remembered is not None and remembered.native_name == "Skill"

    def forget(
        self, raw_event: runtime_dependencies.raw_events.RawEvent, call_id: runtime_dependencies.ids.ClaudeCodeCallId,
    ) -> None:
        """Release a call after all result channels have used its input."""
        self.calls.pop((raw_event.session_id, call_id), None)

    def clear_session(self, session_id: domain_dependencies.ids.SessionId) -> None:
        """Release all transient correlation after one native session ends."""
        for call_key in tuple(self.calls):
            if call_key[0] == session_id:
                self.calls.pop(call_key, None)
        for assignment_key in tuple(self.agent_assignments):
            if assignment_key[0] == session_id:
                self.agent_assignments.pop(assignment_key, None)
        for monitor_key in tuple(self.monitors):
            if monitor_key[0] == session_id:
                self.monitors.pop(monitor_key, None)
        for background_key in tuple(self.background_tasks):
            if background_key[0] == session_id:
                self.background_tasks.pop(background_key, None)
        self.loaded_skills = {key for key in self.loaded_skills if key[0] != session_id}

    def skill_loaded(
        self,
        raw_event: runtime_dependencies.raw_events.RawEvent,
        name: str,
        output: str,
    ) -> domain_dependencies.event_base.CanonicalEvent[domain_dependencies.event_base.EventPayload] | None:
        """Finish the most recent matching Skill call with its loaded file.

        Claude's Skill tool first answers with an empty ``{}``, then injects a
        synthetic prompt containing the actual SKILL.md text.  The injected
        prompt is the useful result of the call, not a separate conversation
        message.  It has no tool-use id, so join it to the newest unclaimed
        matching call in this session.

        Returns:
            The canonical event.

        """
        for remembered in reversed(tuple(self.calls.values())):
            key = remembered.session_id, remembered.call_id
            if (
                remembered.session_id != raw_event.session_id
                or remembered.native_name != "Skill"
                or str(remembered.arguments.skill or "") != name
                or key in self.loaded_skills
            ):
                continue
            self.loaded_skills.add(key)
            skill_id = runtime_dependencies.ids.skill_id_from_claude_code_call(remembered.call_id)
            return runtime_dependencies.support.event(
                raw_event,
                runtime_dependencies.support.CanonicalEventDraft(
                    runtime_dependencies.tool_kind_values.ToolKind.SKILL.value,
                    str(skill_id),
                    runtime_dependencies.tool_values.FINISHED_PHASE,
                    domain_dependencies.event_resource.SkillFinished(
                        skill_id,
                        domain_dependencies.outcomes.Outcome.SUCCEEDED,
                        runtime_dependencies.support.content(output),
                    ),
                ),
            )
        return None


class _ToolCallAssignments(_ToolCallMemory):
    """Track child assignment tool calls."""

    def assignment_launched(
        self,
        raw_event: runtime_dependencies.raw_events.RawEvent,
        actor_id: runtime_dependencies.ids.ClaudeCodeActorId,
        call_id: runtime_dependencies.ids.ClaudeCodeCallId,
    ) -> None:
        """Return the assignment launched."""
        key = raw_event.session_id, actor_id
        self.agent_assignments[key] = runtime_dependencies.tool_state_models.AgentAssignmentState(
            raw_event.session_id,
            actor_id,
            call_id,
        )

    def assignment_call(
        self,
        raw_event: runtime_dependencies.raw_events.RawEvent,
        actor_id: runtime_dependencies.ids.ClaudeCodeActorId | None,
        notification_call_id: runtime_dependencies.ids.ClaudeCodeCallId,
    ) -> runtime_dependencies.ids.ClaudeCodeCallId:
        """Return the Agent call that owns one child completion.

        A resumed async child names the SendMessage call in its final task
        notification. The Agent result is the durable child-to-assignment
        relation. Keep the live relation in memory and recover it from the
        parent runtime_dependencies.transcript after an application restart.

        Returns:
            Agent call that owns one child completion.

        """
        if actor_id is None:
            return notification_call_id
        remembered = self.agent_assignments.get((raw_event.session_id, actor_id))
        if remembered is not None:
            return remembered.call_id
        durable = runtime_dependencies.transcript.assignment_call_before(
            raw_event.source_name,
            raw_event.source_position,
            actor_id,
        )
        if durable is not None:
            self.assignment_launched(raw_event, actor_id, durable)
            return durable
        return notification_call_id

    def assignment_finished(
        self,
        raw_event: runtime_dependencies.raw_events.RawEvent,
        actor_id: runtime_dependencies.ids.ClaudeCodeActorId | None,
    ) -> None:
        """Return the assignment finished."""
        if actor_id is not None:
            self.agent_assignments.pop((raw_event.session_id, actor_id), None)

    def _assignment_finished(
        self,
        raw_event: runtime_dependencies.raw_events.RawEvent,
        call_id: runtime_dependencies.ids.ClaudeCodeCallId,
        tool_response: runtime_dependencies.records.ToolResponse,
        outcome: domain_dependencies.outcomes.Outcome,
    ) -> list[domain_dependencies.event_base.CanonicalEvent[domain_dependencies.event_base.EventPayload]]:
        async_launched = tool_response.is_async is True or tool_response.status in {
            "async_launched",
            "teammate_spawned",
        }
        if async_launched:
            native_actor_id = runtime_dependencies.ids.ClaudeCodeActorId(
                str(tool_response.external_agent_id or tool_response.agent_id or ""),
            )
            if tool_response.status == "teammate_spawned" and tool_response.name:
                native_actor_id = runtime_dependencies.transcript.teammate_actor_id(
                    raw_event.source_name,
                    tool_response.name,
                ) or runtime_dependencies.ids.ClaudeCodeActorId(tool_response.name)
            if native_actor_id:
                self.assignment_launched(
                    raw_event,
                    native_actor_id,
                    call_id,
                )
            return []
        # A successful Agent hook says that the tool call returned. It does not
        # carry the subagent result. Claude Code sends the semantic completion
        # as a task notification, with the result. If this hook writes the same
        # canonical identity first, normal deduplication must discard the richer
        # notification. Keep a failed hook because no successful completion
        # notification will follow it.
        if outcome == domain_dependencies.outcomes.Outcome.SUCCEEDED:
            return []
        assignment_id = runtime_dependencies.ids.assignment_id_from_claude_code_call(call_id)
        payload = domain_dependencies.event_actor.ActorAssignmentFinished(assignment_id, outcome, None, None)
        return [
            runtime_dependencies.support.event(
                raw_event,
                runtime_dependencies.support.CanonicalEventDraft(
                    "actor_assignment", str(assignment_id), runtime_dependencies.tool_values.FINISHED_PHASE, payload,
                ),
            ),
        ]
