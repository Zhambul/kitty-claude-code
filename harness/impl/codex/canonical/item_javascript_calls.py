# Copyright (c) 2026 Zhambyl Yermagambet
"""Item javascript calls."""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from harness.impl.codex.canonical import item_patterns

if TYPE_CHECKING:
    import re


def _following_character(source_text: str, position: int) -> str:
    next_position = position + 1
    return source_text[next_position] if next_position < len(source_text) else ""


class _JavaScriptMasker:
    def __init__(self, source_text: str) -> None:
        self._source_text = source_text
        self._position = 0
        self._quote = ""
        self._escaped = False
        self._line_comment = False
        self._block_comment = False
        self._masked_characters: list[str] = []

    def mask(self) -> str:
        while self._position < len(self._source_text):
            if self._line_comment:
                self._consume_line_comment()
            elif self._block_comment:
                self._consume_block_comment()
            elif self._quote:
                self._consume_quoted_character()
            else:
                self._consume_code_character()
        return "".join(self._masked_characters)

    def _consume_code_character(self) -> None:
        character = self._source_text[self._position]
        following = _following_character(self._source_text, self._position)
        if character in item_patterns.JAVASCRIPT_QUOTES:
            self._quote = character
            self._masked_characters.append(" ")
            self._position += 1
        elif character == "/" and following == "/":
            self._line_comment = True
            self._masked_characters.extend((" ", " "))
            self._position += 2
        elif character == "/" and following == "*":
            self._block_comment = True
            self._masked_characters.extend((" ", " "))
            self._position += 2
        else:
            self._masked_characters.append(character)
            self._position += 1

    def _consume_quoted_character(self) -> None:
        character = self._source_text[self._position]
        self._masked_characters.append(" ")
        self._position += 1
        if self._escaped:
            self._escaped = False
        elif character == "\\":
            self._escaped = True
        elif character == self._quote:
            self._quote = ""

    def _consume_line_comment(self) -> None:
        character = self._source_text[self._position]
        if character in "\r\n":
            self._line_comment = False
            self._masked_characters.append(character)
        else:
            self._masked_characters.append(" ")
        self._position += 1

    def _consume_block_comment(self) -> None:
        following = _following_character(self._source_text, self._position)
        if self._source_text[self._position] == "*" and following == "/":
            self._block_comment = False
            self._masked_characters.extend((" ", " "))
            self._position += 2
        else:
            self._masked_characters.append(" ")
            self._position += 1


class JavaScriptToolCall(NamedTuple):
    """Represent java script tool call."""

    name: str
    arguments: str


def _closing_parenthesis(masked_source: str, start_position: int) -> int | None:
    depth = 1
    for position, character in enumerate(
        masked_source[start_position:],
        start=start_position,
    ):
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return position
    return None


def _javascript_tool_call(
    source_text: str,
    masked_source: str,
    match: re.Match[str],
) -> tuple[JavaScriptToolCall, int]:
    closing_position = _closing_parenthesis(masked_source, match.end())
    argument_end = len(source_text) if closing_position is None else closing_position
    arguments = source_text[match.end() : argument_end].strip()
    next_position = argument_end if closing_position is None else argument_end + 1
    return JavaScriptToolCall(match.group(1), arguments), next_position


def _collect_javascript_tool_calls(
    source_text: str,
    masked_source: str,
) -> tuple[JavaScriptToolCall, ...]:
    calls: list[JavaScriptToolCall] = []
    cursor = 0
    while match := item_patterns.JAVASCRIPT_TOOL_PATTERN.search(masked_source, cursor):
        tool_call, cursor = _javascript_tool_call(
            source_text,
            masked_source,
            match,
        )
        calls.append(tool_call)
    return tuple(calls)


def js_tool_calls(js: str) -> tuple[JavaScriptToolCall, ...]:
    r"""All top-level `tools.<fn>(…)` calls in JavaScript execution order.

    codex ≥ 0.146 runs MANY tools through the SAME `exec` custom tool: a shell
    command is `tools.exec_command({cmd:…})` (handled by _exec_cmd_from_js
    below), but a web/MCP lookup is
    `const r = await tools.web__run({…}); text(JSON.stringify(r))`. The NAME is
    the function (`web__run`) and the ARGS are what it was called with, so a
    presenter can paint the same quiet `· <name>` block every other tool call in
    this repo gets, with the arguments behind the click.

    The args end at the call's MATCHING close paren, found by a depth count that
    skips quoted text. A fixed suffix list ("; text(r)", …) was the previous
    approach and matched NONE of the five real calls in the measured child
    rollout — the wrapper's tail varies per call (`text(JSON.stringify(r))`,
    `text(r.content.map(x=>x.text||"").join("\\\\n"))`), so the whole `; text(…)`
    tail was landing in the rendered command. An unbalanced (truncated) input
    falls open to the rest of the string rather than raising.

    Returns:
        Result items.

    """
    source_text = js or ""
    masked_source = _JavaScriptMasker(source_text).mask()
    return _collect_javascript_tool_calls(source_text, masked_source)
