"""What the subagent did before, from its record: the JSONL file Claude Code writes of it beside the
session's record, each line an entry, among them each tool the subagent used, as the AI gave it,
what the tool gave back, each reply that ended its turn, and each message that reached the
subagent, its prompt first. A tool event carries no path to it, but the session's record and the
subagent's ID, by which Claude Code keeps it. Claude Code does not document the record, so it is
read as Claude Code 2.1.306 writes it, which the tests hold, and a line not in that shape is left
out. The calls of one reply of the AI are written there once their hooks have run, a call a hook
stopped among them, so the record holds every call of the replies before, and none of the reply
being handed."""

from __future__ import annotations

import json
import os
import re
from typing import Any, NamedTuple

# What a user entry's message begins with where a stop hook keeps the subagent going, telling it
# what the hook wrote, as Claude Code 2.1.306 writes it.
TOLD = "Stop hook feedback:"
# How Claude Code 2.1.306 puts a message the main conversation sends into the subagent's record,
# around the message itself; a message from another subagent has the message apart, as its body.
FROM_MAIN = re.compile(
    r"\AThe coordinator sent a message while you were working:\n(?P<message>.*)"
    r"\n\nAddress this before completing your current task\.\Z",
    re.DOTALL,
)
# A reply that ended the subagent's turn, read among the tools it used as one of no tool, the reply
# its input's `text`, as it hands its text on to whoever started or resumed the subagent, as a call
# of the Agent tool or SendMessage hands on theirs.
REPLY, SAID = "", "text"


class Done(NamedTuple):
    """A tool the subagent used, or a reply that ended its turn: the tool, its input as the AI gave
    it, the folder it ran in, the text it gave back, "" where none has come back, or none of text,
    and whether it gave back an error, as a command that exits other than 0 does, or a call a hook
    stopped."""

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


def entries(event: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Each entry of the record of the event's subagent, in order, read from the file once for
    every reading of it below, a line that is no JSON object left out; None where no record is
    found, told apart from a record of no entries."""
    file = path(event)
    if file is None:
        return None
    try:
        with open(file, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return None
    found = []
    for line in lines:
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict):
            found.append(entry)
    return found


def content(entry: dict[str, Any]) -> Any:
    """The content of the entry's message, a text or a list of blocks; None where it has none."""
    message = entry.get("message")
    return message.get("content") if isinstance(message, dict) else None


def blocks(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Each block of the entry's message; none where its message is not one of blocks."""
    given = content(entry)
    return [b for b in given if isinstance(b, dict)] if isinstance(given, list) else []


def text(entry: dict[str, Any]) -> str | None:
    """The text of a user entry whose message is a text, as a message brought to the subagent is;
    None for any other entry."""
    given = content(entry)
    return given if isinstance(given, str) and entry.get("type") in ("user",) else None


def of(entry: dict[str, Any], kind: str, block: str) -> list[dict[str, Any]]:
    """Each block of the type given in an entry of the kind given, such as an assistant entry's
    tool uses; none in an entry of another kind."""
    found = [b for b in blocks(entry) if b.get("type") in (block,)]
    return found if entry.get("type") in (kind,) else []


def uses(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Each tool use of an assistant entry; none for any other entry."""
    return of(entry, "assistant", "tool_use")


def told(entry: dict[str, Any]) -> bool:
    """Whether the entry is a stop hook keeping the subagent going, telling it what the hook
    wrote."""
    return (text(entry) or "").startswith(TOLD)


def ends_turn(entry: dict[str, Any]) -> bool:
    """Whether the entry is the subagent's reply ending its turn: an assistant entry whose message
    stopped at the turn's end, as Claude Code 2.1.306 writes the last entry of a reply."""
    message = entry.get("message")
    stop = message.get("stop_reason") if isinstance(message, dict) else None
    return entry.get("type") in ("assistant",) and stop in ("end_turn",)


def replies(found: list[dict[str, Any]]) -> list[int]:
    """Where each reply that ended the subagent's turn and reached whoever started or resumed it
    stands among the entries of its record; a reply a stop hook kept going, telling it something
    next, never left the subagent."""
    at: list[int] = []
    for number, entry in enumerate(found):
        if ends_turn(entry):
            at.append(number)
        elif told(entry) and at:
            at.pop()
    return at


def done(found: list[dict[str, Any]], cwd: str) -> list[Done]:
    """Each tool the subagent used, in order, from the entries of its record: an assistant entry's
    tool use, with what a user entry's tool result of the same id gave back, made in the folder its
    entry names, or the one given where it names none; and each reply that ended its turn, as a use
    of no tool, REPLY, its texts, a line each, as its input's SAID."""
    used: dict[Any, tuple[Any, Any, Any]] = {}
    results: dict[Any, tuple[str, bool]] = {}
    ended = replies(found)
    for number, entry in enumerate(found):
        if number in ended:
            texts = [b.get("text") for b in of(entry, "assistant", "text")]
            said = "\n".join(t for t in texts if isinstance(t, str))
            used[number] = (REPLY, {SAID: said}, entry.get("cwd") or cwd)
        for b in uses(entry):
            used[b.get("id")] = (b.get("name"), b.get("input"), entry.get("cwd") or cwd)
        for b in of(entry, "user", "tool_result"):
            given = b.get("content")
            said = given if isinstance(given, str) else ""
            results[b.get("tool_use_id")] = (said, b.get("is_error") is True)
    return [
        Done(tool, given, where, *results.get(key, ("", False)))
        for key, (tool, given, where) in used.items()
        if isinstance(tool, str) and isinstance(given, dict)
    ]


def answered(found: list[dict[str, Any]]) -> bool:
    """Whether, in the entries of its record, a stop hook has told the subagent something and it
    has used no tool since, answering with words alone."""
    still = False
    for entry in found:
        if told(entry):
            still = True
        elif uses(entry):
            still = False
    return still


def heard(found: list[dict[str, Any]]) -> list[str]:
    """Each message that reached the subagent since it last asked, by SendMessage or by a reply
    that ended its turn, in order, from the entries of its record: its prompt where it has not
    asked yet, and each message the main conversation or another subagent sent it, as a user entry
    of text whose origin names the sender, as one that resumes it is too."""
    messages: list[str] = []
    asked = replies(found)
    for number, entry in enumerate(found):
        if number in asked or any(b.get("name") in ("SendMessage",) for b in uses(entry)):
            messages = []
        messages.extend(message(entry))
    return messages


def message(entry: dict[str, Any]) -> list[str]:
    """The message the entry brings the subagent, alone, where it is the prompt or one sent to it;
    none otherwise."""
    said = text(entry)
    if said is None:
        return []
    origin = entry.get("origin")
    if origin is None and not entry.get("isMeta"):
        return [said]
    sender = origin if isinstance(origin, dict) else {}
    kind = sender.get("kind")
    if kind in ("coordinator",):
        sent = FROM_MAIN.match(said)
        return [sent["message"] if sent else said]
    body = sender.get("body") if kind in ("peer",) else None
    return [body] if isinstance(body, str) else []
