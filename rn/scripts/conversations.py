"""The orchestrator's conversations with the user as Claude Code keeps them, found by the top of the
repository and the branch: whether the user typed a command, as an approval counts only from the
user's own action, and what was said and done in each from a time on, for the learnings."""

from __future__ import annotations

import datetime
import glob
import os
from typing import Any

import record
import records
import repo


def typed(command: str, start: float) -> bool:
    """Whether the user typed the command, at or after the time in seconds since 1970, in a
    conversation run at the top of the repository on the checked-out branch: an entry of the
    user's that is a command, as Claude Code keeps one typed, and names it; never an agent's
    message nor what a tool gave back, which are kept otherwise."""
    name = f"<command-name>{command}</command-name>"
    for path in conversations(repo.top(), repo.branch()):
        for entry in records.entries(path):
            text = record.text(entry) or ""
            if text.startswith("<command-") and name in text and since(entry, start):
                return True
    return False


def begun(path: str) -> tuple[str, str]:
    """When the record began, its earliest entry's time, Claude Code writing each in one form; and
    its path, so records begun at once come in one order."""
    times = [e["timestamp"] for e in records.entries(path) if "timestamp" in e]
    return min(times, default=""), path


def conversations(top: str, branch: str) -> list[str]:
    """The record of each conversation run at the top of the repository that was on the branch at
    some entry, in the order they began."""
    found = [
        path
        for folder in record.folders(top)
        for path in glob.glob(os.path.join(glob.escape(folder), "*.jsonl"))
        if any(e.get("cwd") == top and e.get("gitBranch") == branch for e in records.entries(path))
    ]
    return sorted(found, key=begun)


def since(entry: dict[str, Any], start: float) -> bool:
    """Whether the entry was kept at or after the time, in seconds since 1970; not where it has no
    time."""
    at = entry.get("timestamp")
    # Python 3.9 reads no `Z` for UTC, which Claude Code writes.
    return (
        at is not None
        and datetime.datetime.fromisoformat(at.replace("Z", "+00:00")).timestamp() >= start
    )


def told(path: str, start: float) -> str:
    """A conversation of the orchestrator from the time, in seconds since 1970: the user's words,
    each skill's text, the orchestrator's words and each tool it called, one to a line; what each
    tool gave back is left out, as the record shows what was kept, and it is most of the
    conversation; "" where it holds none of them from the time."""
    said: list[str] = []
    for entry in (e for e in records.entries(path) if since(e, start)):
        content = record.content(entry)
        if isinstance(content, str):
            said.append(f"[{entry.get('type')}] {content}")
        said += [
            records.said(b) for b in record.blocks(entry) if b.get("type") in ("text", "tool_use")
        ]
    return "".join(f"{line}\n" for line in said)
