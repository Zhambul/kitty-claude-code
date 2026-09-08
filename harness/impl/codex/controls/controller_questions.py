# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex control questions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import TypeAdapter, ValidationError

from domain.event_work import QuestionAsked
from harness.contract import ControlHandler
from harness.impl.codex.controls import dialog
from harness.impl.codex.controls.controller_results import submit_text
from harness.impl.codex.controls.controller_values import SESSION_NOT_LIVE_REASON
from harness.models import controls as control_models
from harness.services.terminal_driver import TerminalDriver

if TYPE_CHECKING:
    from domain.attention import AttentionChoice, AttentionPrompt
    from domain.ids import WindowId


def _native_prompts(question_asked: QuestionAsked) -> list[dialog.Prompt]:
    return [_native_prompt(prompt) for prompt in question_asked.questions]


def _native_prompt(attention_prompt: AttentionPrompt) -> dialog.Prompt:
    choices = [_native_choice(choice) for choice in attention_prompt.choices]
    return dialog.Prompt(
        id=attention_prompt.prompt_id,
        header=attention_prompt.title or "",
        question=attention_prompt.prompt,
        options=tuple(choices),
    )


def _native_choice(attention_choice: AttentionChoice) -> dialog.PromptChoice:
    return dialog.PromptChoice(attention_choice.label, attention_choice.description or "")


class AnswerQuestionHandler(ControlHandler):
    """Represent answer question handler."""

    def __call__(
        self, request: control_models.ControlRequest, control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Handle a question-answer request.

        Returns:
            The control result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        if not isinstance(request, control_models.AnswerQuestion):
            msg = "answer_question handler requires AnswerQuestion"
            raise TypeError(msg)
        if not isinstance(control_context.pending_attention, QuestionAsked):
            return control_models.ControlResult(
                request.request_id, control_models.ControlAcknowledgement.REJECTED, "no question is pending",
            )
        window_id = control_context.terminal_window_id
        if window_id is None:
            return control_models.ControlResult(
                request.request_id, control_models.ControlAcknowledgement.REJECTED, SESSION_NOT_LIVE_REASON,
            )
        try:
            answers = (
                []
                if request.answers is None
                else TypeAdapter(list[dialog.Answer]).validate_json(request.answers.json_text)
            )
        except ValidationError:
            return control_models.ControlResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                "question answers must be an array",
            )
        return _deliver_question_answer(request, control_context, window_id, answers)


def _deliver_question_answer(
    request: control_models.AnswerQuestion,
    control_context: control_models.ControlContext,
    window_id: WindowId,
    answers: list[dialog.Answer],
) -> control_models.ControlResult:
    pending_attention = control_context.pending_attention
    if not isinstance(pending_attention, QuestionAsked):
        return control_models.ControlResult(
            request.request_id, control_models.ControlAcknowledgement.REJECTED, "no question is pending",
        )
    prompts = _native_prompts(pending_attention)
    try:
        return _apply_question_answer(request, control_context, window_id, prompts, answers)
    except dialog.CodexAskError as error:
        return control_models.ControlResult(
            request.request_id, control_models.ControlAcknowledgement.INDETERMINATE, str(error),
        )


def _apply_question_answer(
    request: control_models.AnswerQuestion,
    control_context: control_models.ControlContext,
    window_id: WindowId,
    prompts: list[dialog.Prompt],
    answers: list[dialog.Answer],
) -> control_models.ControlResult:
    driver = TerminalDriver(control_context.terminal)
    if request.decision == control_models.AnswerDecision.DISCUSS:
        dialog.decline(driver, window_id, prompts, "Continue in chat.")
        if request.discussion:
            delivered = submit_text(request, control_context, request.discussion)
            if delivered.status != control_models.ControlAcknowledgement.ACKNOWLEDGED:
                return delivered
    else:
        dialog.drive(driver, window_id, prompts, answers)
    return control_models.ControlResult(request.request_id, control_models.ControlAcknowledgement.ACKNOWLEDGED)
