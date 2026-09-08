# Copyright (c) 2026 Zhambyl Yermagambet
"""Format Claude Code prompts that contain file mentions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.models.controls import (
        AttachmentReference,
    )


def _attachment_prompt(attachment_reference: AttachmentReference) -> str:
    if (attachment_reference.media_type or "").startswith("image/"):
        return f'Image attachment "{attachment_reference.display_name}": {attachment_reference.local_path}'
    return f"@{attachment_reference.local_path}"


def prompt_with_attachments(
    text: str,
    attachments: tuple[AttachmentReference, ...],
) -> str:
    """Keep prompt text visible while Claude Code accepts attachment mentions.

    Returns:
        Text result.

    """
    mentions = " ".join(_attachment_prompt(attachment) for attachment in attachments)
    if not text:
        return mentions
    if mentions:
        return f"{text} {mentions}"
    return text


def control_prompt_with_attachments(
    text: str,
    attachments: tuple[AttachmentReference, ...],
) -> str:
    """Put paths before text so the native prompt keeps an exact text suffix.

    Returns:
        Text result.

    """
    attachment_text = " ".join(_attachment_prompt(attachment) for attachment in attachments)
    if not text:
        return attachment_text
    if attachment_text:
        return f"{attachment_text}\n{text}"
    return text
