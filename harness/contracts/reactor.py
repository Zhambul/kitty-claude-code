# Copyright (c) 2026 Zhambyl Yermagambet
"""Define canonical-event reactor contracts."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from domain.ids import HarnessName
    from harness.models import controls as control_models


class _HarnessReactorLifecycleContext(typing.Protocol):
    """Provide text and session lifecycle controls to a reactor."""

    def send_text(self, send_text: control_models.SendText) -> control_models.ControlOutcome:
        """Send text."""
        ...

    def interrupt(self, interrupt: control_models.Interrupt) -> control_models.ControlOutcome:
        """Interrupt a session."""
        ...

    def background(self, background: control_models.Background) -> control_models.ControlOutcome:
        """Move a session to the background."""
        ...

    def close_session(self, close_session: control_models.CloseSession) -> control_models.ControlOutcome:
        """Close a session."""
        ...

    def rename_session(self, rename_session: control_models.RenameSession) -> control_models.ControlOutcome:
        """Rename a session."""
        ...

    def auto_name_session(
        self,
        auto_name_session: control_models.AutoNameSession,
    ) -> control_models.ControlOutcome:
        """Name a session automatically."""
        ...

    def open_rewind(self, open_rewind: control_models.OpenRewind) -> control_models.ControlOutcome:
        """Open rewind choices."""
        ...


class _HarnessReactorSelectionContext(typing.Protocol):
    """Provide rewind, model, effort, question, and plan controls."""

    def apply_rewind(self, apply_rewind: control_models.ApplyRewind) -> control_models.ControlOutcome:
        """Apply a rewind choice."""
        ...

    def compact(self, compact: control_models.Compact) -> control_models.ControlOutcome:
        """Compact a session."""
        ...

    def select_model(self, select_model: control_models.SelectModel) -> control_models.ControlOutcome:
        """Select a model."""
        ...

    def select_effort(self, select_effort: control_models.SelectEffort) -> control_models.ControlOutcome:
        """Select an effort level."""
        ...

    def answer_question(
        self,
        answer_question: control_models.AnswerQuestion,
    ) -> control_models.ControlOutcome:
        """Answer a question."""
        ...

    def read_plan_choices(
        self,
        read_plan_choices: control_models.ReadPlanChoices,
    ) -> control_models.ControlOutcome:
        """Read plan choices."""
        ...

    def decide_plan(self, decide_plan: control_models.DecidePlan) -> control_models.ControlOutcome:
        """Select a plan choice."""
        ...


class HarnessReactorContext(
    _HarnessReactorLifecycleContext,
    _HarnessReactorSelectionContext,
    typing.Protocol,
):
    """Provide all named harness controls to a reactor."""


class HarnessCanonicalEventReactor(typing.Protocol):
    """React to canonical events for one harness."""

    def react(
        self,
        canonical_event: CanonicalEvent[EventPayload],
        harness_reactor_context: HarnessReactorContext,
    ) -> None:
        """React to one canonical event."""
        ...


class ReactorCollection(typing.Protocol):
    """Provide the canonical reactions of one harness."""

    @property
    def reactors(self) -> tuple[HarnessCanonicalEventReactor, ...]:
        """The harness reactions."""
        ...


class HarnessReactorProvider(typing.Protocol):
    """Find the reactions for a harness."""

    def plugin(self, harness: HarnessName) -> ReactorCollection:
        """Return the selected harness plug-in."""
        ...
