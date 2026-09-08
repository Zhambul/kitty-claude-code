# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide sqlite domain dependencies."""

from domain import (
    ids as _domain_ids,
    lifecycle as lifecycle,
    messaging as messaging,
    outcomes as outcomes,
    preferences as _preference_models,
    records as _domain_records,
    references as references,
)

# Keep session and stored file models in a separate group.
# isort: split

from domain import (
    session_state as session_state,
    shells as _shell_models,
    uploads as _upload_models,
)

shell_models = _shell_models
upload_models = _upload_models
domain_ids = _domain_ids
preference_models = _preference_models
domain_records = _domain_records
