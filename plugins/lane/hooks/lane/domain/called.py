"""Decides what Lane keeps of a session, and how the starts of a run join one another.

Each plugin's guard keeps its own record of a session, in the system's temporary folder, at
`lane/<yyyymmdd>-<session>-<plugin>/record.jsonl`. The record holds one JSON object a line, each an
entry with a `kind`. The guard of each hook event adds an entry in one write at the file's end, so
that hooks that run at once each add a whole line.

The kinds of entry:
- `run`, with `skill`, begins a run, in place of any run before it. `end` ends it.
- `start`, with `agent`, `role`, `prompt`, and `status`, keeps an Agent call of the main
  conversation that came back.
- `skill`, with `skill`, keeps a Skill call of a dependency's skill that the routes name.
- `call`, with `agent`, `tool`, `input`, and `cwd`, keeps a tool call of a role that came back.
- `result`, with `agent`, `role`, and `result`, keeps a result. A dependency's skill gives its
  result with `agent` null.
- `message`, with `agent` and `text`, keeps a SendMessage call to a start that came back.
- `ended`, with `agent`, keeps the end of a role.
- `given`, with `role` and `text`, keeps what the routes' command printed for a start.
- `words`, with `text`, keeps a prompt of the person's while a role's point waits.
"""

from __future__ import annotations

import glob
import json
import os
import tempfile
import time
from typing import Any, NamedTuple


class Start(NamedTuple):
    """One start of a role in a run, or one move of a dependency's skill."""

    # The ID that Claude Code gave the start, or None for a dependency's skill.
    agent: str | None
    # The role, or the dependency's skill.
    role: str
    # The prompt of the Agent call that made the start.
    prompt: str
    # Whether the start still runs.
    running: bool
    # The last result that the start gave since it began, or since a message resumed it, or None.
    result: str | None


class Group(NamedTuple):
    """Starts of one role that run at once, which the routes count as one move."""

    # The role.
    role: str
    # Each start, in the order the main conversation made them.
    starts: tuple[Start, ...]


class Run(NamedTuple):
    """The run that a record keeps."""

    # The skill that the run began with.
    skill: str
    # Each group of starts, in their order.
    groups: list[Group]
    # The last text that the routes' command printed for each role, by the role's name.
    given: dict[str, str]
    # Each prompt of the person's since the last message to a start.
    words: list[str]


class Record(NamedTuple):
    """The record of a session for one plugin."""

    # The folder that holds the record.
    folder: str

    def add(self, entry: dict[str, Any]) -> None:
        """Adds the entry at the record's end, in one write."""
        line = (json.dumps(entry, ensure_ascii=False) + "\n").encode("utf-8")
        os.makedirs(self.folder, exist_ok=True)
        handle = os.open(self._path(), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            os.write(handle, line)
        finally:
            os.close(handle)

    def entries(self) -> list[dict[str, Any]]:
        """Each entry of the record, in the order the guard added them."""
        try:
            with open(self._path(), encoding="utf-8") as f:
                return [json.loads(line) for line in f if line.strip()]
        except FileNotFoundError:
            return []

    def _path(self) -> str:
        return os.path.join(self.folder, "record.jsonl")


def record(session: str, plugin: str) -> Record:
    """The record of the session for the plugin. Its folder comes with its first entry."""
    top = os.path.join(tempfile.gettempdir(), "lane")
    found = sorted(
        glob.glob(os.path.join(glob.escape(top), f"*-{glob.escape(session)}-{glob.escape(plugin)}"))
    )
    folder = (
        found[0] if found else os.path.join(top, f"{time.strftime('%Y%m%d')}-{session}-{plugin}")
    )
    return Record(folder)


def run(entries: list[dict[str, Any]]) -> Run | None:
    """The run that the entries keep, or None where no run is on."""
    begun = [i for i, e in enumerate(entries) if e["kind"] in ("run", "end")]
    if not begun or entries[begun[-1]]["kind"] == "end":
        return None
    first = begun[-1]
    since = entries[first + 1 :]
    given = {e["role"]: e["text"] for e in since if e["kind"] == "given"}
    messages = [i for i, e in enumerate(since) if e["kind"] == "message"]
    words = [
        e["text"] for e in since[messages[-1] + 1 if messages else 0 :] if e["kind"] == "words"
    ]
    return Run(entries[first]["skill"], _groups(since), given, words)


def _groups(entries: list[dict[str, Any]]) -> list[Group]:
    """The groups of starts that the entries of a run keep."""
    starts: dict[Any, dict[str, Any]] = {}
    order: list[list[Any]] = []
    early: dict[Any, dict[str, Any]] = {}
    for entry in entries:
        kind = entry["kind"]
        if kind in ("start", "skill"):
            agent = entry.get("agent")
            role = str(entry.get("role") or entry.get("skill"))
            state = {
                "role": role,
                "prompt": entry.get("prompt", ""),
                "running": True,
                "result": None,
            }
            state.update(early.pop(agent, {}) if agent else {})
            key = agent if agent else ("skill", len(order))
            starts[key] = state
            _join(order, starts, key, role)
            continue
        key = entry.get("agent")
        if key is None and kind == "result":
            key = next((k for g in reversed(order) for k in g if isinstance(k, tuple)), None)
        target = starts.get(key) if key is not None else None
        if target is None:
            target = early.setdefault(key, {})
        if kind == "result":
            target["result"] = entry["result"]
            if key is None or isinstance(key, tuple):
                target["running"] = False
        elif kind == "message":
            target["running"], target["result"] = True, None
        elif kind == "ended":
            target["running"] = False
    return [Group(starts[g[0]]["role"], tuple(_start(k, starts[k]) for k in g)) for g in order if g]


def _join(order: list[list[Any]], starts: dict[Any, dict[str, Any]], key: Any, role: str) -> None:
    """Puts the start of the key in the last group, where it joins it, or in a group of its own."""
    last = order[-1] if order else []
    if last and starts[last[0]]["role"] == role and not isinstance(key, tuple):
        failed = [k for k in last if not starts[k]["running"] and starts[k]["result"] is None]
        if failed:
            last[last.index(failed[0])] = key
            return
        if any(starts[k]["running"] for k in last):
            last.append(key)
            return
    order.append([key])


def _start(key: Any, state: dict[str, Any]) -> Start:
    agent = None if isinstance(key, tuple) else key
    return Start(agent, state["role"], state["prompt"], state["running"], state["result"])


def texts(entries: list[dict[str, Any]], agent: str) -> list[str] | None:
    """The prompt that started the agent and each message sent to it after, or None where its
    start hasn't come back yet."""
    found = None
    for entry in entries:
        if entry["kind"] == "start" and entry["agent"] == agent:
            found = [entry["prompt"]]
        elif entry["kind"] == "message" and entry.get("agent") == agent and found is not None:
            found.append(entry["text"])
    return found
