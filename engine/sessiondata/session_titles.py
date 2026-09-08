# Copyright (c) 2026 Zhambyl Yermagambet
"""Apply title changes to session facts."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from domain.content import TextContent
from domain.event_conversation import MessageCreated

if TYPE_CHECKING:
    from domain.event_base import EventPayload
    from domain.event_session import SessionTitleChanged
    from domain.session_state import SessionFacts

PROMPT_TITLE_LIMIT = 200


def is_prompt(event_payload: EventPayload) -> bool:
    """Return whether the event is a user prompt.

    Returns:
        Whether the event is a user prompt.

    """
    return (
        isinstance(event_payload, MessageCreated) and event_payload.role == "user" and event_payload.phase == "prompt"
    )


def titled(session_facts: SessionFacts, session_title_changed: SessionTitleChanged) -> SessionFacts:
    """Return session facts with the changed title.

    Returns:
        Session facts with the changed title.

    """
    title = session_title_changed.title or None
    if session_title_changed.origin == "custom":
        session_facts = replace(session_facts, custom_title_internal=title)
    elif session_title_changed.origin == "automatic":
        session_facts = replace(session_facts, automatic_title_internal=title)
    else:
        session_facts = replace(session_facts, summary_title_internal=title)
    return retitled(session_facts)


def prompt_titled(session_facts: SessionFacts, message_created: MessageCreated) -> SessionFacts:
    """Return session facts with a title derived from the prompt.

    Returns:
        Session facts with a title derived from the prompt.

    """
    if not isinstance(message_created.content, TextContent):
        return session_facts
    lines = message_created.content.text.strip().splitlines()
    if not lines:
        return session_facts
    return retitled(
        replace(session_facts, prompt_title_internal=lines[0][:PROMPT_TITLE_LIMIT]),
    )


def retitled(session_facts: SessionFacts) -> SessionFacts:
    """Return session facts with title precedence applied.

    Returns:
        Session facts with title precedence applied.

    """
    return replace(
        session_facts,
        title=(
            session_facts.custom_title_internal
            or session_facts.automatic_title_internal
            or session_facts.summary_title_internal
            or session_facts.prompt_title_internal
        ),
    )
