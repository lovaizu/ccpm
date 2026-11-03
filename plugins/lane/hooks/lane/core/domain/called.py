"""The calls kept: each call of a subagent as it came back, each result it gave, and each start and
end of its runs, kept under its agent_id in `lane/<yyyymmdd>-<session>/<agent_id>.jsonl` of the
system's temporary folder, as dev/architecture.md's Where a plugin writes its files has it for what
is used only while a plugin runs; a line of JSON each, read back for the run the subagent is in,
from its last start, as a subagent resumed keeps its ID and gives a result again."""

from __future__ import annotations

import glob
import json
import os
import re
import tempfile
import time
from typing import Any

import schema
from lanes import follow_routes
from routes import Start

# An ID Claude Code gives a session or a subagent, as it can name a file of its own in a folder.
ID = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9._-]*")
START = {"kind": "start"}
END = {"kind": "end"}
# What an Agent call gives back that is kept: its status and the ID of the subagent's run.
KEPT_BACK = ("status", "agentId")


def gave(on: str) -> dict[str, Any]:
    """The entry of a result given."""
    return {"kind": "result", "on": on}


def call(tool: str, given: dict[str, Any], back: Any = None) -> dict[str, Any]:
    """The entry of a call of the tool with the input as it came back, with what an Agent call gave
    back of its start."""
    kept = {k: back[k] for k in KEPT_BACK if k in back} if isinstance(back, dict) else None
    return {"kind": "call", "tool": tool, "input": given, **({"back": kept} if kept else {})}


def file(session: str, agent: str, made: bool) -> str:
    """The file the agent's entries are kept in: in the session's folder, the one of the day it was
    made, so a session going on past midnight keeps one, or of today where none was, made where
    `made`. Stops with ValueError where an ID could name a file elsewhere."""
    for given in (session, agent):
        if not ID.fullmatch(given):
            raise ValueError(f"{schema.shown(given)} is no ID Claude Code gives")
    top = os.path.join(tempfile.gettempdir(), "lane")
    day = "[0-9]" * 8
    found = sorted(glob.glob(os.path.join(glob.escape(top), f"{day}-{glob.escape(session)}")))
    folder = found[0] if found else os.path.join(top, time.strftime(f"%Y%m%d-{session}"))
    if made:
        os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{agent}.jsonl")


def keep(session: str, agent: str, entry: dict[str, Any]) -> None:
    """Keeps the entry under the agent's ID in the session's folder, after those before."""
    with open(file(session, agent, True), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def kept(session: str, agent: str) -> list[dict[str, Any]]:
    """The entries kept under the agent's ID, in order; none where none are. Stops with ValueError
    naming the file where a line is no entry, as an entry left unread could let a start through."""
    path = file(session, agent, False)
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return []
    entries = []
    for text in lines:
        try:
            entry = json.loads(text)
        except ValueError:
            entry = None
        if isinstance(entry, dict):
            entries.append(entry)
            continue
        shown = os.path.relpath(path, tempfile.gettempdir())
        raise ValueError(f"{shown} holds a line that is no entry")
    return entries


def this_run(session: str, agent: str) -> list[dict[str, Any]]:
    """The entries of the agent's run it is in: those from its last start."""
    entries = kept(session, agent)
    starts = [n for n, e in enumerate(entries) if e.get("kind") == "start"]
    return entries[starts[-1] :] if starts else entries


def result(session: str, agent: str) -> str | None:
    """The result the agent gave last in its run; None where it gave none."""
    given = [e["on"] for e in this_run(session, agent) if e.get("kind") == "result"]
    return given[-1] if given else None


def ended(session: str, agent: str) -> bool:
    """Whether the agent's run has ended."""
    return END in this_run(session, agent)


def starts(session: str, agent: str, named: list[str], plugin: str) -> list[Start]:
    """The orchestrator's starts of the subagents of the names, as its Agent calls came back, in
    order."""
    found = []
    for e in kept(session, agent):
        back = e.get("back")
        name = follow_routes.started(e.get("tool", ""), e.get("input", {}), named, plugin)
        if e.get("kind") == "call" and back and name:
            found.append(Start(name, back["status"], back["agentId"]))
    return found
