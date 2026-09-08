# Copyright (c) 2026 Zhambyl Yermagambet
"""Every control gesture: what is asked, what it is asked against, what came back.

One dataclass per gesture, each carrying its own `control_name` — the request
type IS the discriminator, so a handler never parses a command word, and the
union below is the whole vocabulary a harness may be asked to perform.
"""

from __future__ import annotations

from harness.models import (
    control_attention,
    control_context,
    control_enums,
    control_outcomes,
    control_plan_choices,
    control_session,
)

AnswerDecision = control_enums.AnswerDecision
ConfirmationOutcome = control_enums.ConfirmationOutcome
ControlAcknowledgement = control_enums.ControlAcknowledgement
ControlName = control_enums.ControlName
MessageDeliveryStatus = control_enums.MessageDeliveryStatus
TitleWriteOutcome = control_enums.TitleWriteOutcome
AnswerQuestion = control_attention.AnswerQuestion
DecidePlan = control_attention.DecidePlan
ReadPlanChoices = control_attention.ReadPlanChoices
AttachmentReference = control_context.AttachmentReference
Background = control_context.Background
CloseSession = control_context.CloseSession
ControlContext = control_context.ControlContext
ControlTarget = control_context.ControlTarget
Interrupt = control_context.Interrupt
SendText = control_context.SendText
CommandResult = control_outcomes.CommandResult
ControlResult = control_outcomes.ControlResult
DurableTitleResult = control_outcomes.DurableTitleResult
InterruptResult = control_outcomes.InterruptResult
MessageDeliveryResult = control_outcomes.MessageDeliveryResult
RewindResult = control_outcomes.RewindResult
PlanChoice = control_plan_choices.PlanChoice
PlanChoicesResult = control_plan_choices.PlanChoicesResult
ApplyRewind = control_session.ApplyRewind
AutoNameSession = control_session.AutoNameSession
Compact = control_session.Compact
OpenRewind = control_session.OpenRewind
RenameSession = control_session.RenameSession
SelectEffort = control_session.SelectEffort
SelectModel = control_session.SelectModel


type ControlRequest = (
    SendText
    | Interrupt
    | Background
    | CloseSession
    | RenameSession
    | AutoNameSession
    | OpenRewind
    | ApplyRewind
    | Compact
    | SelectModel
    | SelectEffort
    | AnswerQuestion
    | ReadPlanChoices
    | DecidePlan
)


type ControlOutcome = (
    ControlResult
    | DurableTitleResult
    | InterruptResult
    | MessageDeliveryResult
    | CommandResult
    | RewindResult
    | PlanChoicesResult
)
