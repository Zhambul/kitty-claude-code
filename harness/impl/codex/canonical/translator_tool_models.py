# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from enum import StrEnum

from harness.impl.codex.canonical import translator_dependencies as dependencies

_JS_STRING_FIELD_PATTERN = r"""
["']?([A-Za-z_][A-Za-z0-9_]*)["']?\s*:\s*"((?:[^"\\]|\\.)*)\"
"""

_JS_STRING_FIELD = re.compile(_JS_STRING_FIELD_PATTERN, re.VERBOSE)

_JS_REQUEST_VALUE_PATTERN = r"""
["']?(?:q|query|url|ref_id)["']?\s*:\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')
"""

_JS_REQUEST_VALUE = re.compile(_JS_REQUEST_VALUE_PATTERN, re.VERBOSE)

_NODE_READ_FILE_PATTERN = r"""
\breadFile\(\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')
"""

_NODE_READ_FILE = re.compile(_NODE_READ_FILE_PATTERN, re.VERBOSE)

_NODE_READ_TEMPLATE_EXPRESSION_PATTERN = r"""
\breadFile\(\s*["']\$\{\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')\s*\}["']
"""

_NODE_READ_TEMPLATE_EXPRESSION = re.compile(_NODE_READ_TEMPLATE_EXPRESSION_PATTERN, re.VERBOSE)

_NODE_READ_CWD_SUFFIX_PATTERN = r"""
\breadFile\(\s*nodeRepl\.cwd\s*\+\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')
"""

_NODE_READ_CWD_SUFFIX = re.compile(_NODE_READ_CWD_SUFFIX_PATTERN, re.VERBOSE)


class CodexToolField(StrEnum):
    """Represent codex tool field."""

    SEARCH_QUERY = "search_query"
    IMAGE_QUERY = "image_query"
    WEATHER = "weather"
    FINANCE = "finance"
    SPORTS = "sports"
    TIME = "time"
    QUERY = "query"
    OPEN = "open"
    CLICK = "click"
    FIND = "find"
    SCREENSHOT = "screenshot"
    URL = "url"
    PATH = "path"
    FILE_PATH = "file_path"
    URI = "uri"


@dataclass(frozen=True)
class ToolStringField:
    """Represent tool string field."""

    name: str
    content: str


@dataclass
class _ArrayScanState:
    depth: int = 0
    quote: str = ""
    escaped: bool = False

    def consume(self, character: str) -> bool:
        if self.escaped:
            self.escaped = False
            return False
        if self.quote:
            return self._consume_quoted(character)
        if character in "\"'`":
            self.quote = character
        elif character == "[":
            self.depth += 1
        elif character == "]":
            self.depth -= 1
            return self.depth == 0
        return False

    def _consume_quoted(self, character: str) -> bool:
        if character == "\\":
            self.escaped = True
        elif character == self.quote:
            self.quote = ""
        return False


