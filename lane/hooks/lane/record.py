"""What the subagent did before, from its record: the JSONL file Claude Code writes of it beside the
session's record, each line an entry, among them each tool the subagent used, as the AI gave it,
what the tool gave back, and each message that reached the subagent, its prompt first. A tool event
carries no path to it, but the session's record and the subagent's ID, by which Claude Code keeps
it. Claude Code does not document the record, so it is read as Claude Code 2.1.306 writes it, which
the tests hold, and a line not in that shape is left out. The calls of one reply of the AI are
written there once their hooks have run, a call a hook stopped among them, so the record holds
every call of the replies before, and none of the reply being handed."""

from __future__ import annotations

import json
import os
import re
from typing import Any, NamedTuple


class Done(NamedTuple):
    """A tool the subagent used: the tool, its input as the AI gave it, the folder it ran in, the
    text it gave back, "" where none has come back, or none of text, and whether it failed, as a
    command that exits other than 0 does."""

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


def done(event: dict[str, Any]) -> list[Done] | None:
    """Each tool the event's subagent used before it, in order: an assistant entry's tool use, with
    what a user entry's tool result of the same id gave back; None where no record is found, told
    apart from a record of no calls."""
    file = path(event)
    if file is None:
        return None
    try:
        with open(file, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return None
    uses: dict[Any, tuple[Any, Any, Any]] = {}
    results: dict[Any, str] = {}
    failed: set[Any] = set()
    for line in lines:
        for kind, b, cwd in blocks(line):
            if kind in ("assistant",) and b.get("type") in ("tool_use",):
                uses[b.get("id")] = (b.get("name"), b.get("input"), cwd or event["cwd"])
            elif kind in ("user",) and b.get("type") in ("tool_result",):
                content = b.get("content")
                results[b.get("tool_use_id")] = content if isinstance(content, str) else ""
                if b.get("is_error") is True:
                    failed.add(b.get("tool_use_id"))
    return [
        Done(tool, given, cwd, results.get(key, ""), key in failed)
        for key, (tool, given, cwd) in uses.items()
        if isinstance(tool, str) and isinstance(given, dict)
    ]


# How Claude Code 2.1.306 puts a message the main conversation sends into the subagent's record,
# around the message itself; a message from another subagent has the message apart, as its body.
FROM_MAIN = re.compile(
    r"\AThe coordinator sent a message while you were working:\n(?P<message>.*)"
    r"\n\nAddress this before completing your current task\.\Z",
    re.DOTALL,
)


def heard(event: dict[str, Any]) -> list[str] | None:
    """Each message that reached the event's subagent since it last asked, by SendMessage, in
    order: its prompt where it has not asked yet, and each message the main conversation or another
    subagent sent it, as a user entry of text whose origin names the sender; None where no record is
    found."""
    file = path(event)
    if file is None:
        return None
    try:
        with open(file, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return None
    found: list[str] = []
    for line in lines:
        if any(
            b.get("name") in ("SendMessage",)
            for kind, b, _ in blocks(line)
            if kind in ("assistant",)
        ):
            found = []
        found.extend(message(line))
    return found


def message(line: str) -> list[str]:
    """The message the entry on the line brings the subagent, alone, where it is the prompt or one
    sent to it; none otherwise."""
    try:
        entry = json.loads(line)
    except ValueError:
        return []
    given = entry.get("message") if isinstance(entry, dict) else None
    text = given.get("content") if isinstance(given, dict) else None
    if not isinstance(text, str) or entry.get("type") not in ("user",):
        return []
    origin = entry.get("origin")
    kind = origin.get("kind") if isinstance(origin, dict) else None
    if origin is None and not entry.get("isMeta"):
        return [text]
    if kind in ("coordinator",):
        sent = FROM_MAIN.match(text)
        return [sent["message"] if sent else text]
    body = origin.get("body") if kind in ("peer",) else None
    return [body] if isinstance(body, str) else []
