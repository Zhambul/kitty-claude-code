# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide http runtime dependencies."""

from domain import (
    content as _domain_content,
    entries as _domain_entries,
    event_base as event_base,
    event_conversation as event_conversation,
    event_session as event_session,
    ids as _domain_ids,
    messaging as messaging,
    records as _domain_records,
)
from harness.models import controls as _control_models, raw_events as _raw_event_models

domain_content = _domain_content
domain_entries = _domain_entries
domain_ids = _domain_ids
domain_records = _domain_records
control_models = _control_models
raw_event_models = _raw_event_models
