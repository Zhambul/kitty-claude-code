# Copyright (c) 2026 Zhambyl Yermagambet
"""Own dashboard rebuild."""

from dashboard.cli_health import holder
from dashboard.cli_output import _error, _output


def rebuild() -> int:
    """Re-derive `session_data`, `session_data_actors` and `session_entries`.

    The insurance the push-based read model needs: if a writer was wrong, or
    crashed halfway, the facts are all still in `canonical_events` and the whole
    read model can be folded again from them. Runs the WRITERS only — a replay
    that also ran the side-effect reactions would reopen the panes of every
    session that ever finished.

    Not a bin script of its own: `tests/test_canonical_architecture.py` keeps the
    entry points to the two the clients need, and this is an operator's command
    on the daemon they already have.

    Returns:
        Integer result.

    """
    from app import provider_reaction_loop  # noqa: PLC0415 -- Apply CLI environment options first.
    from app.injection import registry, resolve  # noqa: PLC0415 -- Apply CLI environment options first.

    pid = holder()
    if pid:
        _error("stop the dashboard first: one writer, or the rebuild races it")
        return 1
    loop = resolve(registry(), provider_reaction_loop.reaction_loop)
    _output("rebuilding the read model…")
    total = loop.rebuild()
    _output(f"rebuilt {int(total)} facts")
    return 0
