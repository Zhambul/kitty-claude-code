# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the slashcmds module."""
# harness/impl/claude_code/slashcmds.py — slash-command discovery for the web
# composer's "/" menu.
#
# The dashboard composer offers the same "/" autocomplete the Claude Code TUI
# does. The TUI stays AUTHORITATIVE — the composer only TYPES the command into
# the terminal (Frontend.send_text) and Claude Code's own palette executes it —
# so this list has to be good enough to complete against, never to validate:
# BUILTINS is a curated snapshot of the CLI's built-in commands (drift is
# harmless — an unknown or missing name still types fine), and the custom
# entries are discovered from the same ancestor-`.claude/` walk that
# agent/settings resolution uses (config_dirs.claude_dirs, env_pin=False — the
# lookup is for an ARBITRARY session's cwd, not this process's project):
# `commands/**/*.md` (namespaced by subdirectory, `gh/fix.md` -> `gh:fix`)
# and `skills/*/SKILL.md`.

from dataclasses import dataclass
from pathlib import Path

from harness.impl.claude_code.config_dirs import claude_dirs

DESCRIPTION_CHARACTER_LIMIT = 120

# Curated snapshot of the CLI's built-in slash commands. The composer's menu
# is a convenience layer over the TUI's own palette, so an entry the CLI
# dropped types harmlessly and an entry the CLI added is simply not offered
# until this list catches up.
BUILTINS = (
    ("add-dir", "add a new working directory"),
    ("agents", "manage agent configurations"),
    ("clear", "clear conversation history"),
    ("compact", "compact the conversation, keeping a summary"),
    ("config", "open the settings panel"),
    ("context", "visualize current context usage"),
    ("cost", "show session cost and duration"),
    ("doctor", "diagnose the Claude Code installation"),
    ("exit", "exit the session"),
    ("export", "export the conversation"),
    ("fast", "toggle fast mode"),
    ("goal", "set an autonomous completion goal Claude works toward"),
    ("help", "show help and available commands"),
    ("hooks", "manage hook configurations"),
    ("init", "initialize a CLAUDE.md for this project"),
    ("loop", "repeat a prompt until a condition is met"),
    ("mcp", "manage MCP servers"),
    ("memory", "edit memory files"),
    ("model", "switch the model for this session"),
    ("output-style", "set the output style"),
    ("permissions", "view or update permissions"),
    ("pr-comments", "get comments from a GitHub PR"),
    ("release-notes", "view release notes"),
    ("rename", "rename the session (bare = Claude names it)"),
    ("resume", "resume a previous conversation"),
    ("review", "review a pull request"),
    ("rewind", "rewind the conversation"),
    ("security-review", "security review of pending changes"),
    ("status", "show session status"),
    ("statusline", "set up the status line"),
    ("todos", "list current todo items"),
    ("usage", "show plan usage limits"),
    ("vim", "toggle vim editing mode"),
)

_HEAD = 4096  # how much of a command/skill file the description scan reads


@dataclass(frozen=True)
class SlashCommand:
    """Represent slash command."""

    name: str
    description: str
    source: str


class _DescriptionReader:
    def __init__(self, path: str) -> None:
        try:
            with Path(path).open(encoding="utf-8", errors="replace") as source:
                self.lines: list[str] | None = source.read(_HEAD).splitlines()
        except OSError:
            self.lines = None

    def description(self) -> str:
        if self.lines is None:
            return ""
        frontmatter_description, body_start = self._frontmatter()
        if frontmatter_description:
            return frontmatter_description
        return self._body(body_start)

    def _frontmatter(self) -> tuple[str | None, int]:
        lines = self.lines or []
        if not lines or lines[0].strip() != "---":
            return None, 0
        for line_index, line in enumerate(lines[1:], start=1):
            stripped_line = line.strip()
            if stripped_line == "---":
                return None, line_index + 1
            if stripped_line.startswith("description:"):
                description = stripped_line[len("description:") :].strip().strip("'\"")
                if description:
                    return description[:DESCRIPTION_CHARACTER_LIMIT], len(lines)
        return None, len(lines)

    def _body(self, body_start: int) -> str:
        lines = self.lines or []
        for body_line in lines[body_start:]:
            stripped_line = body_line.strip()
            if stripped_line:
                return stripped_line.lstrip("#").strip()[:DESCRIPTION_CHARACTER_LIMIT]
        return ""


def describe(path: str) -> str:
    """Return the describe.

    One display line for a command/skill file: the YAML frontmatter's
        `description:` when present, else the first non-empty body line (leading
        `#` heading marks stripped). Unreadable file -> '' (the entry still lists
        by name — same optional-file tolerance as session_title).

    Returns:
        Describe.

    """
    return _DescriptionReader(path).description()


def _dir_label(candidate_directory: str, configuration_directory: str) -> str:
    return "user" if candidate_directory == configuration_directory else "project"


class _SlashCommandCatalog:
    def __init__(self) -> None:
        self.commands: list[SlashCommand] = []
        self.names: set[str] = set()

    def add(self, name: str, description: str, source: str) -> None:
        if name and name not in self.names:
            self.names.add(name)
            self.commands.append(SlashCommand(name, description, source))

    def add_builtins(self) -> None:
        for name, description in BUILTINS:
            self.add(name, description, "built-in")

    def add_directory(
        self,
        candidate_directory: str,
        configuration_directory: str,
    ) -> None:
        label = _dir_label(candidate_directory, configuration_directory)
        self._add_command_files(Path(candidate_directory) / "commands", label)
        self._add_skills(Path(candidate_directory) / "skills", label)

    def result(self) -> list[SlashCommand]:
        return sorted(self.commands, key=lambda command: command.name)

    def _add_command_files(self, command_root: Path, label: str) -> None:
        for command_file in sorted(command_root.rglob("*.md")):
            relative_name = command_file.relative_to(command_root).with_suffix("")
            self.add(
                ":".join(relative_name.parts),
                describe(str(command_file)),
                label,
            )

    def _add_skills(self, skill_root: Path, label: str) -> None:
        skill_directories = sorted(skill_root.iterdir()) if skill_root.is_dir() else ()
        for skill_directory in skill_directories:
            skill_file = skill_directory / "SKILL.md"
            if skill_file.is_file():
                self.add(
                    skill_directory.name,
                    describe(str(skill_file)),
                    f"{label} skill",
                )


def slash_commands(
    cwd: str | None,
    configuration_directory: str,
) -> list[SlashCommand]:
    """Return the slash commands.

    [{name, desc, src}, …] for a session rooted at `cwd`, sorted by name and
        name-deduped: built-ins first (the TUI resolves those names to itself no
        matter what a same-named custom file claims), then discovered entries in
        claude_dirs order (nearest-first — a project command shadows a user-level
        one of the same name). src: 'built-in' | 'project' | 'user' (+' skill').
        No cwd (a session with no recorded one) still gets built-ins + the
        user-level entries.

    Returns:
        Slash commands.

    """
    catalog = _SlashCommandCatalog()
    catalog.add_builtins()
    directories = (
        claude_dirs(start=cwd, env_pin=False, config=configuration_directory) if cwd else [configuration_directory]
    )
    for candidate_directory in directories:
        catalog.add_directory(candidate_directory, configuration_directory)
    return catalog.result()
