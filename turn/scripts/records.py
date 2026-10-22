"""What Claude Code keeps of an agent's conversation, read as the learner is shown it."""

from __future__ import annotations

import glob
import json
import os
import textwrap
from typing import Any

# A page of a record is short enough for one read to show it whole.
PAGE = 20000


def entries(path: str) -> list[dict[str, Any]]:
    """The agent's own entries: Claude Code also keeps a copy of each request it sends, which says
    again what the agent was shown."""
    with open(path, encoding="utf-8") as f:
        kept = [json.loads(line) for line in f]
    return [e for e in kept if e.get("type") in ("user", "assistant", "attachment")]


def split(text: str) -> list[str]:
    """A text cut into pages, each short enough for one read to show it whole."""
    return [text[i : i + PAGE] for i in range(0, len(text), PAGE)] or [""]


def shown(path: str) -> str:
    lines: list[str] = []
    for entry in entries(path):
        attachment = entry.get("attachment")
        if isinstance(attachment, dict) and attachment.get("type") == "edited_text_file":
            lines.append(f"[shown {attachment.get('filename')}] {attachment.get('snippet')}")
        content = entry.get("message", {}).get("content")
        if isinstance(content, str):
            lines.append(f"[{entry.get('type')}] {content}")
        for part in content if isinstance(content, list) else []:
            lines.append(said(part))
    return "\n".join(lines) + "\n"


def said(part: dict[str, Any]) -> str:
    """One part of a message as the learner reads it."""
    if part.get("type") == "tool_use":
        return f"[tool_use {part.get('name')}] {json.dumps(part.get('input'), ensure_ascii=False)}"
    if part.get("type") == "tool_result":
        return f"[tool_result] {result(part)}"
    return f"[{part.get('type')}] {part.get('text', '')}"


def result(part: dict[str, Any]) -> str:
    """What a tool gave back, its text parts joined."""
    content = part.get("content")
    if isinstance(content, list):
        return "\n".join(str(c.get("text", "")) for c in content)
    return str(content)


# A line of a record as the learner is shown it, short enough for one read to show it whole.
WIDTH = 1000


def wrapped(text: str) -> str:
    """The text with each line longer than a read shows cut at its blanks, so the learner reads
    every word; a quote across a cut is found, as the cut is a blank."""
    return "".join(
        textwrap.fill(line, WIDTH, break_long_words=False) + "\n"
        if len(line) > WIDTH
        else line + "\n"
        for line in text.splitlines()
    )


def kept() -> str:
    """Where Claude Code keeps each conversation's records."""
    return os.path.join(
        os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude"), "projects"
    )


def find(agent_id: str) -> str | None:
    """The record of the agent of the ID, kept beside its conversation's as
    `<conversation>/subagents/agent-<ID>.jsonl`; None where none is."""
    found = glob.iglob(os.path.join(kept(), "*", "*", "subagents", f"agent-{agent_id}.jsonl"))
    return next(found, None)


def orchestrator(roles: list[str], result: str) -> str | None:
    """The record of the orchestrator of the run: beside its roles' records, a `turn:up` agent's
    whose prompt, the call, names the result; the latest where several do; None where none is."""
    found = []
    for folder in sorted({os.path.dirname(r) for r in roles}):
        for meta in glob.glob(os.path.join(folder, "agent-*.meta.json")):
            path = meta[: -len(".meta.json")] + ".jsonl"
            if kind(meta) == "turn:up" and os.path.exists(path) and names(path, result):
                found.append(path)
    return max(found, key=os.path.getmtime) if found else None


def kind(meta: str) -> str:
    """The agent type a record's meta file names."""
    try:
        with open(meta, encoding="utf-8") as f:
            given = json.load(f)
    except (OSError, ValueError):
        return ""
    return str(given.get("agentType", "")) if isinstance(given, dict) else ""


def names(path: str, result: str) -> bool:
    """Whether the record's first prompt is a call naming the result."""
    found = entries(path)
    content = found[0].get("message", {}).get("content") if found else None
    try:
        given = json.loads(content) if isinstance(content, str) else None
    except ValueError:
        return False
    return isinstance(given, dict) and given.get("result") == result
