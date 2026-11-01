"""Each call a subagent with lanes made, kept by lane's hooks as it comes back, so the guard holds
the subagent to every call it made before, those of the reply being handed among them, whose
results the record may not hold yet, as record.py says: Claude Code runs each call's PostToolUse,
or PostToolUseFailure where it failed, before the next call's PreToolUse. A call a hook stopped
gets neither, as it never ran, and record.done leaves it out too.

The calls are kept one JSON line each, in the order they came back, in
`lane/<yyyymmdd>-<session>/<agent>.jsonl` in the system's temporary folder, used only while the
subagent runs, as dev/architecture.md's Where a plugin writes its files has it. What a call gave
back is kept as the text the AI is shown, in the form the record's tool result has for the same
call, as the version of Claude Code record.py names gives both; where the record and a kept call
differ, the record holds, so a kept call is read only until the record holds its result."""

from __future__ import annotations

import glob
import json
import os
import re
import tempfile
import time
from typing import Any

import call
import hook
import lanes_json
import record

# A session's or a subagent's ID as Claude Code gives it, letters, digits and hyphens, so a folder
# or a file named by it stays in the folder of the kept calls.
ID = re.compile(r"[A-Za-z0-9-]+")
# The tool a subagent may hand its report back with, the field of its input holding the report.
HANDBACK, MESSAGE = "SubagentHandback", "message"
# A line flow.py prints where it cannot tell the run: headed by the plugin's name, or lane's where
# it does not know it, and ending by telling the orchestrator to end with it.
FLOW_FAILED = re.compile(
    rf"^\S+: (?P<said>lane cannot check the flow of .*{re.escape(hook.ENDED)})$", re.MULTILINE
)


def place(event: dict[str, Any], kind: str = ".jsonl") -> str | None:
    """Where the calls of the event's subagent are kept: `<agent>.jsonl` in the folder of its
    session, the one made on the day a call of the session was first kept, so a run past midnight
    keeps one folder, or today's where none is made; its answer, given `.reply.json`, beside them;
    None where the event names no session or no subagent by an ID as Claude Code gives it, as in
    the main conversation."""
    session, agent = event.get("session_id"), event.get("agent_id")
    if not all(isinstance(i, str) and ID.fullmatch(i) for i in (session, agent)):
        return None
    top = os.path.join(tempfile.gettempdir(), "lane")
    made = sorted(glob.glob(os.path.join(glob.escape(top), f"[0-9]*-{session}")))
    folder = made[0] if made else os.path.join(top, f"{time.strftime('%Y%m%d')}-{session}")
    return os.path.join(folder, f"{agent}{kind}")


def begun(file: str) -> None:
    """Makes the file the calls of a subagent are kept in, as `place` names it, where it is not
    there, so flow.py tells a run whose calls are none yet from one whose calls are not found."""
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "a", encoding="utf-8"):
        pass


def given_back(event: dict[str, Any]) -> str:
    """The text the AI is shown of what the event's call gave back, as the record's tool result
    holds it: of a failed call its error; of a Bash call what it printed, its output then its
    errors, or the words Claude Code shows for none, record.SILENT; of a Read call each line it
    read, numbered from the first, a tab before its text; "" of any other tool, whose text no lane
    reads."""
    if failed(event):
        return event["error"]
    back = event.get("tool_response")
    back = back if isinstance(back, dict) else {}
    if event["tool_name"] == "Bash":
        printed = [back.get(k) for k in ("stdout", "stderr")]
        return "\n".join(p for p in printed if isinstance(p, str) and p) or record.SILENT
    if event["tool_name"] != "Read":
        return ""
    file = back.get("file")
    file = file if isinstance(file, dict) else {}
    content, first = file.get("content"), file.get("startLine")
    if not isinstance(content, str) or not isinstance(first, int):
        return ""
    return "\n".join(f"{first + at}\t{line}" for at, line in enumerate(content.split("\n")))


def failed(event: dict[str, Any]) -> bool:
    """Whether the event's call failed: it comes back on PostToolUseFailure, the one event of the
    two that gives an error, the text the AI is shown."""
    return "error" in event


def started(event: dict[str, Any]) -> dict[str, str]:
    """The ID of the subagent the event's call started, as `{"agent": <its ID>}`, where it is an
    Agent call Claude Code gave it back of; none otherwise."""
    back = event.get("tool_response")
    agent = back.get("agentId") if isinstance(back, dict) else None
    return {"agent": agent} if event["tool_name"] == "Agent" and isinstance(agent, str) else {}


