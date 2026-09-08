# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide test foundation liveness."""

from __future__ import annotations

from tests import (
    canonical_foundation_components as foundation_components,
    foundation_dependencies,
    foundation_test_events,
    foundation_test_primitives,
    foundation_test_reactions,
    interrupt_clock,
)

IGNORED_TRANSLATION = foundation_components.raw_events.TranslationResult(
    (), foundation_dependencies.domain.domain_records.RecordedTranslationDecision.IGNORED_NONSEMANTIC,
)
OWN_PROCESS_NAME = foundation_dependencies.standard.Path(
    foundation_dependencies.standard.subprocess.run(
        ["ps", "-o", "comm=", "-p", str(foundation_dependencies.standard.os.getpid())],
        capture_output=True,
        check=False,
        text=True,
    ).stdout.strip(),
).name
FIXTURE_PROCESS_ID = 4242
SECOND_SESSION_ID_TEXT = "session-two"
WINDOW_ID_TEXT = "window-one"
TERMINAL_COLUMNS = 120
TERMINAL_LINES = 40
TAB_ID_TEXT = "tab-one"


def test_terminal_ownership_transfer_finishes_old(
    ignored_plugin: foundation_dependencies.engine.harness_contract.HarnessPlugin,
) -> None:
    """Verify terminal ownership transfer finishes the old session."""
    session = foundation_dependencies.standard.replace(
        foundation_test_events.example_session(),
        plugin=ignored_plugin,
        terminal_window_id=foundation_dependencies.domain.domain_ids.WindowId(WINDOW_ID_TEXT),
        harness_process_id=foundation_dependencies.standard.os.getpid(),
    )
    window = foundation_components.terminal_value_models.WindowInfo(
        window_id=foundation_components.terminal_value_models.WindowId(WINDOW_ID_TEXT),
        tab_id=foundation_components.terminal_value_models.TabId(TAB_ID_TEXT),
        tags={foundation_components.terminal_value_models.SESSION_WINDOW_TAG: SECOND_SESSION_ID_TEXT},
        columns=TERMINAL_COLUMNS,
        lines=TERMINAL_LINES,
        is_first_in_tab=True,
        tab_is_active=True,
        tab_is_focused=True,
        processes=(
            foundation_components.terminal_value_models.WindowProcess(
                foundation_dependencies.standard.os.getpid(), ("/opt/codex",),
            ),
        ),
    )
    source = foundation_components.liveness.SessionLivenessSource(
        session, foundation_components.liveness.ProcessProbe(), (window,),
    )
    assert not source.read(None)
    raw_event = source.read(None)[0]
    assert raw_event.source_position == "displaced"
    translation = foundation_components.translators.LivenessTranslator().translate(raw_event)
    assert len(translation.canonical_events) == 1
    assert isinstance(
        translation.canonical_events[0].payload, foundation_dependencies.domain.event_session.SessionFinished,
    )
    assert translation.canonical_events[0].payload.reason == "terminal_reassigned"


def test_transient_old_terminal_tag_does_not(
    ignored_plugin: foundation_dependencies.engine.harness_contract.HarnessPlugin,
) -> None:
    """Verify a transient old terminal tag does not finish the new session."""
    session = foundation_dependencies.standard.replace(
        foundation_test_events.example_session(),
        plugin=ignored_plugin,
        terminal_window_id=foundation_dependencies.domain.domain_ids.WindowId(WINDOW_ID_TEXT),
        harness_process_id=foundation_dependencies.standard.os.getpid(),
    )
    old_tag = foundation_components.terminal_value_models.WindowInfo(
        window_id=foundation_components.terminal_value_models.WindowId(WINDOW_ID_TEXT),
        tab_id=foundation_components.terminal_value_models.TabId(TAB_ID_TEXT),
        tags={foundation_components.terminal_value_models.SESSION_WINDOW_TAG: "old-session"},
        columns=TERMINAL_COLUMNS,
        lines=TERMINAL_LINES,
        is_first_in_tab=True,
        tab_is_active=True,
        tab_is_focused=True,
        processes=(
            foundation_components.terminal_value_models.WindowProcess(
                foundation_dependencies.standard.os.getpid(), ("/opt/codex",),
            ),
        ),
    )
    current_tag = foundation_dependencies.standard.replace(
        old_tag,
        tags={foundation_components.terminal_value_models.SESSION_WINDOW_TAG: str(session.session_id)},
    )
    probe = foundation_components.liveness.ProcessProbe()
    assert not foundation_components.liveness.SessionLivenessSource(session, probe, (old_tag,)).read(None)
    assert not foundation_components.liveness.SessionLivenessSource(session, probe, (current_tag,)).read(None)


def test_copied_terminal_id_does_not_displace_its(
    ignored_plugin: foundation_dependencies.engine.harness_contract.HarnessPlugin,
) -> None:
    """Verify a copied terminal identifier does not displace its session."""
    session = foundation_dependencies.standard.replace(
        foundation_test_events.example_session(),
        plugin=ignored_plugin,
        terminal_window_id=foundation_dependencies.domain.domain_ids.WindowId(WINDOW_ID_TEXT),
        harness_process_id=foundation_dependencies.standard.os.getpid(),
    )
    window = foundation_components.terminal_value_models.WindowInfo(
        window_id=foundation_components.terminal_value_models.WindowId(WINDOW_ID_TEXT),
        tab_id=foundation_components.terminal_value_models.TabId(TAB_ID_TEXT),
        tags={foundation_components.terminal_value_models.SESSION_WINDOW_TAG: SECOND_SESSION_ID_TEXT},
        columns=TERMINAL_COLUMNS,
        lines=TERMINAL_LINES,
        is_first_in_tab=True,
        tab_is_active=True,
        tab_is_focused=True,
        processes=(foundation_components.terminal_value_models.WindowProcess(FIXTURE_PROCESS_ID, ("/opt/codex",)),),
    )
    assert not foundation_components.liveness.SessionLivenessSource(
        session, foundation_components.liveness.ProcessProbe(), (window,),
    ).read(None)


