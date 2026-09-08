#!/Users/z.yermagambet/code/personal/baqylau/.venv/bin/python
# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the retarget-python module."""

# retarget-python — point every hook entry point at the *real* CPython binary
# instead of the pyenv shim, and undo it with --revert.
#
# WHY THIS EXISTS
# ---------------
# Every hook fires a fresh `python3`. When `python3` resolves to the pyenv shim
# (a bash script that re-runs `pyenv` on every call to pick a version), that shim
# costs ~140ms of pure overhead *per process* — measured 0.15s vs 0.01s for the
# concrete interpreter it eventually execs. A single PostToolUse fans out to five
# or more hook processes, so the shim tax dominates end-to-end hook latency by an
# order of magnitude, swamping the scripts' own ~5ms of imports.
#
# The two top-level entry shapes both hit the shim:
#   1. `/abs/path/claude-*.py …`  via the `#!/usr/bin/env python3` shebang, and
#   2. any literal `python3 …` hook command in ~/.claude/settings.json.
# (Child processes are already fast: they spawn via sys.executable, which — once
# we're inside a shim-launched interpreter — is the concrete binary, not the shim.)
#
# This tool rewrites both shapes to an absolute concrete-interpreter path, chosen
# to respect pyenv's *active* selection (sys.executable under the shim already IS
# that selected binary). It is idempotent and re-runnable: run it again after a
# `pyenv` version change to re-point everything. `--revert` restores the portable
# `#!/usr/bin/env python3` shebang and the `python3` settings prefix.
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SETTINGS = Path("~/.claude/settings.json").expanduser()
ENV_SHEBANG = "#!/usr/bin/env python3"
TEXT_ENCODING = "utf-8"

# A hook command's leading interpreter token: bare `python3`, a virtualenv's
# `.../bin/python`, or a concrete `.../bin/python3[.N]` written on a previous
# run (so re-targeting is idempotent across both environment shapes).
_CMD_PY = re.compile(r'("command":\s*")(python3|\S*/bin/python(?:3(?:\.\d+)?)?)(\s)')


def real_interpreter() -> str:
    """Return the real interpreter.

    The concrete interpreter to bake in — never the shim.

        Under the pyenv shim, sys.executable is already the selected version's real
        binary (the shim execs it), so it honours `pyenv version`. Only if we were
        somehow launched via the shim path itself do we fall back to resolving it.

    Returns:
        Real interpreter.

    Exit the process if no executable interpreter is found outside pyenv's shims.

    """
    interpreter_path = sys.executable or ""
    if interpreter_path and "/shims/" not in interpreter_path and os.access(interpreter_path, os.X_OK):
        return interpreter_path
    resolved_path = os.path.realpath(interpreter_path) if interpreter_path else ""
    if resolved_path and "/shims/" not in resolved_path and os.access(resolved_path, os.X_OK):
        return resolved_path
    message = "could not resolve a concrete python3 (only found the shim)"
    sys.exit(message)


def retarget_shebangs(interpreter: str, *, revert: bool) -> list[str]:
    """Return the retarget shebangs.

    Returns:
        Retarget shebangs.

    """
    new_line = ENV_SHEBANG if revert else f"#!{interpreter}"
    return [path.name for path in sorted(HERE.iterdir()) if _retarget_file(path, new_line)]


def _retarget_file(path: Path, new_line: str) -> bool:
    if path.suffix != ".py":
        return False
    # utf-8 on BOTH halves, explicitly: this is a read-modify-WRITE of the
    # repo's own sources, and they are full of non-ASCII (⧉ ✉ ▪ ⇢, the
    # Kazakh in the docs). Under a non-UTF-8 locale the default encoding
    # would decode the body one way and re-encode it another — rewriting a
    # shebang would corrupt every bin/ entry it touched.
    with path.open(encoding=TEXT_ENCODING) as source:
        lines = source.readlines()
    if not lines:
        return False
    if not (lines[0].startswith("#!") and "python" in lines[0]):
        return False
    if lines[0].rstrip("\n") == new_line:
        return False
    lines[0] = f"{new_line}\n"
    with path.open("w", encoding=TEXT_ENCODING) as sink:
        sink.writelines(lines)
    return True


def retarget_settings(interpreter: str, *, revert: bool) -> int | None:
    """Return the retarget settings.

    Returns:
        Retarget settings.

    """
    if not SETTINGS.exists():
        return None
    with SETTINGS.open(encoding=TEXT_ENCODING) as source:  # same read-modify-write
        text = source.read()  # pairing as above
    replacement = "python3" if revert else interpreter
    new_text, replacement_count = _CMD_PY.subn(
        lambda match: match.group(1) + replacement + match.group(3),
        text,
    )
    if new_text != text:
        SETTINGS.write_text(new_text, encoding=TEXT_ENCODING)
        return replacement_count
    return 0  # matched, but already pointed at the target — nothing written


USAGE = "usage: retarget-python [--revert]"


def _output(message: str) -> None:
    sys.stdout.write(f"{message}\n")


def main() -> None:
    # An UNRECOGNISED argument must not be read as "retarget" — this tool rewrites
    # files in place, and the old `"--revert" in argv` test meant every other argv,
    # `--help` included, silently performed the rewrite (it rewrote a shebang out
    # from under the author of this comment). Anything but the one flag is usage.
    """Run the command.

    Exit the process if the command input is not valid.

    """
    args = sys.argv[1:]
    if args in (["-h"], ["--help"]):
        _output(USAGE)
        return
    if args not in ([], ["--revert"]):
        message = "{}\nunrecognised: {}".format(USAGE, " ".join(args))
        sys.exit(message)
    revert = args == ["--revert"]
    _retarget(revert=revert)


def _retarget(*, revert: bool) -> None:
    interpreter = real_interpreter()
    changed_shebangs = retarget_shebangs(interpreter, revert=revert)
    changed_commands = retarget_settings(interpreter, revert=revert)
    if revert:
        _output(f"reverted to: {ENV_SHEBANG}")
    else:
        _output(f"targeting: {interpreter}")
    changed_names = ", ".join(changed_shebangs)
    changed_detail = f"  ({changed_names})" if changed_shebangs else "  (already current)"
    _output(
        f"  shebangs rewritten : {len(changed_shebangs)}"
        + changed_detail,
    )
    if changed_commands is None:
        _output(f"  settings.json      : not found at {SETTINGS}")
    else:
        _output(f"  settings commands  : {changed_commands} interpreter token(s) rewritten")
    if not revert:
        _output("Re-run this after any `pyenv` version change to re-point the hooks.")


if __name__ == "__main__":
    main()
