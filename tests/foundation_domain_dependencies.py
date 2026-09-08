# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide domain dependencies."""

from domain import (
    content as _domain_content,
    event_actor as event_actor,
    event_base as event_base,
    event_conversation as event_conversation,
    event_session as event_session,
    event_shell as event_shell,
    events as _domain_events,
)

# Keep event payloads separate from identity and state vocabulary.
# isort: split

from domain import (
    ids as _domain_ids,
    messaging as messaging,
    outcomes as outcomes,
    records as _domain_records,
    work_state as work_state,
)

domain_content = _domain_content
domain_events = _domain_events
domain_ids = _domain_ids
domain_records = _domain_records
