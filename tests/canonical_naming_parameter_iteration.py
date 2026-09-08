# Copyright (c) 2026 Zhambyl Yermagambet
"""Iterate typed parameters for canonical naming gates."""

import ast
from collections.abc import Iterator


def annotated_parameters(
    tree: ast.AST,
) -> Iterator[tuple[ast.FunctionDef | ast.AsyncFunctionDef, ast.arg]]:
    """Read parameters from functions in a syntax tree.

    Yields:
        Each function node and its non-receiver parameter node.

    """
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for argument in named_parameters(node):
                yield node, argument


def named_parameters(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> Iterator[ast.arg]:
    """Read named parameters except instance and class receivers.

    Yields:
        Positional and keyword-only parameter nodes, including unannotated nodes.

    """
    function_parameters = (
        *function.args.posonlyargs,
        *function.args.args,
        *function.args.kwonlyargs,
    )
    for parameter in function_parameters:
        if parameter.arg not in {"self", "cls"}:
            yield parameter
