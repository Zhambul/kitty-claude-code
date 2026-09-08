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

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEXT_ENCODING = "utf-8"

PACKAGES = (
    "api",
    "app",
    "audit",
    "core",
    "dashboard",
    "domain",
    "engine",
    "harness",
    "notify",
    "repository",
    "terminal",
)

# Gate 2 does not apply to api/: the wire carries strings, and the api mappers
# are the one sanctioned place where a typed id is turned into one.
ID_GATE_PACKAGES = tuple(package for package in PACKAGES if package != "api")

# Parameters that hold an id of NO fixed kind. Each line is a deliberate,
# justified exception; this list only ever shrinks.
ID_GATE_ALLOWED = (
    # These are opaque native source positions, not canonical event identifiers.
    "harness/impl/claude_code/hooks/observation.py:native_event_id",
    "harness/impl/claude_code/hooks/observation.py:observation_id",
    "harness/impl/codex/hooks/gateway.py:event_id",
    # stable_event_id builds identity from whatever subject an event has —
    # a shell id, a call id, a path. There is no one kind to name.
    "domain/ids.py:subject_id",
    # UsageReported.scope says which id `subject_id` is (session, actor, turn
    # or operation) — the same "no one fixed kind" shape as stable_event_id's
    # own subject_id above, and for the same reason.
    "domain/event_telemetry.py:subject_id",
    "harness/impl/claude_code/canonical/support.py:subject_id",
    "harness/impl/claude_code/canonical/message_launch.py:subject_id",
    "harness/impl/codex/canonical/support.py:subject_id",
    "harness/models/raw_event_builders.py:subject_id",
    # codex's OWN compaction-window id, distinct from domain WindowId (a
    # TERMINAL window) — a naming collision, not the same concept. Unread by
    # any canonical logic (rollout.py module header): carried for a future
    # reader, not worth a NewType for a field nothing consumes yet.
    "harness/impl/codex/canonical/record_interaction_records.py:window_id",
    "harness/impl/codex/canonical/record_session_sources.py:window_id",
    "harness/impl/codex/canonical/record_turn_payloads.py:window_id",
    "harness/impl/codex/canonical/record_interaction_records.py:previous_window_id",
    "harness/impl/codex/canonical/record_turn_payloads.py:previous_window_id",
    "harness/impl/codex/canonical/record_turn_payloads.py:first_window_id",
    # A hook delivery's own id (SessionStart/PreCompact/PostCompact) — used
    # only as a last-resort native_identity fallback string, the same role
    # raw_event.source_position plays; not a domain concept.
    "harness/impl/codex/canonical/record_session_meta.py:hook_event_id",
    # The codex CommandExecution item's own id — declared (it is a real
    # field) but never read by any canonical logic, the same as the original
    # dict literal carried it unread. Not worth a NewType for a value with no
    # reader.
    "harness/impl/codex/canonical/record_rollout_headers.py:item_id",
    "harness/impl/codex/canonical/record_tool_records.py:item_id",
    # codex's own account plan-limit identifier (measured: "codex") — unread,
    # opaque, no domain equivalent.
    "harness/impl/codex/canonical/record_usage_payloads.py:limit_id",
    # The model provider's own name ("openai") — a vendor label, not an id
    # this codebase has a NewType for.
    "harness/impl/codex/canonical/record_task_payloads.py:model_provider_id",
    # The client UI's own opaque session id on a `user_message` — unread by
    # any canonical logic.
    "harness/impl/codex/canonical/record_event_messages.py:client_id",
    # A Claude Code hook delivery's own id (SessionStart/PreCompact/…) — the
    # same role codex's own hook_event_id plays above: used only as a
    # last-resort native_identity fallback string, not a domain concept.
    "harness/impl/claude_code/canonical/record_tool_response.py:hook_event_id",
    # Declared (a real, corpus-observed hook field) but read by nothing here —
    # the same "not worth a NewType" shape as codex's item_id/limit_id above.
    "harness/impl/claude_code/canonical/record_tool_response.py:prompt_id",
    # Telegram's OWN chat identifier (the Bot API's `chat_id`, an int OR a
    # string `@channelusername`) — a vendor concept with no domain
    # equivalent, the same shape as codex's client_id/model_provider_id
    # above.
    "notify/channels/telegram_models.py:chat_id",
)


def _module_paths() -> list[pathlib.Path]:
    return _package_paths(PACKAGES)


def _package_paths(packages: tuple[str, ...]) -> list[pathlib.Path]:
    """Return Python files from packages, without cache files.

    Returns:
        Python files from packages, without cache files.

    """
    paths: list[pathlib.Path] = []
    for package in packages:
        paths.extend(
            path for path in sorted((ROOT / package).rglob("*.py"))
            if "__pycache__" not in path.parts
        )
    return paths
