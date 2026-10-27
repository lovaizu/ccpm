"""What the subagent did before, from its record: the JSONL file Claude Code writes of it beside the
session's record, each line an entry, among them each tool the subagent used, as the AI gave it,
what the tool gave back, each reply that ended its turn, and each message that reached the
subagent, its prompt first. A tool event carries no path to it, but the session's record and the
subagent's ID, by which Claude Code keeps it. Claude Code does not document the record, so it is
read as Claude Code 2.1.309 writes it, the one version lane's code and tests name for it, and a
line not in that shape is left out. A call is written there as two entries, its tool use and then
its result: the tool use at times before the call's PreToolUse hook runs, so the call being checked
may be there already, and the result of a call of the reply being handed at times only after the
next call's hooks have run, which is why called.py keeps each call as it comes back. So `done`
reads a call as made only once its result is there, and leaves out a call a PreToolUse hook
stopped, its result the hook's error, as it never ran. Where Claude Code keeps the records, a
conversation's beside each subagent's of it, and the agent type of each, are read here too, for
every plugin that reads a record, kept as that version keeps them."""

from __future__ import annotations

import glob
import json
import os
import re
from typing import Any, NamedTuple

# What a user entry's message begins with where a stop hook keeps the subagent going, telling it
# what the hook wrote.
TOLD = "Stop hook feedback:"
# How Claude Code puts a message the main conversation sends into the subagent's record,
# around the message itself; a message from another subagent has the message apart, as its body.
FROM_MAIN = re.compile(
    r"\AThe coordinator sent a message while you were working:\n(?P<message>.*)"
    r"\n\nAddress this before completing your current task\.\Z",
    re.DOTALL,
)
# What a call's result begins with where a PreToolUse hook stopped it, the call never run.
HOOK_STOPPED = re.compile(r"\APreToolUse:\S+ hook error: ")
# What a Bash call's result is where its command printed nothing.
SILENT = "(Bash completed with no output)"
# A reply that ended the subagent's turn, read among the tools it used as one of no tool, the reply
# its input's `text`, as it hands its text on to whoever started or resumed the subagent, as a call
# of the Agent tool or SendMessage hands on theirs.
REPLY, SAID = "", "text"
# Claude Code names the folder of a project's records by the project's path, each character that is
# not a letter or digit as `-`, counted as JavaScript counts, a character beyond the basic plane as
# two; a name longer than this is cut to it and a hash of the path put after, which is not made
# again here, so that folder is found by what goes before the hash.
NAME_LENGTH = 200
# The name of the record of a subagent, by its ID, as Claude Code names it.
SUBAGENT = "agent-{}.jsonl"


class Done(NamedTuple):
    """A tool the subagent used, or a reply that ended its turn: the tool, its input as the AI gave
    it, the folder it ran in, the text it gave back, "" for a reply or a result of no text, and
    whether it gave back an error, as a command that exits other than 0 does, or a call Claude
    Code refused."""

    tool: str
    given: dict[str, Any]
    cwd: str
    result: str
    failed: bool = False


def projects() -> str:
    """The folder Claude Code keeps each project's records in: `projects/` in the folder
    CLAUDE_CONFIG_DIR names, or in ~/.claude where it names none."""
    return os.path.join(
        os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude"), "projects"
    )


