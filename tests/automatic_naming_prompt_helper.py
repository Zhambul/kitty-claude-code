# Copyright (c) 2026 Zhambyl Yermagambet
"""Durable jobs, title safety, and generic naming semantics."""

from domain import (
    content as domain_content,
    event_base,
    event_conversation,
    ids as domain_ids,
    messaging,
)
from harness.impl.claude_code.plugin import plugin as claude_plugin
from harness.impl.codex.plugin import plugin as codex_plugin
from tests.automatic_naming_values import ACTOR_ID, SESSION_ID


def prompt_event(*, claude: bool = False) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Build a user prompt event for the selected harness.

    Returns:
        The fixed prompt event for Claude Code or Codex.

    """
    plugin = claude_plugin if claude else codex_plugin
    return event_base.CanonicalEvent(
        event_id=domain_ids.CanonicalEventId("prompt-event"),
        session_id=SESSION_ID,
        actor_id=ACTOR_ID,
        turn_id=None,
        parent_actor_id=None,
        harness=plugin.harness_info.name,
        occurred_at=1.0,
        terminal_window_id=None,
        harness_process_id=None,
        payload=event_conversation.MessageCreated(
            domain_ids.MessageId("message-one"),
            messaging.MessageRole.USER,
            domain_content.TextContent("A very long first semantic prompt"),
            messaging.MessagePhase.PROMPT,
            None,
        ),
    )
