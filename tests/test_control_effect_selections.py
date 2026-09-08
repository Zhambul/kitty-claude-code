# Copyright (c) 2026 Zhambyl Yermagambet
"""Test control effect selections."""

from __future__ import annotations

import pytest

from domain import (
    event_session,
    ids as domain_ids,
    references,
    work_state,
)
from engine.interpret import translators as interpret_translators
from harness.models import controls as control_models
from tests import (
    control_effect_recording as recording,
    control_effect_sessions as control_sessions,
    control_effect_values as control_values,
)


@pytest.mark.parametrize(
    ("selection_request", "source_name", "expected"),
    [
        (
            control_models.SelectModel(control_values.TEST_SESSION_ID, domain_ids.RequestId("model-one"), "sonnet"),
            "model_selection",
            event_session.ModelChanged(
                None,
                references.ModelReference("sonnet", "sonnet"),
                work_state.ModelChangeReason.SELECTED,
            ),
        ),
        (
            control_models.SelectEffort(control_values.TEST_SESSION_ID, domain_ids.RequestId("effort-one"), "medium"),
            "effort_selection",
            event_session.EffortChanged(None, "medium", work_state.EffortChangeReason.SELECTED),
        ),
    ],
)
def test_confirmed_selections_become_canon_state(
    selection_request: control_models.SelectModel | control_models.SelectEffort,
    source_name: str,
    expected: event_session.ModelChanged | event_session.EffortChanged,
) -> None:
    """Verify confirmed selections become canonical state changes."""
    session = control_sessions.claude_session("transcript.jsonl")
    control_fixture = recording.control_effect_fixture(session=session)

    control_fixture.recorder.selection_changed(session, selection_request)

    assert len(control_fixture.raw_events.events) == 1
    raw_event = control_fixture.raw_events.events[0]
    assert raw_event.source_name == source_name
    translated = interpret_translators.ControlTranslator().translate(raw_event)
    assert [event.payload for event in translated.canonical_events] == [expected]
