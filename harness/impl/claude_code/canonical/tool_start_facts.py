# Copyright (c) 2026 Zhambyl Yermagambet
"""Build Claude Code tool start facts."""

from domain import event_actor, event_base, event_conversation, event_resource, event_shell, messaging, outcomes
from harness.impl.claude_code import ids as claude_ids
from harness.impl.claude_code.canonical import records, support, tool_kind_values as kind_values, transcript
from harness.models import raw_events


def shell_started(
    raw_event: raw_events.RawEvent,
    call_id: claude_ids.ClaudeCodeCallId,
    native_name: str,
    arguments: records.ToolArguments,
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Map a shell start and its execution mode.

    Returns:
        The shell start event with command content and an optional description.

    """
    shell_id = claude_ids.shell_id_from_claude_code_call(call_id)
    if native_name == kind_values.MONITOR_TOOL_NAME:
        execution = outcomes.ExecutionMode.MONITOR
    elif native_name == "Bash" and arguments.run_in_background:
        execution = outcomes.ExecutionMode.BACKGROUND
    else:
        execution = outcomes.ExecutionMode.FOREGROUND
    command = arguments.command
    shell_content = support.content(arguments)
    if isinstance(command, str) and command:
        shell_content = support.content(command)
    payload = event_shell.ShellStarted(
        shell_id,
        shell_content,
        execution,
        arguments.description or None,
    )
    return support.event(
        raw_event,
        support.CanonicalEventDraft(kind_values.ToolKind.SHELL.value, str(shell_id), "started", payload),
    )


def skill_started(
    raw_event: raw_events.RawEvent,
    call_id: claude_ids.ClaudeCodeCallId,
    arguments: records.ToolArguments,
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Map a skill invocation.

    Returns:
        The skill start event with its name and optional arguments.

    """
    skill_id = claude_ids.skill_id_from_claude_code_call(call_id)
    name = str(arguments.skill or "")
    payload = event_resource.SkillStarted(
        skill_id,
        name,
        support.content(arguments.args) if arguments.args else None,
    )
    draft = support.CanonicalEventDraft(kind_values.ToolKind.SKILL.value, str(skill_id), "started", payload)
    return support.event(raw_event, draft)


def assignment_started(
    raw_event: raw_events.RawEvent,
    call_id: claude_ids.ClaudeCodeCallId,
    arguments: records.ToolArguments,
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Map a new actor assignment.

    Returns:
        The assignment start event with its description, actor name, and prompt.

    """
    assignment_id = claude_ids.assignment_id_from_claude_code_call(call_id)
    actor_name = arguments.name or arguments.subagent_type
    prompt = arguments.prompt
    payload = event_actor.ActorAssignmentStarted(
        assignment_id,
        support.content(arguments.description or prompt or ""),
        actor_name=str(actor_name) if actor_name else None,
        prompt=support.content(prompt, markdown=True) if prompt else None,
    )
    draft = support.CanonicalEventDraft("actor_assignment", str(assignment_id), "started", payload)
    return support.event(raw_event, draft)


def actor_message(
    raw_event: raw_events.RawEvent,
    call_id: claude_ids.ClaudeCodeCallId,
    arguments: records.ToolArguments,
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Map an outgoing actor message and resolve its recipient.

    Returns:
        The intermediate assistant message addressed to its parent or peer.

    """
    recipient_text = str(arguments.recipient or arguments.to or "peer")
    recipient = (
        raw_event.parent_actor_id
        if recipient_text == transcript.LEAD_TEAMMATE_ID and raw_event.parent_actor_id is not None
        else claude_ids.actor_id_from_claude_code(claude_ids.ClaudeCodeActorId(recipient_text))
    )
    message_id = claude_ids.message_id_from_claude_code_call(call_id)
    payload = event_conversation.MessageCreated(
        message_id,
        messaging.MessageRole.ASSISTANT,
        support.content(arguments.content or arguments.message, markdown=True),
        messaging.MessagePhase.INTERMEDIATE,
        None,
        recipient,
    )
    draft = support.CanonicalEventDraft("message", str(message_id), "created", payload)
    return support.event(raw_event, draft)
