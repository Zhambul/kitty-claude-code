# Copyright (c) 2026 Zhambyl Yermagambet
"""Split SDK client implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sdk import control_models
from sdk.client_answers import (
    QuestionAnswer,
    _answer_selection,
)
from sdk.client_session_controls import _SessionsBasicControls

if TYPE_CHECKING:
    from sdk.client_models import (
        ActionReceipt,
        SessionRef,
    )


class _SessionsSessionActions(_SessionsBasicControls):
    """Control session configuration and rewind actions."""

    def open_rewind(self, session: SessionRef) -> ActionReceipt:
        """Open rewind.

        Returns:
            The action receipt.

        """
        return self._control(
            session,
            "open-rewind",
            lambda request_id: control_models.open_rewind_request.OpenRewindRequest(request_id=request_id),
        )

    def apply_rewind(
        self,
        session: SessionRef,
        *,
        target_message_id: str,
        target_text: str,
        newer_prompt_count: int,
        mode: str,
    ) -> ActionReceipt:
        """Apply rewind.

        Returns:
            The action receipt.

        """
        return self._control(
            session,
            "apply-rewind",
            lambda request_id: control_models.apply_rewind_request.ApplyRewindRequest(
                request_id=request_id,
                target_message_id=target_message_id,
                target_text=target_text,
                newer_prompt_count=newer_prompt_count,
                mode=mode,
            ),
        )

    def compact(self, session: SessionRef) -> ActionReceipt:
        """Compact.

        Returns:
            The action receipt.

        """
        return self._control(
            session,
            "compact",
            lambda request_id: control_models.compact_request.CompactRequest(request_id=request_id),
        )

    def select_model(self, session: SessionRef, model: str) -> ActionReceipt:
        """Select model.

        Returns:
            The action receipt.

        """
        return self._control(
            session,
            "select-model",
            lambda request_id: control_models.select_model_request.SelectModelRequest(
                request_id=request_id, model_id=model,
            ),
        )

    def select_effort(self, session: SessionRef, effort: str) -> ActionReceipt:
        """Select effort.

        Returns:
            The action receipt.

        """
        return self._control(
            session,
            "select-effort",
            lambda request_id: control_models.select_effort_request.SelectEffortRequest(
                request_id=request_id, effort=effort,
            ),
        )


class _SessionsAttentionControls(_SessionsSessionActions):
    """Control question and plan attention."""

    def answer_question(
        self,
        session: SessionRef,
        *,
        attention_id: str,
        answers: tuple[QuestionAnswer, ...],
    ) -> ActionReceipt:
        """Answer question.

        Returns:
            The action receipt.

        """
        return self._control(
            session,
            "answer-question",
            lambda request_id: control_models.answer_question_request.AnswerQuestionRequest(
                request_id=request_id,
                attention_id=attention_id,
                decision=control_models.answer_decision.AnswerDecisionBody.ANSWER,
                answers=tuple(_answer_selection(answer) for answer in answers),
            ),
        )

    def discuss_question(
        self,
        session: SessionRef,
        *,
        attention_id: str,
        discussion: str,
    ) -> ActionReceipt:
        """Return the discuss question.

        Returns:
            Discuss question.

        """
        return self._control(
            session,
            "answer-question",
            lambda request_id: control_models.answer_question_request.AnswerQuestionRequest(
                request_id=request_id,
                attention_id=attention_id,
                decision=control_models.answer_decision.AnswerDecisionBody.DISCUSS,
                discussion=discussion,
            ),
        )

    def read_plan_choices(self, session: SessionRef, attention_id: str) -> ActionReceipt:
        """Return plan choices.

        Returns:
            Plan choices.

        """
        return self._control(
            session,
            "read-plan-choices",
            lambda request_id: control_models.read_plan_choices_request.ReadPlanChoicesRequest(
                request_id=request_id,
                attention_id=attention_id,
            ),
        )

    def decide_plan(
        self,
        session: SessionRef,
        *,
        attention_id: str,
        decision: str,
        feedback: str | None = None,
    ) -> ActionReceipt:
        """Decide plan.

        Returns:
            The action receipt.

        """
        return self._control(
            session,
            "decide-plan",
            lambda request_id: control_models.decide_plan_request.DecidePlanRequest(
                request_id=request_id,
                attention_id=attention_id,
                decision=decision,
                feedback=feedback,
            ),
        )


class SessionsResource(_SessionsAttentionControls):
    """Represent sessions resource."""
