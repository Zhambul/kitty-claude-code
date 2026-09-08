# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for Claude telemetry storage tests."""

import json
from decimal import Decimal

from domain.event_telemetry import UsageReported
from domain.ids import SessionId
from domain.usage import TokenUsage
from harness.models.raw_events import RawEventAudit
from harness.services.telemetry import TelemetryGatewayService
from tests.canonical_runtime import CanonicalRuntime
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.support_storage import stored_payloads


def telemetry_gateway(runtime: CanonicalRuntime) -> TelemetryGatewayService:
    """Create a telemetry gateway for the test runtime.

    Returns:
        A telemetry gateway for the test runtime.

    """
    harness_registry = runtime.sessions.harness_registry
    assert harness_registry is not None
    return TelemetryGatewayService(
        harness_registry,
        runtime.recorder,
        runtime.sessions,
    )


def claude_cost_usage_body() -> bytes:
    """Build one Claude cost usage request body.

    Returns:
        One Claude cost usage request body.

    """
    return json.dumps(
        {
            "resourceMetrics": [
                {
                    "scopeMetrics": [
                        {
                            "metrics": [
                                {
                                    fixture.NAME_FIELD: "claude_code.cost.usage",
                                    "sum": {
                                        "dataPoints": [
                                            {
                                                "attributes": [
                                                    {
                                                        "key": fixture.DOTTED_SESSION_ID_FIELD,
                                                        fixture.VALUE_FIELD: {
                                                            "stringValue": fixture.SESSION_ONE_ID,
                                                        },
                                                    },
                                                    {
                                                        "key": fixture.QUERY_SOURCE_FIELD,
                                                        fixture.VALUE_FIELD: {
                                                            "stringValue": fixture.MAIN,
                                                        },
                                                    },
                                                ],
                                                "asDouble": 0.09,
                                            },
                                        ],
                                    },
                                },
                            ],
                        },
                    ],
                },
            ],
        },
        separators=(",", ":"),
    ).encode()


def assert_telemetry_audit(
    evidence: tuple[RawEventAudit, ...],
    raw_body: bytes,
) -> None:
    """Verify the recorded raw telemetry evidence."""
    assert len(evidence) == 1
    audit = evidence[0]
    assert audit.raw_event.payload == raw_body
    assert audit.interpretation is not None
    assert audit.interpretation.decision == fixture.TRANSLATED
    assert len(audit.interpretation.events) == 1


def assert_stored_telemetry_usage(runtime: CanonicalRuntime) -> None:
    """Verify the stored usage facts from one telemetry delivery."""
    usages = stored_payloads(runtime, SessionId(fixture.SESSION_ONE_ID), UsageReported)
    assert [usage.cost_in_usd for usage in usages] == [Decimal("0.09")]
    assert [usage.tokens for usage in usages] == [TokenUsage()]