class Kept:
    """The check lane's hooks run as a call of the subagent of the plugin at root, as
    `<plugin>:<name>`, comes back: it keeps the call, and the answer of a `from` subagent of the
    flow, and tells the user the line a run of lane's flow.py printed where it could not tell the
    run, as an error; it says nothing else."""

    def __init__(self, root: str, agent: str) -> None:
        self.root, self.agent = root, agent

    def check(self, event: dict[str, Any]) -> list[hook.Said]:
        """Keeps the event's call where `place` says, as one JSON line after those kept before:
        its ID, its tool, its input, the folder it ran in, what it gave back, whether it failed,
        and the subagent it started, as `started` gives it; where it is the subagent's call of
        SubagentHandback and the subagent is a `from` of the flow, its message as the answer kept,
        to be read as it ends; nothing where `place` names no file."""
        file = place(event)
        if file is None:
            return []
        kept = {
            "id": event["tool_use_id"],
            "tool": event["tool_name"],
            "input": event["tool_input"],
            "cwd": event["cwd"],
            "result": given_back(event),
            "failed": failed(event),
            **started(event),
        }
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "a", encoding="utf-8") as f:
            f.write(json.dumps(kept) + "\n")
        if event["tool_name"] == HANDBACK and answering(self.root, self.agent):
            message = event["tool_input"].get(MESSAGE)
            kept_as(event, message if isinstance(message, str) else "", True)
        return self.told(event)

    def told(self, event: dict[str, Any]) -> list[hook.Said]:
        """The line the event's call printed where it is a Bash run of lane's flow.py in the plugin
        that could not tell the run, without its head, as the hook heads it with the plugin's name,
        an error told the user; none for any other call."""
        command = event["tool_input"].get("command") if event["tool_name"] == "Bash" else None
        script = lanes_json.flow_script(self.root)
        if not isinstance(command, str) or not call.runs_path(command, event["cwd"], script):
            return []
        return [hook.Said(m["said"], True) for m in FLOW_FAILED.finditer(given_back(event))]


def answering(root: str, agent: str) -> bool:
    """Whether the subagent, as `<plugin>:<name>`, is a `from` of the flow the plugin at root lays;
    not where its hooks/lanes.json cannot be read, which the guard tells on the subagent's next
    call."""
    try:
        flow = lanes_json.laid(root).get("flow")
    except ValueError:
        return False
    return agent.split(":")[1] in lanes_json.froms(flow)


def kept_as(event: dict[str, Any], answer: str, handed: bool) -> None:
    """Keeps the answer of the event's subagent, in place of the one kept before, with whether it
    was handed back by SubagentHandback and not yet read as the subagent ended; nothing where
    `place` names no file."""
    file = place(event, ".reply.json")
    if file is not None:
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w", encoding="utf-8") as f:
            f.write(json.dumps({"answer": answer, "handed": handed}) + "\n")


def ended(event: dict[str, Any]) -> None:
    """Keeps the answer of the SubagentStop event's subagent as it ends: the message it handed
    back since it last ended, where it handed one, and else its last reply, "" for none."""
    held = read_answer(place(event, ".reply.json"))
    if held is not None and held[1]:
        kept_as(event, held[0], False)
    else:
        reply = event.get("last_assistant_message")
        kept_as(event, reply if isinstance(reply, str) else "", False)


def answer(session: str, agent: str) -> str | None:
    """The answer kept of the subagent of the ID in the session of the ID; None where none is kept,
    or the IDs are none as Claude Code gives them."""
    held = read_answer(place({"session_id": session, "agent_id": agent}, ".reply.json"))
    return None if held is None else held[0]


def read_answer(file: str | None) -> tuple[str, bool] | None:
    """The answer kept in the file, with whether it was handed back and not yet read as the subagent
    ended; None where there is no file, or it holds no answer in the form `kept_as` writes."""
    try:
        with open(str(file), encoding="utf-8") as f:
            held = json.load(f)
    except (OSError, ValueError):
        return None
    said = held.get("answer") if isinstance(held, dict) else None
    return None if not isinstance(said, str) else (said, bool(held.get("handed")))


def entries(event: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Each entry of the record of the event's subagent, as record.entries reads it, then each call
    kept of it whose result the record does not hold yet, by its ID, in the order kept, as the two
    entries the record would hold of it; None where no record is found."""
    found = record.entries(event)
    file = place(event)
    if found is None or file is None:
        return found
    held = {b.get("tool_use_id") for e in found for b in record.of(e, "user", "tool_result")}
    kept = [k for k in record.read(file) or [] if k.get("id") not in held]
    return [*found, *(e for k in kept for e in as_entries(k))]


def as_entries(kept: dict[str, Any]) -> list[dict[str, Any]]:
    """A kept call as the record holds it: an assistant entry of its tool use, made in its folder,
    and a user entry of its tool result."""
    use = {"type": "tool_use", "id": kept.get("id"), "name": kept.get("tool")}
    back = {"type": "tool_result", "tool_use_id": kept.get("id"), "content": kept.get("result")}
    return [
        {
            "type": "assistant",
            "cwd": kept.get("cwd"),
            "message": {"content": [{**use, "input": kept.get("input")}]},
        },
        {"type": "user", "message": {"content": [{**back, "is_error": kept.get("failed")}]}},
    ]
