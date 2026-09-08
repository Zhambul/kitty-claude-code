# Copyright (c) 2026 Zhambyl Yermagambet
"""Expose domain namespaces used by canonical session-data tests."""

from domain import (
    actor_state as actor_state,
    attention as attention,
    content as content,
)

# Keep read-model entries in their own group.
# isort: split

from domain import (
    entries as entries,
    entry_attention as entry_attention,
    entry_base as entry_base,
    entry_conversation as entry_conversation,
    entry_lifecycle as entry_lifecycle,
    entry_resources as entry_resources,
    entry_shells as entry_shells,
)

# Keep canonical event payloads in their own group.
# isort: split

from domain import (
    event_actor as event_actor,
    event_base as event_base,
    event_conversation as event_conversation,
    event_resource as event_resource,
    event_session as event_session,
    event_shell as event_shell,
    event_telemetry as event_telemetry,
    event_work as event_work,
)

# Keep shared identity and state vocabulary in its own group.
# isort: split

from domain import (
    ids as ids,
    messaging as messaging,
    outcomes as outcomes,
    records as records,
    references as references,
    session_state as session_state,
    usage as usage,
    work_state as work_state,
)
