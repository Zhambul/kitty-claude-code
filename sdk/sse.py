# Copyright (c) 2026 Zhambyl Yermagambet
"""Small typed parser for server-sent event envelopes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


@dataclass(frozen=True)
class SseEvent:
    """Represent SSE event."""

    event: str
    event_id: str | None
    payload: str


@dataclass
class SseBuffer:
    """Collect one SSE event from input lines."""

    event_name: str = "message"
    event_id: str | None = None
    payload_lines: tuple[str, ...] = ()
    has_fields: bool = False

    def clear(self) -> None:
        """Clear the current event."""
        self.event_name = "message"
        self.event_id = None
        self.payload_lines = ()
        self.has_fields = False

    def append(self, line: str) -> None:
        """Append one SSE field line."""
        if line.startswith(":"):
            return
        field_name, separator, field_content = line.partition(":")
        if not separator:
            field_content = ""
        elif field_content.startswith(" "):
            field_content = field_content[1:]
        if field_name == "event":
            self.event_name = field_content
        elif field_name == "id":
            self.event_id = field_content
        elif field_name == "data":
            self.payload_lines = (*self.payload_lines, field_content)
        else:
            return
        self.has_fields = True

    def event(self) -> SseEvent:
        """Build the current event.

        Returns:
            The current SSE event.

        """
        return SseEvent(
            event=self.event_name,
            event_id=self.event_id,
            payload="\n".join(self.payload_lines),
        )


def events(lines: Iterable[str]) -> Iterator[SseEvent]:
    """Return the events.

    Yields:
        Parsed SSE events.

    """
    event_buffer = SseBuffer()
    for line in lines:
        if not line:
            if event_buffer.has_fields:
                yield event_buffer.event()
            event_buffer.clear()
            continue
        event_buffer.append(line)
    if event_buffer.has_fields:
        yield event_buffer.event()
