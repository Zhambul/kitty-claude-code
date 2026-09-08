# Copyright (c) 2026 Zhambyl Yermagambet
"""Decode provider-specific structured title documents."""

from __future__ import annotations

from pydantic import BaseModel, ValidationError

from inference.output_documents import ClaudeOutput, CodexEvent, TitleDocument


def direct_title(document_text: str) -> str | None:
    """Read a direct title document.

    Returns:
        Text result.

    """
    document = _document(TitleDocument, document_text)
    if document and document.title.strip():
        return document.title
    return None


def codex_title(document_text: str) -> str | None:
    """Read a title from one Codex event.

    Returns:
        Text result.

    """
    event = _document(CodexEvent, document_text)
    if event is None or event.event_item is None or event.event_item.text is None:
        return None
    return direct_title(event.event_item.text)


def claude_title(document_text: str) -> str | None:
    """Read a title from one Claude result.

    Returns:
        Text result.

    """
    output = _document(ClaudeOutput, document_text)
    if output is None:
        return None
    if output.structured_output and output.structured_output.title.strip():
        return output.structured_output.title
    if output.result:
        return direct_title(output.result)
    return None


def _document[Document: BaseModel](
    document_type: type[Document],
    document_text: str,
) -> Document | None:
    try:
        return document_type.model_validate_json(document_text)
    except ValidationError:
        return None
