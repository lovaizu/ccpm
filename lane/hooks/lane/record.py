"""What the subagent did before, from its record: the JSONL file Claude Code writes of it beside the
session's record, each line an entry, among them each tool the subagent used, as the AI gave it, and
what the tool gave back. A tool event carries no path to it, but the session's record and the
subagent's ID, by which Claude Code keeps it. Claude Code does not document the record, so it is
read as Claude Code 2.1.306 writes it, which the tests hold, and a line not in that shape is left
out. The calls of one reply of the AI are written there once their hooks have run, a call a hook
stopped among them, so the record holds every call of the replies before, and none of the reply
being handed."""

from __future__ import annotations

import json
import os
from typing import Any, NamedTuple

# What a user entry's message begins with where a stop hook keeps the subagent going, telling it
# what the hook wrote, as Claude Code 2.1.306 writes it.
TOLD = "Stop hook feedback:"


class Done(NamedTuple):
    """A tool the subagent used: the tool, its input as the AI gave it, the folder it ran in, the
    text it gave back, "" where none has come back, or none of text, and whether it gave back an
    error, as a command that exits other than 0 does, or a call a hook stopped."""

    tool: str
    given: dict[str, Any]
    cwd: str
    result: str
    failed: bool = False


def path(event: dict[str, Any]) -> str | None:
    """Where the record of the event's subagent is: `<session>/subagents/agent-<id>.jsonl` beside
    the session's `<session>.jsonl`, the event's transcript_path; None where the event names no
    session or no subagent, as in the main conversation."""
    session, agent = event.get("transcript_path"), event.get("agent_id")
    if not isinstance(session, str) or not isinstance(agent, str):
        return None
    return os.path.join(os.path.splitext(session)[0], "subagents", f"agent-{agent}.jsonl")


def blocks(line: str) -> list[tuple[Any, dict[str, Any], Any]]:
    """Each block of the message of the entry on the line, with the entry's type and the folder it
    names; none where the line is not an entry with a message of blocks."""
    try:
        entry = json.loads(line)
    except ValueError:
        return []
    message = entry.get("message") if isinstance(entry, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, list):
        return []
    return [(entry.get("type"), b, entry.get("cwd")) for b in content if isinstance(b, dict)]


def lines(event: dict[str, Any]) -> list[str] | None:
    """The lines of the record of the event's subagent; None where no record is found."""
    file = path(event)
    if file is None:
        return None
    try:
        with open(file, encoding="utf-8") as f:
            return f.read().splitlines()
    except OSError:
        return None


def done(event: dict[str, Any]) -> list[Done] | None:
    """Each tool the event's subagent used before it, in order: an assistant entry's tool use, with
    what a user entry's tool result of the same id gave back; None where no record is found, told
    apart from a record of no calls."""
    found = lines(event)
    if found is None:
        return None
    uses: dict[Any, tuple[Any, Any, Any]] = {}
    results: dict[Any, tuple[str, bool]] = {}
    for line in found:
        for kind, b, cwd in blocks(line):
            if kind in ("assistant",) and b.get("type") in ("tool_use",):
                uses[b.get("id")] = (b.get("name"), b.get("input"), cwd or event["cwd"])
            elif kind in ("user",) and b.get("type") in ("tool_result",):
                content = b.get("content")
                text = content if isinstance(content, str) else ""
                results[b.get("tool_use_id")] = (text, bool(b.get("is_error")))
    return [
        Done(tool, given, cwd, *results.get(key, ("", False)))
        for key, (tool, given, cwd) in uses.items()
        if isinstance(tool, str) and isinstance(given, dict)
    ]


def told(line: str) -> bool:
    """Whether the line is the entry of a stop hook's telling: a user entry whose message is the
    text Claude Code writes for it."""
    try:
        entry = json.loads(line)
    except ValueError:
        return False
    message = entry.get("message") if isinstance(entry, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    # A content of text is held by an entry that is an object.
    return isinstance(content, str) and entry.get("type") in ("user",) and content.startswith(TOLD)


def answered(event: dict[str, Any]) -> bool:
    """Whether a stop hook has told the event's subagent something and it has used no tool since,
    answering with words alone; not where no record is found."""
    still = False
    for line in lines(event) or []:
        if told(line):
            still = True
        elif any(
            k in ("assistant",) and b.get("type") in ("tool_use",) for k, b, _ in blocks(line)
        ):
            still = False
    return still
