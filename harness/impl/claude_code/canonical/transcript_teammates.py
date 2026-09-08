# Copyright (c) 2026 Zhambyl Yermagambet
"""Read teammate metadata near Claude transcripts."""

from pathlib import Path

from harness.impl.claude_code.canonical import records
from harness.impl.claude_code.ids import ClaudeCodeActorId
from harness.models import raw_events

AGENT_SUBDIR = "subagents"
TEXT_ENCODING = "utf-8"


def teammate_meta(path: str, actor_id: ClaudeCodeActorId) -> records.AgentMetaFile:
    """Read the sidecar for one native teammate actor.

    Returns:
        The agent meta file.

    """
    base = path.removesuffix(".jsonl")
    metadata_path = Path(base) / AGENT_SUBDIR / f"agent-{actor_id}.meta.json"
    try:
        with metadata_path.open(encoding=TEXT_ENCODING) as source:
            return records.AgentMetaFile.model_validate_json(source.read())
    except OSError:
        return records.AgentMetaFile()


def teammate_actor_id(path: str, teammate_name: str) -> ClaudeCodeActorId | None:
    """Resolve Claude's short teammate name to its transcript actor id.

    Returns:
        The claude code actor id.

    Raises:
        TranslationError: If a raw event cannot be translated.

    """
    if not teammate_name:
        return None
    metadata_directory = Path(path.removesuffix(".jsonl")) / AGENT_SUBDIR
    matches: list[ClaudeCodeActorId] = []
    for metadata_path in sorted(metadata_directory.glob("agent-*.meta.json")):
        match = _teammate_metadata_match(metadata_path, teammate_name)
        if match is not None:
            matches.append(match)
    if len(matches) > 1:
        message = f"Claude Code teammate name {teammate_name!r} identifies multiple actors"
        raise raw_events.TranslationError(
            message,
        )
    return matches[0] if matches else None


def _teammate_metadata_match(
    metadata_path: Path,
    teammate_name: str,
) -> ClaudeCodeActorId | None:
    try:
        with metadata_path.open(encoding=TEXT_ENCODING) as source:
            metadata = records.AgentMetaFile.model_validate_json(source.read())
    except OSError:
        return None
    if metadata.name != teammate_name:
        return None
    prefix = "agent-"
    suffix = ".meta.json"
    actor_text = metadata_path.name[len(prefix) : -len(suffix)]
    return ClaudeCodeActorId(actor_text) if actor_text else None
