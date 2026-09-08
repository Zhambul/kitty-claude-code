# Copyright (c) 2026 Zhambyl Yermagambet
"""Find and copy Claude Code shell output without running the command."""

from __future__ import annotations

import os
import pathlib
import shlex

import bashlex  # type: ignore[import-untyped]  # bashlex does not provide type information.

from harness.impl.claude_code.shell_models import RedirectedOutput as RedirectedOutput, ShellChild, ShellDirectory


def copy_output_to(command: str, output_path: str) -> str:
    """Return a command that copies stdout and stderr to `output_path`.

    Returns:
        A command that copies stdout and stderr to `output_path`.

    """
    quoted_path = shlex.quote(output_path)
    return f"{{ {command}\n\n}} > >(tee -a {quoted_path}) 2> >(tee -a {quoted_path} >&2)"


_OUTPUT_REDIRECTS = (">", ">>", ">|", "&>", "&>>")
_APPEND_REDIRECTS = (">>", "&>>")
KIND_ATTRIBUTE = "kind"
PARTS_ATTRIBUTE = "parts"
WORD_KIND = "word"
STANDARD_INPUT_PATH = "-"
DIRECTORY_CHANGE_WORD_COUNT = 2


class _ShellSyntax:
    def __init__(self) -> None:
        self.output_redirects = _OUTPUT_REDIRECTS
        self.append_redirects = _APPEND_REDIRECTS

    def literal_word(self, node: bashlex.ast.node) -> str | None:
        if getattr(node, KIND_ATTRIBUTE, None) != WORD_KIND:
            return None
        parts = getattr(node, PARTS_ATTRIBUTE, ())
        if any(getattr(part, KIND_ATTRIBUTE, None) != "tilde" for part in parts):
            return None
        word = str(node.word)
        if word == "~" or word.startswith("~/"):
            word = str(pathlib.Path(word).expanduser())
        if not word or any(character in word for character in "$`*?["):
            return None
        return word

    def output_path(
        self,
        node: bashlex.ast.node,
        shell_directory: ShellDirectory,
    ) -> str | None:
        target = self.literal_word(node)
        if target is None or target == STANDARD_INPUT_PATH or target.startswith("/dev/"):
            return None
        if pathlib.Path(target).is_absolute():
            return os.path.normpath(target)
        if not shell_directory.known:
            return None
        return os.path.normpath(pathlib.Path(shell_directory.path) / target)

    def word_nodes(self, command: bashlex.ast.node) -> list[bashlex.ast.node]:
        return [part for part in getattr(command, PARTS_ATTRIBUTE, ()) if part.kind == WORD_KIND]

    def redirects(
        self,
        command: bashlex.ast.node,
        shell_directory: ShellDirectory,
    ) -> list[RedirectedOutput]:
        found: list[RedirectedOutput] = []
        for part in getattr(command, PARTS_ATTRIBUTE, ()):
            redirect_type = getattr(part, "type", None)
            if getattr(part, KIND_ATTRIBUTE, None) != "redirect":
                continue
            if redirect_type not in self.output_redirects:
                continue
            path = self.output_path(getattr(part, "output", None), shell_directory)
            if path is not None:
                found.append(
                    RedirectedOutput(path, redirect_type in self.append_redirects),
                )
        return found

    def children(
        self,
        node: bashlex.ast.node,
        shell_directory: ShellDirectory,
    ) -> list[ShellChild]:
        kind = getattr(node, KIND_ATTRIBUTE, None)
        if kind == "pipeline":
            return [
                ShellChild(part, shell_directory.copy())
                for part in node.parts
                if getattr(part, KIND_ATTRIBUTE, None) != "pipe"
            ]
        if kind == "compound":
            compound_parts = getattr(node, "list", ())
            first_word = next(
                (getattr(part, WORD_KIND, None) for part in compound_parts if part.kind == "reservedword"),
                None,
            )
            scoped_directory = shell_directory.copy() if first_word == "(" else shell_directory
            return [
                ShellChild(part, scoped_directory)
                for part in compound_parts
                if getattr(part, KIND_ATTRIBUTE, None) != "reservedword"
            ]
        return [
            ShellChild(part, shell_directory)
            for part in getattr(node, PARTS_ATTRIBUTE, ())
            if getattr(part, KIND_ATTRIBUTE, None) not in {"operator", "pipe", "reservedword"}
        ]


