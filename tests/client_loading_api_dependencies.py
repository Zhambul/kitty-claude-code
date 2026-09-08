# Copyright (c) 2026 Zhambyl Yermagambet
"""Group API modules inspected by client architecture tests."""


from api.controls import routes as _control_routes
from api.hooks import routes as _hook_routes
from api.sessiondata import routes as _session_data_routes, streams as _session_data_streams
from api.telemetry import harness as _telemetry_routes
from api.terminal import panes as _pane_routes

control_routes = _control_routes
hook_routes = _hook_routes
session_data_routes = _session_data_routes
session_data_streams = _session_data_streams
telemetry_routes = _telemetry_routes
pane_routes = _pane_routes
