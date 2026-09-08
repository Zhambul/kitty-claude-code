# Copyright (c) 2026 Zhambyl Yermagambet
"""Run one terminal action without loss of the user's draft."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

    from domain.ids import WindowId
    from harness.contract import ComposerDriver, HarnessComposer

Result = TypeVar("Result")


class ComposerRestoreError(Exception):
    """The terminal action ran, but its saved draft could not be restored."""


def _restore_after_action_error(
    harness_composer: HarnessComposer,
    composer_driver: ComposerDriver,
    window_id: WindowId,
    draft: str,
    action_error: BaseException,
) -> None:
    try:
        harness_composer.insert(composer_driver, window_id, draft)
    except Exception as restore_error:  # noqa: BLE001 -- Keep the original action error as the cause if restoration fails.
        message = f"the terminal action failed and the draft was not restored: {restore_error}"
        raise ComposerRestoreError(message) from action_error


def with_preserved_draft[Result](
    harness_composer: HarnessComposer,
    composer_driver: ComposerDriver,
    window_id: WindowId,
    action: Callable[[], Result],
) -> Result:
    """Clear the composer, run `action`, and restore the exact visible draft.

    Returns:
        The result.

    Raises:
        ComposerRestoreError: If the terminal draft cannot be restored.

    """
    state = harness_composer.read(composer_driver, window_id)
    if state is None:
        message = "the terminal composer is not readable"
        raise ComposerRestoreError(message)
    draft = state.typed_text or ""
    harness_composer.clear(composer_driver, window_id)
    try:
        result = action()
    except BaseException as action_error:
        _restore_after_action_error(
            harness_composer,
            composer_driver,
            window_id,
            draft,
            action_error,
        )
        raise
    try:
        harness_composer.insert(composer_driver, window_id, draft)
    except Exception as restore_error:
        message = f"the terminal draft was not restored: {restore_error}"
        raise ComposerRestoreError(
            message,
        ) from restore_error
    return result
