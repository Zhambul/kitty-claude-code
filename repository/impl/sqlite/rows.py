# Copyright (c) 2026 Zhambyl Yermagambet
"""SQLite row adapters, grouped by the table family they map."""

from repository.impl.sqlite.rows_audit import (
    error as error,
    spawn as spawn,
    state_file as state_file,
)
from repository.impl.sqlite.rows_events import (
    canonical_event as canonical_event,
    raw_event as raw_event,
    session_data as session_data,
    session_data_actor as session_data_actor,
    session_entry as session_entry,
    shell_output as shell_output,
)
from repository.impl.sqlite.rows_preferences import (
    hidden_directory as hidden_directory,
    new_session_draft as new_session_draft,
    new_session_preference as new_session_preference,
    push_signing_key as push_signing_key,
    push_subscription as push_subscription,
    session_view_mode as session_view_mode,
)
from repository.impl.sqlite.rows_session import session as session
from repository.impl.sqlite.rows_uploads import upload as upload
from repository.impl.sqlite.rows_workspace import (
    composer_queue_item as composer_queue_item,
    dialog_answer as dialog_answer,
    dialog_answer_selection as dialog_answer_selection,
    session_workspace as session_workspace,
)
