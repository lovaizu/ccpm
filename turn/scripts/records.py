"""Each record of a run as the learner is shown it: what Claude Code keeps of an agent's
conversation, found and read by lane's record.py, as text the learner reads whole."""

from __future__ import annotations

import glob
import json
import os
import textwrap
from typing import Any

import record

# A line of a record as the learner is shown it, short enough for one read to show it whole.
WIDTH = 1000


def entries(path: str) -> list[dict[str, Any]]:
    """The agent's own entries of the record at the path: Claude Code also keeps a copy of each
    request it sends, which says again what the agent was shown."""
    kept = record.read(path) or []
    return [e for e in kept if e.get("type") in ("user", "assistant", "attachment")]


def as_text(path: str) -> str:
    """The record at the path as the learner reads it: each message by its type, each file Claude
    Code showed the agent whole by its name, a line each."""
    lines: list[str] = []
    for entry in entries(path):
        attachment = entry.get("attachment")
        if isinstance(attachment, dict) and attachment.get("type") == "edited_text_file":
            lines.append(f"[shown {attachment.get('filename')}] {attachment.get('snippet')}")
        content = record.content(entry)
        if isinstance(content, str):
            lines.append(f"[{entry.get('type')}] {content}")
        lines += [said(part) for part in record.blocks(entry)]
    return "\n".join(lines) + "\n"


def said(part: dict[str, Any]) -> str:
    """One part of a message as the learner reads it."""
    if part.get("type") == "tool_use":
        return f"[tool_use {part.get('name')}] {given(part.get('input'))}"
    if part.get("type") == "tool_result":
        return f"[tool_result] {result(part)}"
    return f"[{part.get('type')}] {part.get('text', '')}"


def given(values: Any) -> str:
    """What a tool was given, each value under its name, text as the agent wrote it, so a quote
    of a file it wrote is found with its quotes and lines as they are; any other value as JSON."""
    if not isinstance(values, dict):
        return json.dumps(values, ensure_ascii=False)
    return "\n".join(
        f"{name}: {v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)}"
        for name, v in values.items()
    )


def result(part: dict[str, Any]) -> str:
    """What a tool gave back, its text parts joined."""
    content = part.get("content")
    if isinstance(content, list):
        return "\n".join(str(c.get("text", "")) for c in content if isinstance(c, dict))
    return str(content)


def wrapped(text: str) -> str:
    """The text with each line longer than a read shows cut at its blanks, so the learner reads
    every word; a quote across a cut is found, as the cut is a blank."""
    return "".join(
        textwrap.fill(line, WIDTH, break_long_words=False) + "\n"
        if len(line) > WIDTH
        else line + "\n"
        for line in text.splitlines()
    )


def find(agent_id: str) -> str | None:
    """The record of the agent of the ID, in any conversation Claude Code keeps; None where none
    is."""
    return next(glob.iglob(record.subagent(record.conversation(), agent_id)), None)


def orchestrator(roles: list[str], result: str) -> str | None:
    """The record of the orchestrator of the run: beside its roles' records, a `turn:up` agent's
    whose prompt, the call, names the result; the latest where several do; None where none is."""
    found = [
        path
        for conversation in sorted({os.path.dirname(os.path.dirname(r)) + ".jsonl" for r in roles})
        for path in glob.glob(record.subagent(glob.escape(conversation), "*"))
        if record.agent_type(path) == "turn:up" and names(path, result)
    ]
    return max(found, key=os.path.getmtime) if found else None


def names(path: str, result: str) -> bool:
    """Whether the record's prompt is a call naming the result."""
    try:
        given = json.loads(record.prompt(record.read(path) or []))
    except ValueError:
        return False
    return isinstance(given, dict) and given.get("result") == result
