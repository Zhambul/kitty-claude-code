# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the attachment reference module."""

# One staged attachment riding a launch or a send-text gesture.
from pydantic import BaseModel

from api.common.models.fields import RequiredText
from harness.models.controls import (
    AttachmentReference,
)


class AttachmentReferenceBody(BaseModel):
    """Represent attachment reference body."""

    local_path: RequiredText
    display_name: RequiredText
    media_type: str | None = None

    def reference(self) -> AttachmentReference:
        """Return the reference.

        Returns:
            Reference.

        """
        return AttachmentReference(self.local_path, self.display_name, self.media_type)


def references(attachments: tuple[AttachmentReferenceBody, ...]) -> tuple[AttachmentReference, ...]:
    """Return the references.

    Returns:
        References.

    """
    return tuple(attachment.reference() for attachment in attachments)
