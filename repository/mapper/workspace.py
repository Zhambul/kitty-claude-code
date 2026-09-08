# Copyright (c) 2026 Zhambyl Yermagambet
"""Row DTOs to a session's unsent work.

The two JSON columns this used to encode and decode — `queued_messages` and
`dialog_answers` — are tables now, so what is left is assembly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.composer import (
    ComposerDraft,
    ComposerQueue,
    QueuedMessage,
)
from domain.dialogs import AnswerSelection, DialogDraft
from domain.ids import AttentionId, SessionId
from domain.workspace import SessionWorkspace

if TYPE_CHECKING:
    from repository.model.sql import SqlValues
    from repository.model.workspace import (
        ComposerQueueItemRow,
        DialogAnswerRow,
        DialogAnswerSelectionRow,
        SessionWorkspaceRow,
    )


def session_workspace(
    session_workspace_row: SessionWorkspaceRow,
    queue_items: tuple[ComposerQueueItemRow, ...],
    answers: tuple[DialogAnswerRow, ...],
    selections: tuple[DialogAnswerSelectionRow, ...],
) -> SessionWorkspace:
    """Return the session workspace.

    Returns:
        Session workspace.

    """
    return SessionWorkspace(
        session_id=SessionId(session_workspace_row.session_id),
        draft=_draft(session_workspace_row),
        queue=_queue(session_workspace_row, queue_items),
        dialog=_dialog(session_workspace_row, answers, selections),
    )


def _draft(session_workspace_row: SessionWorkspaceRow) -> ComposerDraft | None:
    if not session_workspace_row.composer_text.strip():
        return None
    return ComposerDraft(
        session_workspace_row.composer_text,
        session_workspace_row.composer_origin,
        session_workspace_row.composer_sequence,
    )


def _queue(
    session_workspace_row: SessionWorkspaceRow,
    queue_items: tuple[ComposerQueueItemRow, ...],
) -> ComposerQueue | None:
    messages = tuple(
        QueuedMessage(queue_row.request_id, queue_row.text)
        for queue_row in sorted(queue_items, key=lambda queue_row: queue_row.position)
    )
    return ComposerQueue(messages, session_workspace_row.queue_origin) if messages else None


def _dialog(
    session_workspace_row: SessionWorkspaceRow,
    answers: tuple[DialogAnswerRow, ...],
    selections: tuple[DialogAnswerSelectionRow, ...],
) -> DialogDraft | None:
    if session_workspace_row.dialog_attention_id is None:
        return None
    by_prompt: dict[int, list[DialogAnswerSelectionRow]] = {}
    for selection in selections:
        by_prompt.setdefault(selection.prompt_index, []).append(selection)
    selected = tuple(
        AnswerSelection(
            tuple(
                selection_row.selected_value
                for selection_row in sorted(
                    by_prompt.get(answer.prompt_index, ()),
                    key=lambda selection_row: selection_row.selection_index,
                )
            ),
            answer.other_text,
        )
        for answer in sorted(answers, key=lambda answer: answer.prompt_index)
    )
    return DialogDraft(
        AttentionId(session_workspace_row.dialog_attention_id),
        selected,
        session_workspace_row.dialog_origin,
    )


def dialog_answer_values(
    session_id: SessionId,
    dialog_draft: DialogDraft,
) -> tuple[SqlValues, ...]:
    """Return the dialog answer values.

    Returns:
        Dialog answer values.

    """
    return tuple(
        (str(session_id), prompt_index, answer.other) for prompt_index, answer in enumerate(dialog_draft.answers)
    )


def dialog_selection_values(
    session_id: SessionId,
    dialog_draft: DialogDraft,
) -> tuple[SqlValues, ...]:
    """Return the dialog selection values.

    Returns:
        Dialog selection values.

    """
    return tuple(
        (str(session_id), prompt_index, selection_index, selected_option)
        for prompt_index, answer in enumerate(dialog_draft.answers)
        for selection_index, selected_option in enumerate(answer.selected)
    )
