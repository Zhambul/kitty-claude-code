# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide E2E fixture dependencies."""


from tests.e2e import (
    e2e_application_dependencies as _application,
    e2e_context_dependencies as _contexts,
    e2e_driver_dependencies as _drivers,
    e2e_harness_dependencies as _harness,
    e2e_standard_dependencies as _standard,
    e2e_testkit_dependencies as _testkit,
)

application = _application
contexts = _contexts
drivers = _drivers
harness = _harness
standard = _standard
testkit = _testkit
