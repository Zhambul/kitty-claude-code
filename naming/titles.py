# Copyright (c) 2026 Zhambyl Yermagambet
"""Bound and normalize model-generated session titles."""

from __future__ import annotations

import html
import re
import unicodedata

from naming.errors import EmptyModelTitleError, ShortModelTitleError

FIRST_PROMPT_LIMIT = 4_000
TITLE_LIMIT = 80
TITLE_WORD_LIMIT = 8
MINIMUM_TITLE_WORDS = 3
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
HTML_TAG = re.compile(r"<[^>]*>")
MARKUP = re.compile(r"[`*_#>|~]+")
WHITESPACE = re.compile(r"\s+")


def bounded_prompt(prompt: str) -> str:
    """Remove control characters and bound one model prompt.

    Returns:
        Text result.

    """
    plain_prompt = "".join(filter(_is_prompt_character, prompt))
    return plain_prompt.strip()[:FIRST_PROMPT_LIMIT]


def normalize_title(title: str) -> str:
    """Return one safe and bounded title from model output.

    Returns:
        One safe and bounded title from model output.

    """
    first_line = _first_title_line(title)
    cleaned_title = html.unescape(HTML_TAG.sub("", first_line))
    cleaned_title = MARKDOWN_LINK.sub(r"\1", cleaned_title)
    cleaned_title = MARKUP.sub("", cleaned_title)
    cleaned_title = _remove_control_characters(cleaned_title)
    cleaned_title = WHITESPACE.sub(" ", cleaned_title).strip(" \"'`“”")
    return _bound_words(cleaned_title)


def _first_title_line(title: str) -> str:
    lines = tuple(filter(None, map(str.strip, title.splitlines())))
    if not lines:
        raise EmptyModelTitleError
    return lines[0]


def _remove_control_characters(title: str) -> str:
    return "".join(filter(_is_plain_character, title))


def _bound_words(title: str) -> str:
    words = title.split()
    if len(words) < MINIMUM_TITLE_WORDS:
        raise ShortModelTitleError
    bounded_title = " ".join(words[:TITLE_WORD_LIMIT])[:TITLE_LIMIT].rstrip()
    if not bounded_title:
        raise EmptyModelTitleError
    return bounded_title


def _is_prompt_character(character: str) -> bool:
    return character in "\n\t" or _is_plain_character(character)


def _is_plain_character(character: str) -> bool:
    return unicodedata.category(character)[:1] != "C"