def test_resume_liveness_waits_for_session_tag(
    ignored_plugin: foundation_dependencies.engine.harness_contract.HarnessPlugin,
) -> None:
    """Verify resume liveness waits for the session tag while the window is starting."""
    session = foundation_dependencies.standard.replace(
        foundation_test_events.example_session(),
        plugin=ignored_plugin,
        terminal_window_id=foundation_dependencies.domain.domain_ids.WindowId(WINDOW_ID_TEXT),
        harness_process_id=None,
    )
    window = foundation_components.terminal_value_models.WindowInfo(
        window_id=foundation_components.terminal_value_models.WindowId(WINDOW_ID_TEXT),
        tab_id=foundation_components.terminal_value_models.TabId(TAB_ID_TEXT),
        tags={},
        columns=TERMINAL_COLUMNS,
        lines=TERMINAL_LINES,
        is_first_in_tab=True,
        tab_is_active=True,
        tab_is_focused=True,
        processes=(
            foundation_components.terminal_value_models.WindowProcess(None, ("/bin/zsh", "-lic", "codex resume")),
        ),
    )
    assert not foundation_components.liveness.SessionWindowLivenessSource(session, (window,)).read(None)


def test_resume_liveness_finishes_missing(
    ignored_plugin: foundation_dependencies.engine.harness_contract.HarnessPlugin,
) -> None:
    """Verify resume liveness finishes a missing or reassigned window."""
    session = foundation_dependencies.standard.replace(
        foundation_test_events.example_session(),
        plugin=ignored_plugin,
        terminal_window_id=foundation_dependencies.domain.domain_ids.WindowId(WINDOW_ID_TEXT),
        harness_process_id=None,
    )
    reassigned = foundation_components.terminal_value_models.WindowInfo(
        window_id=foundation_components.terminal_value_models.WindowId(WINDOW_ID_TEXT),
        tab_id=foundation_components.terminal_value_models.TabId(TAB_ID_TEXT),
        tags={foundation_components.terminal_value_models.SESSION_WINDOW_TAG: SECOND_SESSION_ID_TEXT},
        columns=TERMINAL_COLUMNS,
        lines=TERMINAL_LINES,
        is_first_in_tab=True,
        tab_is_active=True,
        tab_is_focused=True,
        processes=(
            foundation_components.terminal_value_models.WindowProcess(None, (f"/opt/{OWN_PROCESS_NAME}", "resume")),
        ),
    )
    missing = foundation_components.liveness.SessionWindowLivenessSource(session, ()).read(None)
    transferred = foundation_components.liveness.SessionWindowLivenessSource(session, (reassigned,)).read(None)
    assert [event.source_position for event in missing] == ["exited"]
    assert [event.source_position for event in transferred] == ["exited"]


def test_the_probe_pays_for_the_name_check_once(
    monkeypatch: foundation_dependencies.standard.pytest.MonkeyPatch,
) -> None:
    """Verify the probe pays for the name check once.

    After one verified name check, a probe is a signal-0 syscall — the sources
        are rebuilt every tick, so the memory has to survive on the probe itself.
    """
    session = foundation_dependencies.standard.replace(
        foundation_test_events.example_session(), plugin=foundation_test_reactions.example_plugin(IGNORED_TRANSLATION),
    )
    probe = foundation_components.liveness.ProcessProbe()
    name_checks: list[int] = []
    monkeypatch.setattr(
        "engine.interpret.liveness.process_alive",
        lambda process_id, process_name: foundation_test_primitives.record_process_name_check(
            name_checks, process_id, process_name,
        ),
    )
    assert not foundation_components.liveness.SessionLivenessSource(session, probe).read(None)
    assert not foundation_components.liveness.SessionLivenessSource(session, probe).read(None)
    assert len(name_checks) == 1


def test_pending_interrupt_source_waits_out_grace(
    monkeypatch: foundation_dependencies.standard.pytest.MonkeyPatch,
) -> None:
    """Verify pending interrupt source waits out the grace period then latches."""
    session = foundation_dependencies.standard.replace(
        foundation_test_events.example_session(), plugin=foundation_test_reactions.example_plugin(IGNORED_TRANSLATION),
    )
    registry = foundation_dependencies.engine.InterruptRegistry()
    source = foundation_components.interrupts.PendingInterruptSource(session, registry)
    assert not source.read(None)
    registry.mark(session.session_id)
    assert not source.read(None)
    interrupt_clock.advance_past_grace(monkeypatch, registry, session.session_id)
    raw_events = source.read(None)
    assert [raw.source_type for raw in raw_events] == [foundation_components.raw_events.INTERRUPT_SOURCE_TYPE]
    assert not source.read(raw_events[0].source_position)
    with foundation_dependencies.standard.pytest.raises(ValueError, match="no attached harness plugin"):
        foundation_components.interrupts.PendingInterruptSource(
            foundation_dependencies.standard.replace(session, plugin=None), registry,
        )
