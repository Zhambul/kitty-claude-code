# Copyright (c) 2026 Zhambyl Yermagambet
"""Compatibility facade for fact-table mappers."""

from repository.mapper.canonical_codec import payload as payload, payload_json as payload_json
from repository.mapper.canonical_rows import (
    canonical_event_insert_row as canonical_event_insert_row,
    row_canonical_event as row_canonical_event,
)
from repository.mapper.interpretations import (
    interpretation_event_values as interpretation_event_values,
    interpretation_record_values as interpretation_record_values,
)
from repository.mapper.raw_events import (
    raw_event as raw_event,
    raw_event_identity as raw_event_identity,
    raw_event_insert_row as raw_event_insert_row,
)
from repository.mapper.session_facts import session as session, session_insert_row as session_insert_row
from repository.mapper.shell_output import (
    shell_output_following as shell_output_following,
    shell_output_row as shell_output_row,
)
