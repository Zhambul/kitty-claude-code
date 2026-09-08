# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check control responses and message delivery."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from api.controls.models.control_outcome_response import MessageDeliveryResultResponse

if TYPE_CHECKING:
    from tests.e2e.testkit.references import Controls


@then(parsers.parse('control "{name}" response is accepted'))
def control_response_is_accepted(controls: Controls, name: str) -> None:
    """Check an accepted control response."""
    receipt = controls.get(name)
    assert receipt.status_code == HTTPStatus.OK, f"control {name!r} returned {receipt.outcome}"


@then(parsers.parse('control "{name}" response is rejected'))
def control_response_is_rejected(controls: Controls, name: str) -> None:
    """Check a rejected control response."""
    receipt = controls.get(name)
    assert receipt.status_code == HTTPStatus.CONFLICT, f"control {name!r} returned {receipt.outcome}"


@then(parsers.parse('control "{name}" outcome is acknowledged'))
def control_outcome_is_acknowledged(controls: Controls, name: str) -> None:
    """Check an acknowledged control outcome."""
    receipt = controls.get(name)
    assert receipt.outcome.status == "acknowledged"


@then(parsers.parse('control "{name}" outcome is rejected'))
def control_outcome_is_rejected(controls: Controls, name: str) -> None:
    """Check a rejected control outcome."""
    receipt = controls.get(name)
    assert receipt.outcome.status == "rejected"


@then(parsers.parse('control "{name}" reports queued delivery'))
def control_reports_queued_delivery(controls: Controls, name: str) -> None:
    """Check queued prompt delivery."""
    outcome = controls.get(name).outcome
    assert isinstance(outcome, MessageDeliveryResultResponse)
    assert outcome.status == "queued"


@then(parsers.parse('control "{name}" reports sent delivery'))
def control_reports_sent_delivery(controls: Controls, name: str) -> None:
    """Check sent prompt delivery."""
    outcome = controls.get(name).outcome
    assert isinstance(outcome, MessageDeliveryResultResponse)
    assert outcome.status == "sent"
