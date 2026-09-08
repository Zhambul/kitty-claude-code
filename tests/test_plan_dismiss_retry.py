# Copyright (c) 2026 Zhambyl Yermagambet
"""Check bounded retries when a plan dialog misses Escape."""

from unittest.mock import Mock

import pytest

from domain.ids import WindowId
from harness.impl.claude_code.controls import plan_screen, plandialog, screen_driver
from harness.impl.claude_code.controls.plan_models import PlanError


@pytest.mark.parametrize(
    ("first_key_closes", "key_count"),
    [(True, 1), (False, plandialog.DISMISS_ATTEMPTS)],
)
def test_dismiss_stops_after_the_dialog_closes(
    monkeypatch: pytest.MonkeyPatch, key_count: int, *, first_key_closes: bool,
) -> None:
    """Do not send another key after a successful dismissal."""
    monkeypatch.setattr(plan_screen, "open_rows", Mock(return_value=[]))
    screens = [("plan", first_key_closes), ("composer", True)]
    monkeypatch.setattr(screen_driver, "poll_until", Mock(side_effect=screens))
    driver = Mock()
    assert plandialog.dismiss(driver, WindowId("1")).dismissed
    assert driver.send_key.call_count == key_count


def test_dismiss_reports_a_dialog_that_stays_open(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stop after two attempts and retain the failure screen."""
    monkeypatch.setattr(plan_screen, "open_rows", Mock(return_value=[]))
    monkeypatch.setattr(screen_driver, "poll_until", Mock(return_value=("plan", False)))
    driver = Mock()
    with pytest.raises(PlanError, match="dialog still open") as caught:
        plandialog.dismiss(driver, WindowId("1"))
    assert caught.value.screen == "plan"
    assert driver.send_key.call_count == plandialog.DISMISS_ATTEMPTS
