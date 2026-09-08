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

from tests.canonical_naming_bare_support_one import (
    BareStringGate,
    _annotated_fields,
    _is_gate_violation,
)
from tests.canonical_naming_parameter_iteration import annotated_parameters
from tests.canonical_naming_paths import ID_GATE_ALLOWED, ID_GATE_PACKAGES, ROOT, TEXT_ENCODING

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Iterator


def _parameter_gate_violations(
    tree: ast.AST,
    relative_path: str,
    bare_string_gate: BareStringGate,
) -> Iterator[str]:
    """Check parameters against one bare-string rule.

    Yields:
        Each violation with its location, parameter name, and required type.

    """
    for function_node, argument in annotated_parameters(tree):
        if _is_gate_violation(argument.arg, argument.annotation, relative_path, bare_string_gate):
            yield (
                f"{relative_path}:{function_node.lineno} "
                f"{function_node.name}({argument.arg}: str) — {bare_string_gate.replacement}"
            )


def _field_gate_violations(
    tree: ast.AST,
    relative_path: str,
    bare_string_gate: BareStringGate,
) -> Iterator[str]:
    """Check class fields against one bare-string rule.

    Yields:
        Each violation with its location, field name, and required type.

    """
    for class_node, statement, field_name in _annotated_fields(tree):
        if _is_gate_violation(field_name, statement.annotation, relative_path, bare_string_gate):
            yield (
                f"{relative_path}:{statement.lineno} "
                f"{class_node.name}.{field_name}: str — {bare_string_gate.replacement}"
            )


def _bare_string_violations(path: pathlib.Path, bare_string_gate: BareStringGate) -> Iterator[str]:
    """Check a module against one bare-string rule.

    Yields:
        Parameter and field violations for packages covered by the rule.

    """
    relative_path = str(path.relative_to(ROOT))
    if path.relative_to(ROOT).parts[0] not in bare_string_gate.packages:
        return
    tree = ast.parse(path.read_text(encoding=TEXT_ENCODING))
    yield from _parameter_gate_violations(tree, relative_path, bare_string_gate)
    yield from _field_gate_violations(tree, relative_path, bare_string_gate)


def _is_id_named(name: str) -> bool:
    """Return true when a name identifies an identifier value.

    Returns:
        True when a name identifies an identifier value.

    """
    return name.endswith("_id")


ID_BARE_STRING_GATE = BareStringGate(
    ID_GATE_PACKAGES,
    ID_GATE_ALLOWED,
    _is_id_named,
    "use a NewType from domain/ids.py",
)