@dataclass(frozen=True)
class ToolFields:
    """Represent tool fields."""

    document: dependencies.record_payload_namespaces.record_tool_requests.CodexToolArguments | None
    javascript_strings: tuple[ToolStringField, ...]
    javascript_source: str

    def requests(
        self, codex_tool_field: CodexToolField,
    ) -> list[dependencies.record_payload_namespaces.record_tool_requests.ToolRequest] | None:
        """Return the requests.

        Returns:
            Requests.

        """
        if self.document is None:
            return None
        requests_by_name: dict[
            CodexToolField,
            list[dependencies.record_payload_namespaces.record_tool_requests.ToolRequest] | None,
        ] = {
            CodexToolField.SEARCH_QUERY: self.document.search_query,
            CodexToolField.IMAGE_QUERY: self.document.image_query,
            CodexToolField.WEATHER: self.document.weather,
            CodexToolField.FINANCE: self.document.finance,
            CodexToolField.SPORTS: self.document.sports,
            CodexToolField.TIME: self.document.time,
            CodexToolField.OPEN: self.document.open,
            CodexToolField.CLICK: self.document.click,
            CodexToolField.FIND: self.document.find,
            CodexToolField.SCREENSHOT: self.document.screenshot,
        }
        return requests_by_name.get(codex_tool_field)

    def has(self, codex_tool_field: CodexToolField) -> bool:
        """Return true if has.

        Returns:
            True if has.

        """
        if self.document is not None:
            return self._document_has(codex_tool_field)
        return (
            any(field.name == codex_tool_field.value for field in self.javascript_strings)
            or re.search(
                rf"""(?:^|[{{,])\s*["']?{re.escape(codex_tool_field.value)}["']?\s*:""",
                self.javascript_source,
            )
            is not None
        )

    def string(self, codex_tool_field: CodexToolField) -> str | None:
        """Return the string.

        Returns:
            String.

        """
        name = codex_tool_field
        if self.document is not None:
            return self._document_string(name, self.document)
        direct = next(
            (field.content for field in self.javascript_strings if field.name == name.value),
            None,
        )
        if direct is not None:
            return direct
        request_array = self._javascript_array(name)
        request_value = _JS_REQUEST_VALUE.search(request_array or "")
        if request_value is None:
            return None
        try:
            return str(ast.literal_eval(request_value.group(1)))
        except (SyntaxError, ValueError):
            return None

    def _javascript_array(self, codex_tool_field: CodexToolField) -> str | None:
        """Return one named JavaScript array without evaluating JavaScript.

        Returns:
            One named JavaScript array without evaluating JavaScript.

        """
        match = re.search(
            rf"""(?:^|[{{,])\s*["']?{re.escape(codex_tool_field.value)}["']?\s*:\s*\[""",
            self.javascript_source,
        )
        if match is None:
            return None
        start = match.end() - 1
        end = self._javascript_array_end(start)
        return self.javascript_source[start:end]

    def _javascript_array_end(self, start: int) -> int | None:
        state = _ArrayScanState()
        for index, character in enumerate(
            self.javascript_source[start:],
            start=start,
        ):
            if state.consume(character):
                return index + 1
        return None

    def _document_has(self, codex_tool_field: CodexToolField) -> bool:
        document = self.document
        if document is None:
            return False
        string_fields = {
            CodexToolField.QUERY: document.query,
            CodexToolField.URL: document.url,
            CodexToolField.PATH: document.path,
            CodexToolField.FILE_PATH: document.file_path,
            CodexToolField.URI: document.uri,
        }
        missing_field = object()
        string_value = string_fields.get(codex_tool_field, missing_field)
        if string_value is not missing_field:
            return string_value is not None
        return self.requests(codex_tool_field) is not None

    def _document_string(
        self,
        codex_tool_field: CodexToolField,
        document: dependencies.record_payload_namespaces.record_tool_requests.CodexToolArguments,
    ) -> str | None:
        direct_value = {
            CodexToolField.QUERY: document.query,
            CodexToolField.URL: document.url,
            CodexToolField.PATH: document.path,
            CodexToolField.FILE_PATH: document.file_path,
            CodexToolField.URI: document.uri,
        }.get(codex_tool_field)
        if direct_value is not None:
            return direct_value
        requests = self.requests(codex_tool_field)
        if not requests:
            return None
        request = requests[0]
        candidate_values = (
            request.query,
            request.short_query,
            request.url,
            request.reference,
            request.location,
            request.ticker,
            request.utc_offset,
            request.team,
            request.fn,
        )
        return next((candidate for candidate in candidate_values if candidate), None)


_SEARCH_QUERY_FIELDS = (
    CodexToolField.SEARCH_QUERY,
    CodexToolField.IMAGE_QUERY,
    CodexToolField.WEATHER,
    CodexToolField.FINANCE,
    CodexToolField.SPORTS,
    CodexToolField.TIME,
    CodexToolField.QUERY,
)
