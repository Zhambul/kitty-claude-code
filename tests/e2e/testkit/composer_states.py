# Copyright (c) 2026 Zhambyl Yermagambet
"""Check composer state from fresh application reads."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sdk.client import BaqylauClient, SessionRef


def draft_is_saved(client: BaqylauClient, session: SessionRef, text: str) -> bool | None:
    """Return true when a composer draft has the required text.

    Returns:
        True for the required draft, else None.

    """
    draft = client.preferences.session_state(session).composer.draft
    return True if draft is not None and draft.text == text else None


def draft_is_cleared(client: BaqylauClient, session: SessionRef) -> bool | None:
    """Return true when a composer draft is absent.

    Returns:
        True when the draft is absent, else None.

    """
    return True if client.preferences.session_state(session).composer.draft is None else None


def queue_has_text(client: BaqylauClient, session: SessionRef, text: str) -> bool | None:
    """Return true when the composer queue has one required message.

    Returns:
        True for the required queue message, else None.

    """
    queue = client.preferences.session_state(session).composer.queue
    if queue is None:
        return None
    return True if [message.text for message in queue.messages] == [text] else None
