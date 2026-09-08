# Copyright (c) 2026 Zhambyl Yermagambet
"""Own dashboard options."""

from dashboard.cli_models import _DashboardOptions
from dashboard.cli_option_parser import _parse_options
from dashboard.cli_runtime_options import _runtime_configs


def launch_options(arguments: list[str]) -> _DashboardOptions:
    """Build launch options from command-line arguments.

    The launch flags, as (variables to set, log path).

        Accepts `--flag value` and `--flag=value`, because a person types the first
        and a script generates the second.

    The parser raises UsageError for unknown options or invalid option values.

    Returns:
        Options.

    """
    parsed = _parse_options(arguments)
    return _DashboardOptions(
        parsed.variables,
        parsed.log_path,
        _runtime_configs(parsed.harness_flags),
        tuple(parsed.harness_flags),
    )
