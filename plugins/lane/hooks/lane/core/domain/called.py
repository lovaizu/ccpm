"""The calls kept: each call of a subagent as it came back, each result it gave, each start and end
of its runs, and the texts it was given, its prompt and each message sent after, kept under its
agent_id in `lane/<yyyymmdd>-<session>/<agent_id>.jsonl` of the system's temporary folder, as
dev/plugin-best-practice.md's Where a plugin writes its files has it for what is used only while a
plugin runs; a line of JSON each, read back for the run the subagent is in, from its last start, as
a subagent resumed keeps its ID and gives a result again."""

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


def call(tool: str, given: dict[str, Any], back: Any = None, joined: str = "") -> dict[str, Any]:
    """The entry of a call of the tool with the input as it came back, with what an Agent call gave
    back of its start, and how that start is joined to those before it, where it is."""
    kept = {k: back[k] for k in KEPT_BACK if k in back} if isinstance(back, dict) else None
    entry = {"kind": "call", "tool": tool, "input": given, **({"back": kept} if kept else {})}
    return {**entry, **({"joined": joined} if joined else {})}


def file(session: str, agent: str, made: bool) -> str:
    """The file the agent's entries are kept in: in the session's folder, the one of the day it was
    made, so a session going on past midnight keeps one, or of today where none was, made where
    `made`. Stops with ValueError where an ID could name a file elsewhere."""
    if not ID.fullmatch(agent):
        raise ValueError(f"{schema.shown(agent)} is no ID Claude Code gives")
    return os.path.join(folder(session, made), f"{agent}.jsonl")


def folder(session: str, made: bool) -> str:
    """The session's folder of the calls kept, as `file` says. Stops with ValueError where the ID
    could name a folder elsewhere."""
    if not ID.fullmatch(session):
        raise ValueError(f"{schema.shown(session)} is no ID Claude Code gives")
    top = os.path.join(tempfile.gettempdir(), "lane")
    day = "[0-9]" * 8
    found = sorted(glob.glob(os.path.join(glob.escape(top), f"{day}-{glob.escape(session)}")))
    place = found[0] if found else os.path.join(top, time.strftime(f"%Y%m%d-{session}"))
    if made:
        os.makedirs(place, exist_ok=True)
    return place


def keep(session: str, agent: str, entry: dict[str, Any]) -> None:
    """Keeps the entry under the agent's ID in the session's folder, after those before."""
    written(file(session, agent, True), entry)


def written(path: str, entry: dict[str, Any]) -> None:
    """Writes the entry at the end of the file at the path, a line of JSON."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def kept(session: str, agent: str) -> list[dict[str, Any]]:
    """The entries kept under the agent's ID, in order; none where none are. Stops with ValueError
    naming the file where a line is no entry, as an entry left unread could let a start through."""
    return read(file(session, agent, False))


def read(path: str) -> list[dict[str, Any]]:
    """The entries of the file at the path, as `kept` reads them."""
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


def left_without_result(session: str, agent: str) -> bool:
    """Whether a run of the agent ended with no result: its entries from a start to an end hold no
    result, in any of its runs."""
    gave = False
    for e in kept(session, agent):
        kind = e.get("kind")
        if kind == "start":
            gave = False
        gave = gave or kind == "result"
        if kind == "end" and not gave:
            return True
    return False


def ended(session: str, agent: str) -> bool:
    """Whether the agent's run has ended."""
    return END in this_run(session, agent)


def starts(session: str, agent: str, named: list[str], plugin: str) -> list[Start]:
    """The orchestrator's starts of the subagents of the names, as its Agent calls came back, in
    order, each with how it is joined to those before it."""
    found = []
    for e in kept(session, agent):
        back = e.get("back")
        name = follow_routes.started(e.get("tool", ""), e.get("input", {}), named, plugin)
        if e.get("kind") == "call" and back and name:
            found.append(Start(name, back["status"], back["agentId"], e.get("joined", "")))
    return found


def calls(session: str, agent: str, run: bool = False) -> list[dict[str, Any]]:
    """The agent's calls kept, as each came back, of all its runs, or of the run it is in where
    `run`."""
    entries = this_run(session, agent) if run else kept(session, agent)
    return [e for e in entries if e.get("kind") == "call"]


def given(text: str) -> dict[str, Any]:
    """The entry of the prompt a run was given, as the Agent call that started it came back with
    the run's ID."""
    return {"kind": "given", "text": text}


def message(text: str) -> dict[str, Any]:
    """The entry of a message sent to a run."""
    return {"kind": "message", "text": text}


def texts(session: str, agent: str) -> list[str] | None:
    """The texts the agent's run was given, in the order they were sent: its prompt, kept once as
    the Agent call that started it came back, and each message sent to it after; None where no
    prompt is kept yet, as a run starts before that call comes back with its ID."""
    entries = kept(session, agent)
    prompt = next((e["text"] for e in entries if e.get("kind") == "given"), None)
    if prompt is None:
        return None
    sent = [e["text"] for e in entries if e.get("kind") == "message"]
    return [prompt, *sent]
