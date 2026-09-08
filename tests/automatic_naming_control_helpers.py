# Copyright (c) 2026 Zhambyl Yermagambet
"""Durable jobs, title safety, and generic naming semantics."""

import typing
from dataclasses import replace

from harness import contract as harness_contract
from harness.models import controls as control_models
from harness.models.session import (
    Session,
)
from tests.automatic_naming_models_two import AcknowledgingHandler
from tests.automatic_naming_session_helper import session


def session_with_control_handler(
    plugin: harness_contract.HarnessPlugin,
    control_name: control_models.ControlName,
    control_handler: AcknowledgingHandler,
) -> Session:
    """Attach one control handler to the fixed session.

    Returns:
        A session whose plugin routes the supplied control to the handler.

    """
    return replace(
        session(),
        plugin=replace(
            plugin,
            controller=harness_contract.HarnessController(
                {
                    control_name: typing.cast(
                        "harness_contract.ControlHandler",
                        control_handler,
                    ),
                },
            ),
        ),
    )
