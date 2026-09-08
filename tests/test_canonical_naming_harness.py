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

from tests.canonical_naming_bare_support_one import BareStringGate
from tests.canonical_naming_bare_support_two import _bare_string_violations
from tests.canonical_naming_paths import ID_GATE_PACKAGES, _module_paths

HARNESS_GATE_PACKAGES = ID_GATE_PACKAGES

# A parameter or field that holds a harness name but truly cannot be typed.
# Each line is a deliberate, justified exception; this list only ever shrinks.
HARNESS_GATE_ALLOWED: tuple[str, ...] = ()


def _is_harness_named(name: str) -> bool:
    return name == "harness" or name.endswith("_harness")


HARNESS_BARE_STRING_GATE = BareStringGate(
    HARNESS_GATE_PACKAGES,
    HARNESS_GATE_ALLOWED,
    _is_harness_named,
    "use HarnessName from domain/ids.py",
)


def test_harness_name_is_typed_harness_name_not() -> None:
    """Verify a harness name is a typed harness name not a bare str."""
    violations = [
        violation for path in _module_paths() for violation in _bare_string_violations(path, HARNESS_BARE_STRING_GATE)
    ]
    assert not violations


# --- Gate 3: banned words -----------------------------------------------------
#
# A vocabulary the owner has retired, because each word named a thing this tree
# no longer has (a hand-written codec, an "envelope" that is a plain stored
# event, a "wire" that is the HTTP boundary) or was too vague to keep (a
# "wiring" or a "provenance" that always meant something more specific the
# sentence should say instead — a dependency graph, a set of raw event ids,
# whatever the concrete thing actually is). There is no fixed one-word
# replacement for these two: say the plain thing, in place. Grow-only: a word
# retired here may never come back off the list, only new words may join it.
