# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import unquote, urlparse

from harness.impl.codex.canonical import translator_dependencies as dependencies
from harness.impl.codex.canonical.translator_core_values import (
    CODEX_TOOLS,
    FILE_SUBJECT,
    MISSING_NATIVE_VALUE,
)
from harness.impl.codex.canonical.translator_identity import CodexToolKind
from harness.impl.codex.canonical.translator_tool_models import (
    _JS_STRING_FIELD,
    _SEARCH_QUERY_FIELDS,
    CodexToolField,
    ToolFields,
    ToolStringField,
)
from harness.impl.codex.canonical.translator_tool_paths import _node_read_path

if TYPE_CHECKING:
    import re


def codex_tool(native_name: str, arguments: str | None) -> tuple[CodexToolKind, str]:
    """Map Codex transport names onto the canonical vocabulary.

    A name with no fact behind it raises `UnknownRawEventError`: the delivery is
    verdicted `ignored_unknown` — visible in the audit, absent from the feed —
    rather than failing the whole record.

    The web-tool parser raises TranslationError for invalid web arguments.

    Returns:
        Result items.

    Raises:
        UnknownRawEventError: If no translator owns the raw event.

    """
    if native_name == "web__run":
        return _web_tool(arguments)
    if native_name == "mcp__node_repl__js":
        if _node_read_path(arguments):
            return CodexToolKind.FILE, "Read"
        return CodexToolKind.IGNORED, "NodeRepl"
    mapped = CODEX_TOOLS.get(native_name)
    if mapped is None:
        reported_name = native_name or MISSING_NATIVE_VALUE
        message = f"unmapped Codex tool: {reported_name}"
        raise dependencies.translator_service_dependencies.raw_events.UnknownRawEventError(message)
    return mapped.kind, mapped.native_name


def _web_tool(arguments: str | None) -> tuple[CodexToolKind, str]:
    fields = _tool_fields(arguments)
    if not fields:
        message = "Codex web tool arguments are not an object"
        raise dependencies.translator_service_dependencies.raw_events.TranslationError(message)
    if any(fields.has(field) for field in _SEARCH_QUERY_FIELDS):
        return CodexToolKind.SEARCH, "WebSearch"
    fetch_fields = (
        CodexToolField.OPEN,
        CodexToolField.CLICK,
        CodexToolField.FIND,
        CodexToolField.SCREENSHOT,
    )
    if any(fields.has(field) for field in fetch_fields):
        return CodexToolKind.WEB, "WebFetch"
    # A time lookup is neither a search nor a fetch.
    message = "unmapped Codex web action"
    raise dependencies.translator_service_dependencies.raw_events.UnknownRawEventError(message)


def _tool_fields(arguments: str | None) -> ToolFields:
    """Return the tool fields.

    A Codex non-shell tool call's arguments as fields.

        This is the CALL's own argument blob for a tool this codebase does not
        fully model (a web search, an image read) — deliberately read
        best-effort rather than through a declared, `extra="forbid"` shape: only
        one or two of its fields are ever consulted below, by NAME, and a vendor
        field this reads past is not drift worth failing translation over. Two
        spellings arrive: JSON text, and a JavaScript object literal with
        unquoted keys. The latter is read for its STRING fields only — which is
        every field anything below wants — rather than interpreted.

    Returns:
        Tool fields.

    """
    try:
        parsed = dependencies.record_payload_namespaces.record_tool_requests.CodexToolArguments.model_validate_json(
            arguments
            or dependencies.record_payload_namespaces.record_tool_requests.CodexToolArguments().model_dump_json(),
        )
    except dependencies.translator_service_dependencies.ValidationError:
        parsed = None
    matches = _JS_STRING_FIELD.finditer(arguments or "")
    strings = tuple(_tool_string_field(match) for match in matches)
    return ToolFields(parsed, strings, arguments or "")


def _tool_string_field(match: re.Match[str]) -> ToolStringField:
    decoded_value = match.group(2).encode().decode("unicode_escape")
    return ToolStringField(match.group(1), decoded_value)


def search_query(arguments: str | None) -> dependencies.translator_type_dependencies.content.Content:
    """Return the search query.

    What was searched for. The whole argument blob is the fallback: a query
        nobody can read is still a better raw event than an empty one.

    Returns:
        Search query.

    """
    fields = _tool_fields(arguments)
    for name in _SEARCH_QUERY_FIELDS:
        query_text = fields.string(name)
        if query_text:
            return dependencies.translator_codex_dependencies.support.content(query_text)
    return dependencies.translator_codex_dependencies.support.content(arguments)


def web_url(arguments: str | None) -> str | None:
    """Return the web URL.

    The address a fetch was for, when the call names one. Codex's `open` is
        often an index into a previous search's results rather than an address, so
        only something that reads as one counts.

    Returns:
        Web URL.

    """
    fields = _tool_fields(arguments)
    for name in CodexToolField:
        candidate_url = fields.string(name)
        if candidate_url and candidate_url.startswith(("http://", "https://")):
            return candidate_url
    return None


def tool_path(arguments: str | None) -> str:
    """Read a file path from tool arguments or a Node file-read expression.

    Returns:
        The decoded path, or an empty string if no path can be read.

    """
    fields = _tool_fields(arguments)
    for name in (CodexToolField.PATH, CodexToolField.FILE_PATH, CodexToolField.URI):
        candidate_path = fields.string(name)
        if candidate_path:
            parsed = urlparse(candidate_path)
            if parsed.scheme == FILE_SUBJECT:
                return unquote(parsed.path)
            return candidate_path
    return _node_read_path(arguments)
