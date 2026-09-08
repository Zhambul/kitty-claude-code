# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that answer browser questions and decide browser plans."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from tests.e2e.testkit import planning
from tests.e2e.testkit.browser import BrowserPlanAction

if TYPE_CHECKING:
    from tests.e2e.testkit import browser_contexts
    from tests.e2e.testkit.browser import BrowserSessionDriver
    from tests.e2e.testkit.references import BrowserActions, Plans, Questions, Turns


@when(parsers.parse("I answer question \"{question_name}\" in the browser with option '{option}'"))
def answer_question_in_browser(
    browser_session_driver: BrowserSessionDriver,
    questions: Questions,
    turns: Turns,
    question_name: str,
    option: str,
) -> None:
    """Answer one browser question."""
    reference = questions.get(question_name)
    action = browser_session_driver.answer_question(reference, option)
    turn = turns.get(reference.turn_name)
    turns.replace(reference.turn_name, turn.resumed_after(action.cursor_before))


@when(parsers.parse('I choose chat about question "{question_name}" in the browser'))
def discuss_question_in_browser(
    browser_session_driver: BrowserSessionDriver,
    questions: Questions,
    question_name: str,
) -> None:
    """Choose chat for one browser question."""
    browser_session_driver.discuss_question(questions.get(question_name))


@when(parsers.parse('I approve plan "{plan_name}" in the browser as action "{action_name}"'))
def approve_plan_in_browser(
    browser_session_driver: BrowserSessionDriver,
    browser_actions: BrowserActions,
    plans: Plans,
    plan_name: str,
    action_name: str,
) -> None:
    """Approve one browser plan."""
    browser_actions.bind(
        action_name,
        browser_session_driver.decide_plan(plans.get(plan_name), BrowserPlanAction.approve),
    )


@then(parsers.parse('plan "{plan_name}" is followed by final answer \'{text}\' after browser action "{action_name}"'))
def plan_is_followed_by_browser_answer(
    browser_plan_context: browser_contexts.BrowserPlanContext,
    plan_name: str,
    text: str,
    action_name: str,
) -> None:
    """Wait for the answer after one browser plan action.

    Raises:
        AssertionError: If the action and plan use different sessions.

    """
    reference = browser_plan_context.plans.get(plan_name)
    action = browser_plan_context.actions.get(action_name)
    if action.session != reference.session:
        message = "browser action and plan belong to different sessions"
        raise AssertionError(message)
    planning.wait_for_plan_answer(
        browser_plan_context.client,
        reference,
        planning.PlanAnswerExpectation(action.cursor_before, text, plan_name, browser_plan_context.wait_policy.turn),
    )


@when(parsers.parse('I choose chat about plan "{plan_name}" in the browser'))
def discuss_plan_in_browser(browser_session_driver: BrowserSessionDriver, plans: Plans, plan_name: str) -> None:
    """Choose chat for one browser plan."""
    browser_session_driver.decide_plan(plans.get(plan_name), BrowserPlanAction.dismiss)


@when(parsers.parse("I request plan changes '{feedback}' for plan \"{plan_name}\" in the browser"))
def request_plan_changes_in_browser(
    browser_session_driver: BrowserSessionDriver,
    plans: Plans,
    feedback: str,
    plan_name: str,
) -> None:
    """Request changes for one browser plan."""
    browser_session_driver.decide_plan(plans.get(plan_name), BrowserPlanAction.feedback, feedback=feedback)
