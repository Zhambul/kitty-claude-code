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

from tests.canonical_naming_banned_scan import _banned_identifier_violations, _banned_word_violations
from tests.canonical_naming_banned_values import _banned_word_files


def test_no_banned_word_appears_in_code_comments() -> None:
    """Verify no banned word appears in code comments or file names."""
    violations = [violation for path in _banned_word_files() for violation in _banned_word_violations(path)]
    assert not violations


def test_no_banned_identifier_appears_anywhere() -> None:
    """Case-sensitive, unlike Gate 3: these are exact class names, not prose."""
    violations = [violation for path in _banned_word_files() for violation in _banned_identifier_violations(path)]
    assert not violations


# --- Gate 5: enums, not string vocabularies -----------------------------------
#
# TASKS.md item 4b. Every judgment below is a vendor's own vocabulary (a
# record's `type`/`kind` tag, read verbatim off foreign JSON) or another
# program's own names — never a verdict, role, phase or command WE hand out.
# Grow-only: an entry may only be removed once the frozenset or Literal it
# names is converted to a `StrEnum`.
