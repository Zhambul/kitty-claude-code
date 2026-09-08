# Copyright (c) 2026 Zhambyl Yermagambet
"""Focused canonical naming architecture gate.

Gate 1 — a parameter is named after its class. A parameter whose annotation is
one of OUR classes must carry that class's full name in snake case, either
exactly (`session_repository: SessionRepository`) or as a suffix
(`resume_session_id: SessionId`). A shortened name (`sessions:
SessionRepository`) hides what the object is, and the reader has to open the
class to find out.

Gate 2 — an id is a typed id, never a bare `str`. A parameter or a dataclass
field whose name ends in `_id` must use a NewType from `domain/ids.py` (or a
package's own id type). A bare `str` lets any string flow into any id slot,
and the type checker cannot catch the swap.

Gate 4 (below Gate 3, the banned-words gate) — a harness's name is a typed
`HarnessName`, never a bare `str`, for the same reason as Gate 2: a parameter
or dataclass field named exactly `harness` or ending `_harness` must not be
annotated bare `str`.

Gate 5 (TASKS.md item 4b) — a closed string vocabulary is an enum, never a
bare `Literal["a", "b"]` union or a module-level `frozenset` of string
literals. Every one of OUR verdicts, roles, phases and command sets became a
`StrEnum` (`domain/outcomes.py` and related modules); what is left as a `Literal` union
or a bare-string `frozenset` in the production packages is either a vendor's
own vocabulary (a record's `type`/`kind` tag, read verbatim off foreign JSON —
`records.py` in each harness, `rollout.py`'s `KINDS`, `transcript.py`'s
`RECORD_TYPES`) or another program's own names (`terminal/launch.py`'s
`SUPPORTED_LOGIN_SHELLS`), each judged and commented in place. The allowlist
below is that judgment, one line per exception; it only ever shrinks.

Scope: the production packages. `tests/` is not swept (same ratchet stance as
mypy.ini). `api/` is exempt from Gates 2 and 4 only: the HTTP boundary carries
strings by design, and its mappers are exactly where a typed id or a typed
harness name becomes one.
"""

from __future__ import annotations

import ast
from typing import TypeGuard

VOCABULARY_GATE_ALLOWED = (
    # Codex's own rollout record `type`/`kind` tags — the same role every
    # `Literal[...]` in harness/impl/codex/canonical/records.py plays for the
    # same harness; both stay the vendor's words, not ours.
    "harness/impl/codex/canonical/rollout_parsing.py:KINDS",
    # Claude Code's own transcript record `type` tags, read verbatim off its
    # JSON — the same role the `type` Literal tags in
    # harness/impl/claude_code/canonical/records.py play for the same harness.
    "harness/impl/claude_code/canonical/transcript.py:RECORD_TYPES",
    # Other programs' own names: the login shells this launch convention
    # knows how to invoke, read from $SHELL — not a vocabulary this codebase
    # defines the meaning of.
    "terminal/launch.py:SUPPORTED_LOGIN_SHELLS",
)

# These modules now own the vendor type unions from the two former records.py
# files. Keep the exceptions limited to these reviewed record models.


VOCABULARY_GATE_EXEMPT_FILES = (
    # Claude title record types: agent-name, ai-title, and summary.
    "harness/impl/claude_code/canonical/record_attachments.py",
    # Codex empty payload types: thread_goal_cleared and context_compacted.
    "harness/impl/codex/canonical/record_goal_payloads.py",
    # Codex item types whose content comes from another native record.
    "harness/impl/codex/canonical/record_mcp_items.py",
)


def _string_literal_count(node: ast.AST) -> int:
    """Count plain string constants in a literal type slice.

    Returns:
        One for a string, the matching element count for a tuple, or zero otherwise.

    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return 1
    if isinstance(node, ast.Tuple):
        return sum(1 for element in node.elts if _string_literal_count(element) == 1)
    return 0


def _is_literal_subscript(node: ast.Subscript) -> bool:
    name = node.value
    if isinstance(name, ast.Name):
        return name.id == "Literal"
    if isinstance(name, ast.Attribute):
        return name.attr == "Literal"
    return False


def _is_frozenset_of_strings(node: ast.AST) -> bool:
    if not _is_frozenset_call(node):
        return False
    if not node.args:
        return False
    first_argument = node.args[0]
    if isinstance(first_argument, ast.Set):
        return True
    if not isinstance(first_argument, (ast.Tuple, ast.List)):
        return False
    return _are_string_constants(first_argument.elts)


def _is_frozenset_call(node: ast.AST) -> TypeGuard[ast.Call]:
    """Return true when one node constructs a frozenset.

    Returns:
        True when one node constructs a frozenset.

    """
    if not isinstance(node, ast.Call):
        return False
    if not isinstance(node.func, ast.Name):
        return False
    return node.func.id == "frozenset"


def _are_string_constants(elements: list[ast.expr]) -> bool:
    """Return true when a non-empty sequence has only string constants.

    Returns:
        True when a non-empty sequence has only string constants.

    """
    if not elements:
        return False
    for element in elements:
        if not isinstance(element, ast.Constant):
            return False
        if not isinstance(element.value, str):
            return False
    return True
