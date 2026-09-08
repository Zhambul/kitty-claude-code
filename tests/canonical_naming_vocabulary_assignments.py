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
from tests.canonical_naming_vocabulary_paths import ModuleAssignment
from tests.canonical_naming_vocabulary_values import VOCABULARY_GATE_ALLOWED, _is_frozenset_of_strings

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Iterator


def _module_frozenset_violations(path: pathlib.Path) -> Iterator[str]:
    relative_path = path.relative_to(ROOT).as_posix()
    for assignment in _module_assignments(path, relative_path):
        if assignment.expression is None or not _is_frozenset_of_strings(assignment.expression):
            continue
        yield from _frozenset_target_violations(relative_path, assignment.line_number, assignment.targets)


def _module_assignments(path: pathlib.Path, relative_path: str) -> Iterator[ModuleAssignment]:
    """Read module-level assignments from a source file.

    Yields:
        The targets, expression, and line number for each assignment.

    """
    tree = ast.parse(path.read_text(encoding=TEXT_ENCODING), filename=relative_path)
    for statement in tree.body:
        assignment = _module_assignment(statement)
        if assignment is not None:
            yield assignment


def _module_assignment(statement: ast.stmt) -> ModuleAssignment | None:
    """Return targets and value from one module assignment.

    Returns:
        Targets and value from one module assignment.

    """
    if isinstance(statement, ast.Assign):
        return ModuleAssignment(tuple(statement.targets), statement.value, statement.lineno)
    if isinstance(statement, ast.AnnAssign):
        return ModuleAssignment((statement.target,), statement.value, statement.lineno)
    return None


def _frozenset_target_violations(
    relative_path: str,
    line_number: int,
    targets: tuple[ast.expr, ...],
) -> Iterator[str]:
    """Check names assigned to a string frozenset.

    Yields:
        Each unapproved target with its file path and line number.

    """
    for target in targets:
        if not isinstance(target, ast.Name):
            continue
        allowed_key = f"{relative_path}:{target.id}"
        if allowed_key not in VOCABULARY_GATE_ALLOWED:
            yield f"{relative_path}:{line_number}: frozenset({target.id!r}) of string literals"