class _TeeOutputParser:
    def __init__(
        self,
        shell_syntax: _ShellSyntax,
        shell_directory: ShellDirectory,
    ) -> None:
        self.syntax = shell_syntax
        self.shell_directory = shell_directory
        self.append = False
        self.options = True
        self.found: list[RedirectedOutput] = []

    def outputs(self, command: bashlex.ast.node) -> list[RedirectedOutput]:
        words = self.syntax.word_nodes(command)
        if not words or not self._is_tee(words[0]):
            return []
        for word_node in words[1:]:
            self._accept(word_node)
        return self.found

    def _is_tee(self, word_node: bashlex.ast.node) -> bool:
        executable = self.syntax.literal_word(word_node)
        return executable is not None and pathlib.Path(executable).name == "tee"

    def _accept(self, word_node: bashlex.ast.node) -> None:
        word = self.syntax.literal_word(word_node)
        if word is None:
            return
        if self.options and word == "--":
            self.options = False
            return
        if self.options and word.startswith(STANDARD_INPUT_PATH) and word != STANDARD_INPUT_PATH:
            short_append_option = not word.startswith("--") and "a" in word[1:]
            self.append = self.append or word == "--append" or short_append_option
            return
        path = self.syntax.output_path(word_node, self.shell_directory)
        if path is not None:
            self.found.append(RedirectedOutput(path, self.append))


class _ShellOutputScanner:
    def __init__(self, working_directory: str | None) -> None:
        self.syntax = _ShellSyntax()
        self.shell_directory = ShellDirectory(
            working_directory or str(pathlib.Path.cwd()),
        )
        self.found: list[RedirectedOutput] = []

    def scan(self, command: str) -> tuple[RedirectedOutput, ...]:
        try:
            roots = bashlex.parse(command)
        except (bashlex.errors.ParsingError, NotImplementedError):
            return ()
        for root in roots:
            self._walk(root, self.shell_directory)
        return self._unique_outputs()

    def _walk(
        self,
        node: bashlex.ast.node,
        shell_directory: ShellDirectory,
    ) -> None:
        if getattr(node, KIND_ATTRIBUTE, None) == "command":
            self._walk_command(node, shell_directory)
            return
        for child in self.syntax.children(node, shell_directory):
            self._walk(child.node, child.directory)

    def _walk_command(
        self,
        command: bashlex.ast.node,
        shell_directory: ShellDirectory,
    ) -> None:
        self.found.extend(self.syntax.redirects(command, shell_directory))
        self.found.extend(
            _TeeOutputParser(self.syntax, shell_directory).outputs(command),
        )
        for nested_command in self._nested_commands(command):
            self._walk(nested_command, shell_directory.copy())
        self._change_directory(command, shell_directory)

    def _nested_commands(
        self,
        command: bashlex.ast.node,
    ) -> list[bashlex.ast.node]:
        nested_commands: list[bashlex.ast.node] = []
        words = self.syntax.word_nodes(command) + [
            part.output
            for part in getattr(command, PARTS_ATTRIBUTE, ())
            if getattr(part, KIND_ATTRIBUTE, None) == "redirect"
            and getattr(getattr(part, "output", None), KIND_ATTRIBUTE, None) == WORD_KIND
        ]
        for word in words:
            for part in getattr(word, PARTS_ATTRIBUTE, ()):
                nested_command = getattr(part, "command", None)
                if nested_command is not None:
                    nested_commands.append(nested_command)
        return nested_commands

    def _change_directory(
        self,
        command: bashlex.ast.node,
        shell_directory: ShellDirectory,
    ) -> None:
        words = self.syntax.word_nodes(command)
        if not words or self.syntax.literal_word(words[0]) != "cd":
            return
        if len(words) != DIRECTORY_CHANGE_WORD_COUNT:
            shell_directory.known = False
            return
        target = self.syntax.literal_word(words[1])
        if target is None or target == STANDARD_INPUT_PATH or target.startswith(STANDARD_INPUT_PATH):
            shell_directory.known = False
        elif pathlib.Path(target).is_absolute():
            shell_directory.path = os.path.normpath(target)
            shell_directory.known = True
        elif shell_directory.known:
            shell_directory.path = os.path.normpath(
                pathlib.Path(shell_directory.path) / target,
            )

    def _unique_outputs(self) -> tuple[RedirectedOutput, ...]:
        unique: list[RedirectedOutput] = []
        for output in self.found:
            previous_index = next(
                (index for index, previous in enumerate(unique) if previous.path == output.path),
                None,
            )
            if previous_index is None:
                unique.append(output)
            elif unique[previous_index].append and not output.append:
                unique[previous_index] = RedirectedOutput(
                    path=output.path,
                    append=False,
                )
        return tuple(unique)


def redirected_outputs(command: str, working_directory: str | None) -> tuple[RedirectedOutput, ...]:
    """Return each concrete file that receives output from this command.

    Returns:
        Each concrete file that receives output from this command.

    """
    return _ShellOutputScanner(working_directory).scan(command)
