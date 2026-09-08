# Copyright (c) 2026 Zhambyl Yermagambet
"""Select the first semantic user prompt from session data."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeGuard

from domain.content import content_text
from domain.entry_conversation import MessageBody
from naming.errors import MissingSessionPromptError

if TYPE_CHECKING:
    from domain.entry_base import EntryBody
    from harness.models.session import (
        Session,
    )
    from repository.contract.session_data import SessionDataRepository


def first_user_prompt(
    session: Session,
    session_data_repository: SessionDataRepository,
) -> str:
    """Return the first semantic user prompt in a session.

    Returns:
        First semantic user prompt in a session.

    Raises:
        MissingSessionPromptError: If a session prompt is absent.

    """
    entries = session_data_repository.entries_of_types(
        session.session_id,
        ("message",),
    )
    for entry in entries:
        if _is_user_prompt(entry.body):
            return content_text(entry.body.content)
    raise MissingSessionPromptError


def _is_user_prompt(body: EntryBody) -> TypeGuard[MessageBody]:
    return isinstance(body, MessageBody) and body.role == "user" and body.phase == "prompt"
