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
differ, the record holds, so a kept call is read only until the record holds its result. Of an
Agent call it keeps too the status Claude Code gives back and the answer of the subagent it started,
which the flow's moves are read from, as moves.py reads them; and the orchestrator of a flow is told
its move due as it starts and as each call of a subagent of the flow comes back."""

from __future__ import annotations

import glob
import json
import os
import re
import tempfile
import time
from typing import Any

import hook
import lanes_json
import moves
import record

# A session's or a subagent's ID as Claude Code gives it, letters, digits and hyphens, so a folder
# or a file named by it stays in the folder of the kept calls.
ID = re.compile(r"[A-Za-z0-9-]+")
# The tool a subagent may hand its report back with, the field of its input holding the report.
HANDBACK, MESSAGE = "SubagentHandback", "message"


def place(event: dict[str, Any]) -> str | None:
    """Where the calls of the event's subagent are kept: `<agent>.jsonl` in the folder of its
    session, the one made on the day a call of the session was first kept, so a run past midnight
    keeps one folder, or today's where none is made; None where the event names no session or no
    subagent by an ID as Claude Code gives it, as in the main conversation."""
    session, agent = event.get("session_id"), event.get("agent_id")
    if not all(isinstance(i, str) and ID.fullmatch(i) for i in (session, agent)):
        return None
    top = os.path.join(tempfile.gettempdir(), "lane")
    made = sorted(glob.glob(os.path.join(glob.escape(top), f"[0-9]*-{session}")))
    folder = made[0] if made else os.path.join(top, f"{time.strftime('%Y%m%d')}-{session}")
    return os.path.join(folder, f"{agent}.jsonl")


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


def started(event: dict[str, Any]) -> dict[str, Any]:
    """Of an Agent call, what it gave back of the subagent it started: the status Claude Code gives,
    None for none, and its answer: the last report the subagent handed back with SubagentHandback,
    kept among its calls by its ID in the event's session, where it made one, as the call then gives
    back a note in its place, and else the subagent's final text, each text block on a line; none of
    any other tool's call."""
    if event["tool_name"] != moves.AGENT:
        return {}
    back = event.get("tool_response")
    back = back if isinstance(back, dict) else {}
    status = back.get("status")
    blocks = back.get("content")
    texts = (
        [b.get("text") for b in blocks if isinstance(b, dict)] if isinstance(blocks, list) else []
    )
    answer = "\n".join(t for t in texts if isinstance(t, str))
    by = {"session_id": event.get("session_id"), "agent_id": back.get("agentId")}
    handed = [
        k["input"][MESSAGE]
        for k in calls_kept(by)
        if k.get("tool") == HANDBACK
        and isinstance(k.get("input"), dict)
        and isinstance(k["input"].get(MESSAGE), str)
    ]
    return {
        "status": status if isinstance(status, str) else None,
        "answer": (handed or [answer])[-1],
    }


class Kept:
    """The check lane's hooks run as a call of the subagent of the plugin at root, as
    `<plugin>:<name>`, comes back: it keeps the call, and tells the orchestrator of the flow its
    move due as a call of a subagent of the flow comes back; it says nothing else."""

    def __init__(self, root: str, agent: str) -> None:
        self.root, self.agent = root, agent

    def check(self, event: dict[str, Any]) -> list[hook.Said]:
        """Keeps the event's call where `place` says, as one JSON line after those kept before:
        its ID, its tool, its input, the folder it ran in, what it gave back, whether it failed,
        and, of an Agent call, what `started` gives; then, where the subagent is the orchestrator
        of the flow and the call starts a subagent the flow names, the move due, as moves.told
        gives it; nothing where `place` names no file."""
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
        flow = flow_run(self.root, self.agent, event)
        if flow is None:
            return []
        names = [f"{flow.plugin}:{n}" for n in flow.flow["order"]]
        of_flow = kept["tool"] == moves.AGENT and event["tool_input"].get(moves.TYPE) in names
        return [hook.Said(moves.told(flow))] if of_flow else []


class Started:
    """The check lane's hooks run as the subagent of the plugin at root, as `<plugin>:<name>`,
    starts: where it is the orchestrator of the flow, it tells it the move due, as moves.told gives
    it, from the calls kept of it, none where it is new, more where it is started again."""

    def __init__(self, root: str, agent: str) -> None:
        self.root, self.agent = root, agent

    def check(self, event: dict[str, Any]) -> list[hook.Said]:
        """The move due, told the orchestrator of the flow; nothing for any other subagent."""
        flow = flow_run(self.root, self.agent, event)
        return [] if flow is None else [hook.Said(moves.told(flow))]


def calls_kept(event: dict[str, Any]) -> list[dict[str, Any]]:
    """The calls kept of the event's subagent, in the order they came back; none where none came
    back yet, or `place` names no file."""
    file = place(event)
    return (record.read(file) if file is not None else None) or []


def flow_run(root: str, agent: str, event: dict[str, Any]) -> moves.Run | None:
    """The run of the flow the plugin at root lays, where the subagent, as `<plugin>:<name>`, is its
    orchestrator, its calls kept read where `place` names them for the event; None where it is not,
    the plugin lays no flow, or its hooks/lanes.json cannot be read, which the guard tells on the
    subagent's next call."""
    plugin, name = agent.split(":")
    try:
        flow = lanes_json.laid(root).get("flow")
    except ValueError:
        return None
    if flow is None or flow["orchestrator"] != name:
        return None
    return moves.Run(flow, plugin, calls_kept(event))


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
