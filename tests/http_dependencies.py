# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide canonical HTTP test dependencies."""


from tests import (
    http_application_dependencies as _application,
    http_contract_dependencies as _contracts,
    http_library_dependencies as _library,
    http_runtime_dependencies as _runtime,
    http_value_dependencies as _standard,
)

application = _application
contracts = _contracts
library = _library
runtime = _runtime
standard = _standard
