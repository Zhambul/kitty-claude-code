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
from typing import TYPE_CHECKING

from tests.canonical_naming_paths import ROOT, TEXT_ENCODING
from tests.canonical_naming_vocabulary_assignments import _module_frozenset_violations
from tests.canonical_naming_vocabulary_paths import _vocabulary_files
from tests.canonical_naming_vocabulary_values import _is_literal_subscript, _string_literal_count

if TYPE_CHECKING:
    import pathlib

MINIMUM_UNION_MEMBERS = 2


def test_no_new_literal_string_union_outside() -> None:
    """Verify no new literal string union outside vendor record shapes.

    Gate 5, the `Literal[...]` half: two or more plain strings in one
        `Literal` is a closed vocabulary, and OURS are enums now.
    """
    violations = [violation for path in _vocabulary_files() for violation in _literal_union_violations(path)]
    assert not violations


def _literal_union_violations(path: pathlib.Path) -> list[str]:
    """Return literal-string union violations from one file.

    Returns:
        Literal-string union violations from one file.

    """
    relative_path = path.relative_to(ROOT).as_posix()
    tree = ast.parse(path.read_text(encoding=TEXT_ENCODING), filename=relative_path)
    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        if not _is_literal_subscript(node):
            continue
        if _string_literal_count(node.slice) >= MINIMUM_UNION_MEMBERS:
            violations.append(f"{relative_path}:{node.lineno}: Literal union of plain strings")
    return violations


def test_no_module_level_frozenset_of_strings() -> None:
    """Verify no module level frozenset of strings outside the judged allowlist.

    Gate 5, the `frozenset` half: a module-level closed set of string
        literals is a vocabulary too, judged the same way as a `Literal` union.
    """
    violations = [violation for path in _vocabulary_files() for violation in _module_frozenset_violations(path)]
    assert not violations
