# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical text and structured content values."""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from domain.stored import STORED


class MediaType(StrEnum):
    """Identify how a client must render text content."""

    TEXT_PLAIN = "text/plain"
    TEXT_MARKDOWN = "text/markdown"


@dataclass(frozen=True)
class TextContent:
    """Hold text and the media type that defines its rendering."""

    __pydantic_config__ = STORED

    text: str
    media_type: MediaType = MediaType.TEXT_PLAIN


@dataclass(frozen=True)
class StructuredContent:
    """Hold a canonical JSON document that belongs to an external tool."""

    __pydantic_config__ = STORED

    json_text: str

    def __post_init__(self) -> None:
        """Canonicalize the external JSON document."""
        document = json.loads(self.json_text)
        canonical_json = json.dumps(
            document,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        object.__setattr__(self, "json_text", canonical_json)

    def field(self, name: str) -> str | None:
        """Return one top-level string field when it exists.

        Returns:
            One top-level string field when it exists.

        """
        document = json.loads(self.json_text)
        if isinstance(document, Mapping) and isinstance(document.get(name), str):
            field_text: str = document[name]
            return field_text
        return None

    def readable(self) -> str:
        """Return the external document in a human-readable layout.

        Returns:
            External document in a human-readable layout.

        """
        return json.dumps(
            json.loads(self.json_text),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )


type Content = TextContent | StructuredContent


def content_text(content: Content | None) -> str:
    """Return canonical content as plain text.

    Returns:
        Canonical content as plain text.

    """
    if content is None:
        return ""
    if isinstance(content, TextContent):
        return content.text
    return content.readable()
