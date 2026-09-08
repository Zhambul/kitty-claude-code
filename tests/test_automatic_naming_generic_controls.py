# Copyright (c) 2026 Zhambyl Yermagambet
"""Generic automatic naming control tests."""

import typing
from dataclasses import replace

from domain import (
    event_session,
    ids as domain_ids,
    work_state,
)
from harness import contract as harness_contract
from harness.impl.codex.plugin import plugin as codex_plugin
from harness.models import controls as control_models
from naming.renamer import SessionRenamer
from terminal import adapter as terminal_adapter
from terminal.models.values import SESSION_WINDOW_TAG
from tests import (
    automatic_naming_control_helpers,
    automatic_naming_models_one,
    automatic_naming_models_two,
    automatic_naming_prompt_helper,
    automatic_naming_service_support,
    automatic_naming_session_helper,
    automatic_naming_values,
    fake_terminal,
)

if typing.TYPE_CHECKING:
    from repository.contract.sessions import SessionRepository


def test_codex_auto_name_routes_through_generic() -> None:
    """Verify codex auto name routes through generic generation and existing rename."""
    control_handler = automatic_naming_models_two.AcknowledgingHandler()
    automatic_namer = automatic_naming_models_two.RecordingNamer()
    effects = automatic_naming_models_two.Effects()
    title_adapter = automatic_naming_models_two.RecordingTitleAdapter()

    outcome = automatic_naming_service_support.control_service(
        automatic_naming_control_helpers.session_with_control_handler(
            codex_plugin,
            control_models.ControlName.RENAME_SESSION,
            control_handler,
        ),
        automatic_namer,
        effects,
        title_adapter,
    ).auto_name_session(
        control_models.AutoNameSession(automatic_naming_values.SESSION_ID, domain_ids.RequestId("generic")),
    )

    assert outcome.status == control_models.ControlAcknowledgement.ACKNOWLEDGED
    assert automatic_namer.calls == 1
    assert control_handler.requests == [
        control_models.RenameSession(
            automatic_naming_values.SESSION_ID, domain_ids.RequestId("generic"), "Generated generic control title",
        ),
    ]
    assert effects.renames == control_handler.requests
    assert title_adapter.calls == [
        (automatic_naming_values.SESSION_ID, "Generated generic control title"),
    ]


def test_terminal_rename_failure_makes_control() -> None:
    """Verify terminal rename failure makes the control indeterminate."""
    control_handler = automatic_naming_models_two.AcknowledgingHandler()
    plugin = replace(
        codex_plugin,
        controller=harness_contract.HarnessController(
            {
                control_models.ControlName.RENAME_SESSION: typing.cast(
                    "harness_contract.ControlHandler",
                    control_handler,
                ),
            },
        ),
    )
    stored_session = replace(automatic_naming_session_helper.session(), plugin=plugin)
    title_adapter = automatic_naming_models_two.RecordingTitleAdapter(
        terminal_adapter.SessionTerminalResult(succeeded=False, reason="terminal title failed"),
    )

    outcome = automatic_naming_service_support.control_service(
        stored_session,
        automatic_naming_models_two.RecordingNamer(),
        automatic_naming_models_two.Effects(),
        title_adapter,
    ).rename_session(
        control_models.RenameSession(
            automatic_naming_values.SESSION_ID, domain_ids.RequestId("rename"), "Central title",
        ),
    )

    assert outcome.status == control_models.ControlAcknowledgement.INDETERMINATE
    assert outcome.reason == "terminal title failed"
    assert title_adapter.calls == [(automatic_naming_values.SESSION_ID, "Central title")]


def test_each_canon_title_change_uses_same() -> None:
    """Verify each canonical title change uses the same session renamer."""
    adapter = automatic_naming_models_two.RecordingTitleAdapter()
    renamer = SessionRenamer(typing.cast("terminal_adapter.TerminalAdapter", adapter))
    title_event = replace(
        automatic_naming_prompt_helper.prompt_event(),
        payload=event_session.SessionTitleChanged(
            "Canonical automatic title",
            work_state.TitleOrigin.AUTOMATIC,
        ),
    )

    renamer.react(title_event)
    renamer.react(automatic_naming_prompt_helper.prompt_event())

    assert adapter.calls == [(automatic_naming_values.SESSION_ID, "Canonical automatic title")]


def test_session_renamer_resolves_and_renames() -> None:
    """Verify session renamer resolves and renames the live session tab."""
    live_session = replace(
        automatic_naming_session_helper.session(),
        terminal_window_id=domain_ids.WindowId("window-one"),
    )
    terminal = fake_terminal.FakeTerminal(
        windows=(
            fake_terminal.window(
                "window-one",
                tags={SESSION_WINDOW_TAG: str(automatic_naming_values.SESSION_ID)},
            ),
        ),
    )
    renamer = SessionRenamer(
        terminal_adapter.TerminalAdapter(
            terminal.plugin(),
            typing.cast("SessionRepository", automatic_naming_models_one.Sessions(live_session)),
        ),
    )

    renamer.react(
        replace(
            automatic_naming_prompt_helper.prompt_event(),
            payload=event_session.SessionTitleChanged(
                "Live terminal title",
                work_state.TitleOrigin.CUSTOM,
            ),
        ),
    )

    assert terminal.renamed_tabs == [("window-one", "Live terminal title")]