def folders(top: str) -> list[str]:
    """The folders where Claude Code keeps the records of conversations run at the path: the one
    named by it, or, where the name is longer than Claude Code keeps, each there named by its
    beginning and a hash."""
    name = "".join(
        c if c.isascii() and c.isalnum() else "-" * (len(c.encode("utf-16-le")) // 2) for c in top
    )
    if len(name) <= NAME_LENGTH:
        return [os.path.join(projects(), name)]
    found = glob.escape(name[:NAME_LENGTH]) + "-*"
    return sorted(glob.glob(os.path.join(glob.escape(projects()), found)))


def conversation(session: str = "*", folder: str = "") -> str:
    """Where the record of the conversation of the session's ID is kept, `<session>.jsonl` in its
    project's folder, any project's where no folder is given; a pattern of glob where `*` is
    given."""
    return os.path.join(folder or os.path.join(projects(), "*"), f"{session}.jsonl")


def subagent(session: str, agent: str) -> str:
    """Where the record of the subagent of the ID is kept, `<session>/subagents/agent-<id>.jsonl`
    beside the record of its conversation, `<session>.jsonl`; a pattern of glob where either is
    one."""
    return os.path.join(os.path.splitext(session)[0], "subagents", SUBAGENT.format(agent))


def agent_id(file: str) -> str:
    """The ID of the subagent whose record is kept at the path, as `subagent` names it."""
    before, _, after = SUBAGENT.partition("{}")
    return os.path.basename(file)[len(before) : -len(after)]


def agent_type(file: str) -> str:
    """The agent type of the record at the path, as its meta file beside it, `<record>.meta.json`,
    names it; "" where that file is not there or names none."""
    try:
        with open(os.path.splitext(file)[0] + ".meta.json", encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, ValueError):
        return ""
    named = meta.get("agentType") if isinstance(meta, dict) else None
    return named if isinstance(named, str) else ""


def path(event: dict[str, Any]) -> str | None:
    """Where the record of the event's subagent is, beside the session's record, the event's
    transcript_path; None where the event names no session or no subagent, as in the main
    conversation."""
    session, agent = event.get("transcript_path"), event.get("agent_id")
    if not isinstance(session, str) or not isinstance(agent, str):
        return None
    return subagent(session, agent)


def entries(event: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Each entry of the record of the event's subagent, in order, read from the file once for
    every reading of it below, as `read` reads it; None where no record is found, told apart from a
    record of no entries."""
    file = path(event)
    return None if file is None else read(file)


def read(file: str) -> list[dict[str, Any]] | None:
    """Each entry of the record at the path, in order, a line that is no JSON object left out, as
    one Claude Code is still writing; None where it is not there."""
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
    return given if isinstance(given, str) and entry.get("type") == "user" else None


def prompt(found: list[dict[str, Any]]) -> str:
    """The prompt the subagent was started with, the text of the first user entry of text among
    the entries of its record; "" where none is."""
    return next((t for t in map(text, found) if t is not None), "")


def of(entry: dict[str, Any], kind: str, block: str) -> list[dict[str, Any]]:
    """Each block of the type given in an entry of the kind given, such as an assistant entry's
    tool uses; none in an entry of another kind."""
    found = [b for b in blocks(entry) if b.get("type") == block]
    return found if entry.get("type") == kind else []


def uses(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Each tool use of an assistant entry; none for any other entry."""
    return of(entry, "assistant", "tool_use")


def told(entry: dict[str, Any]) -> bool:
    """Whether the entry is a stop hook keeping the subagent going, telling it what the hook
    wrote."""
    return (text(entry) or "").startswith(TOLD)


def ends_turn(entry: dict[str, Any]) -> bool:
    """Whether the entry is the subagent's reply ending its turn: an assistant entry whose message
    stopped at the turn's end, as Claude Code writes the last entry of a reply."""
    message = entry.get("message")
    stop = message.get("stop_reason") if isinstance(message, dict) else None
    return entry.get("type") == "assistant" and stop == "end_turn"


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
    """Each tool the subagent used, in order, from the entries of its record, as `done_at` gives
    them."""
    return [d for _, d in done_at(found, cwd)]


def done_at(found: list[dict[str, Any]], cwd: str) -> list[tuple[int, Done]]:
    """Each tool the subagent used, in order, from the entries of its record, with the number of
    the entry it was used in among them: an assistant entry's tool use, with what a user entry's
    tool result of the same id gave back, made in the folder its entry names, or the one given
    where it names none, a call whose result is not there left out, as it has not come back, and a
    call a hook stopped too, as it did nothing; and each reply that ended its turn, as a use of no
    tool, REPLY, its texts, a line each, as its input's SAID."""
    used: dict[Any, tuple[int, Any, Any, Any]] = {}
    results: dict[Any, tuple[str, bool]] = {}
    ended = replies(found)
    for number, entry in enumerate(found):
        if number in ended:
            texts = [b.get("text") for b in of(entry, "assistant", "text")]
            said = "\n".join(t for t in texts if isinstance(t, str))
            used[number] = (number, REPLY, {SAID: said}, entry.get("cwd") or cwd)
            # A reply that ended the turn is made once it is written, giving back nothing.
            results[number] = ("", False)
        for b in uses(entry):
            used[b.get("id")] = (number, b.get("name"), b.get("input"), entry.get("cwd") or cwd)
        for b in of(entry, "user", "tool_result"):
            given = b.get("content")
            said = given if isinstance(given, str) else ""
            results[b.get("tool_use_id")] = (said, b.get("is_error") is True)
    each = [
        (number, Done(tool, given, where, *results[key]))
        for key, (number, tool, given, where) in used.items()
        if isinstance(tool, str) and isinstance(given, dict) and key in results
    ]
    return [(n, d) for n, d in each if not (d.failed and HOOK_STOPPED.match(d.result))]


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
        if number in asked or any(b.get("name") == "SendMessage" for b in uses(entry)):
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
    if kind == "coordinator":
        sent = FROM_MAIN.match(said)
        return [sent["message"] if sent else said]
    body = sender.get("body") if kind == "peer" else None
    return [body] if isinstance(body, str) else []
