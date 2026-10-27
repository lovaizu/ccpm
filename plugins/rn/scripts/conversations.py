"""The orchestrator's conversations with the user as Claude Code keeps them, read by lane's
record.py and found by the top of the repository and the branch: whether the user typed a command,
as an approval counts only from the user's own action, and where words were said or given to a
tool, as the learnings check each cause they doubt in them; where none is kept here, each says it
could not look, apart from finding nothing."""

from __future__ import annotations

import datetime
import glob
import json
import os
from typing import Any

import record
import repo
import stop


def entries(path: str) -> list[dict[str, Any]]:
    """The conversation's own entries of the record at the path: Claude Code also keeps a copy of
    each request it sends, which says again what was shown."""
    kept = record.read(path) or []
    return [e for e in kept if e.get("type") in ("user", "assistant", "attachment")]


def typed(command: str, start: float) -> bool:
    """Whether the user typed the command, at or after the time in seconds since 1970, in a
    conversation run at the top of the repository on the checked-out branch: an entry of the
    user's that is a command, as Claude Code keeps one typed, and names it; never an agent's
    message nor what a tool gave back, which are kept otherwise. Stops where no such conversation
    is kept, as kept says."""
    name = f"<command-name>{command}</command-name>"
    unchecked = (
        f"whether the user typed {command} could not be checked; it needs this conversation's"
        " record there, where CLAUDE_CONFIG_DIR, or ~/.claude where it names none, says Claude"
        " Code keeps it: tell the user so, and end"
    )
    for path in kept(unchecked):
        for entry in entries(path):
            text = record.text(entry) or ""
            if text.startswith("<command-") and name in text and since(entry, start):
                return True
    return False


def begun(path: str) -> tuple[str, str]:
    """When the record began, its earliest entry's time, Claude Code writing each in one form; and
    its path, so records begun at once come in one order."""
    times = [e["timestamp"] for e in entries(path) if "timestamp" in e]
    return min(times, default=""), path


def conversations(top: str, branch: str) -> list[str]:
    """The record of each conversation run at the top of the repository that was on the branch at
    some entry, in the order they began; the agents a conversation started are kept beside it, not
    among them."""
    found = [
        path
        for folder in record.folders(top)
        for path in glob.glob(os.path.join(glob.escape(folder), "*.jsonl"))
        if any(e.get("cwd") == top and e.get("gitBranch") == branch for e in entries(path))
    ]
    return sorted(found, key=begun)


def kept(unchecked: str) -> list[str]:
    """The record of each conversation run at the top of the repository on the checked-out branch,
    as conversations gives them; stops where there is none, saying where they were looked for and
    what could not be checked, which the words given say with what to do, as a look at no record
    finds nothing whatever was said."""
    top, branch = repo.top(), repo.branch()
    found = conversations(top, branch)
    if not found:
        raise stop.Stop(
            f"rn: no record of a conversation run at the top of this repository on {branch} is"
            f" under {record.projects()}, the folder Claude Code keeps them in, so {unchecked}"
        )
    return found


def since(entry: dict[str, Any], start: float) -> bool:
    """Whether the entry was kept at or after the time, in seconds since 1970; not where it has no
    time."""
    at = entry.get("timestamp")
    # Python 3.9 reads no `Z` for UTC, which Claude Code writes.
    return (
        at is not None
        and datetime.datetime.fromisoformat(at.replace("Z", "+00:00")).timestamp() >= start
    )


def given(values: Any) -> str:
    """What a tool was given, each value under its name, text as it was written, so a quote of a
    file written is found with its quotes and lines as they are; any other value as JSON."""
    if not isinstance(values, dict):
        return json.dumps(values, ensure_ascii=False)
    return "\n".join(
        f"{name}: {v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)}"
        for name, v in values.items()
    )


def said(part: dict[str, Any]) -> tuple[str, str]:
    """One part of a message: its mark, its type, and for a tool used its name; and its words, for
    a tool what it was given."""
    if part.get("type") == "tool_use":
        return f"[tool_use {part.get('name')}]", given(part.get("input"))
    return f"[{part.get('type')}]", part.get("text", "")


def parts(entry: dict[str, Any]) -> list[tuple[str, str]]:
    """Each part of the entry the user or the orchestrator said or did, as `said` gives it: the
    user's words or a skill's text, each word of the orchestrator's and each tool it called; what
    a tool gave back is left out, as the history keeps what was kept, and the orchestrator's
    thinking, which no one was shown."""
    content = record.content(entry)
    found = [(f"[{entry.get('type')}]", content)] if isinstance(content, str) else []
    return found + [said(b) for b in record.blocks(entry) if b.get("type") in ("text", "tool_use")]


def search(words: str) -> list[dict[str, Any]]:
    """Each part said or done, as `parts` gives them, whose words hold the words given, in the
    conversations of the orchestrator run at the top of the repository on the checked-out branch,
    in the order they began and each in its order: the conversation's record, the time its entry
    was kept, None where Claude Code kept none, and the part as one text, its mark first. Stops
    where no such conversation is kept, as kept says."""
    unchecked = (
        "the session's conversations could not be searched, as when it ran on another machine;"
        " tell the user a cause only they show is left unchecked, and go on without it"
    )
    return [
        {"conversation": path, "time": entry.get("timestamp"), "said": f"{mark} {text}"}
        for path in kept(unchecked)
        for entry in entries(path)
        for mark, text in parts(entry)
        if words in text
    ]
