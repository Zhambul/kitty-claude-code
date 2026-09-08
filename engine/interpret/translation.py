# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate raw events and update translation-input state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from audit.failures import FailureContext
from domain import event_session, records
from engine.interpret import consistency
from harness.models.raw_events import TranslationResult

if TYPE_CHECKING:
    from collections.abc import Callable

    from engine.interpret.dependencies import InterpreterDependencies
    from engine.interpret.snapshots import TerminalSnapshotCache
    from harness.contract import CoreTranslator, HarnessPlugin
    from harness.models.raw_events import RawEvent

TRANSLATION_BATCH_SIZE = 500


class TranslationPhase:
    """Translate unverdicted raw events and apply input reactions."""

    def __init__(
        self,
        interpreter_dependencies: InterpreterDependencies,
        terminal_snapshot_cache: TerminalSnapshotCache,
        audit_failure: Callable[[str, FailureContext], None],
    ) -> None:
        """Initialize the translation phase."""
        self.dependencies = interpreter_dependencies
        self.terminal_snapshots = terminal_snapshot_cache
        self.audit_failure = audit_failure

    def translate(self) -> int:
        """Translate one batch of raw events.

        Returns:
            The number of processed events.

        """
        raw_events = self.dependencies.repositories.raw_events
        batch = raw_events.unverdicted(TRANSLATION_BATCH_SIZE)
        for raw_event in batch:
            self._translate_one(raw_event)
        return len(batch)

    def _translate_one(self, raw_event: RawEvent) -> None:
        plugin = self.dependencies.services.harnesses.plugin(raw_event.harness)
        translator = self.dependencies.services.core_translators.get(
            raw_event.source_type,
            plugin.translator,
        )
        translation = _translate_safely(translator, raw_event)
        outcome = self.dependencies.repositories.canonical_events.record_translation(
            raw_event,
            plugin.harness_info.plugin_version,
            translation,
            self.dependencies.runtime.clock(),
        )
        self._react_to(outcome)
        self._release_finished(plugin, raw_event, outcome)

    def _react_to(self, outcome: records.TranslationOutcome) -> None:
        if any(
            isinstance(canonical_event.payload, event_session.SessionStarted) for canonical_event in outcome.accepted
        ):
            self.terminal_snapshots.invalidate()
        for reaction in self.dependencies.services.inputs:
            for canonical_event in outcome.accepted:
                try:
                    reaction.react(canonical_event)
                except Exception:  # noqa: BLE001 - Record each failed reaction and let other reactions run.
                    self.audit_failure(
                        type(reaction).__name__,
                        FailureContext(
                            session_id=canonical_event.session_id,
                            event_id=canonical_event.event_id,
                        ),
                    )

    def _release_finished(
        self,
        harness_plugin: HarnessPlugin,
        raw_event: RawEvent,
        outcome: records.TranslationOutcome,
    ) -> None:
        has_finished = any(
            isinstance(canonical_event.payload, event_session.SessionFinished) for canonical_event in outcome.accepted
        )
        if not has_finished:
            return
        for name, release in (
            ("translation", harness_plugin.translator.release_session),
            ("source", harness_plugin.sources.release_session),
        ):
            try:
                release(raw_event.session_id)
            except Exception:  # noqa: BLE001 - Record plugin cleanup failure and continue other cleanup.
                self.audit_failure(
                    f"{name} memory release",
                    FailureContext(session_id=raw_event.session_id),
                )


def _translate_safely(
    core_translator: CoreTranslator,
    raw_event: RawEvent,
) -> TranslationResult:
    try:
        translation = core_translator.translate(raw_event)
    except Exception as error:  # noqa: BLE001 - Store plugin failure as a translation decision.
        translation = TranslationResult(
            (),
            records.RecordedTranslationDecision.TRANSLATION_FAILED,
            f"{type(error).__name__}: {error}",
        )
    else:
        translation = consistency.checked(raw_event, translation)
    return translation
