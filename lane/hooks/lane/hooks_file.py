"""How lanes are laid in a plugin, the layer writing it and the guard and the layer reading it: the
command of each entry lane:up writes in the plugin's hooks/hooks.json, and that file read; and the
lanes laid, kept in its hooks/lanes.json in the shape of the proposal, read.

A command first checks that lane's code can run, then runs its event's script in lane's code with
the subagent as `<plugin>:<name>`, as Claude Code gives it in the event's agent_type; the guard
reads that subagent's lanes from hooks/lanes.json, so what was approved is what is read, and a thing
taken holds any text, a comma among the rest."""

from __future__ import annotations

import json
import os
import re
import shlex
from typing import Any

import hook
import lanes
import schema

# A plugin's or a subagent's name, as a hook's command carries it unquoted.
NAME = r"[A-Za-z0-9._-]+"
AGENT = re.compile(rf"{NAME}:{NAME}")
# The lanes laid in a plugin, as hooks/lanes.json holds them: each subagent by its name, with each
# step its lanes are laid on, by its number, and each lane, its name and what it takes.
LANE = {
    "type": "object",
    "required": ["lane", "takes"],
    "additionalProperties": False,
    "properties": {
        "lane": {"enum": list(lanes.LANES)},
        "takes": {"type": "array", "items": {"type": "string"}},
    },
}
STEP = {
    "type": "object",
    "required": ["step", "lanes"],
    "additionalProperties": False,
    "properties": {"step": {"type": "integer"}, "lanes": {"type": "array", "items": LANE}},
}
SUBAGENT = {
    "type": "object",
    "required": ["name", "steps"],
    "additionalProperties": False,
    "properties": {"name": {"type": "string"}, "steps": {"type": "array", "items": STEP}},
}
LAID = {
    "type": "object",
    "required": ["subagents"],
    "additionalProperties": False,
    "properties": {"subagents": {"type": "array", "items": SUBAGENT}},
}
# The events a call is kept on as it comes back, for every subagent lanes are laid in, as called.py
# says.
KEPT = ("PostToolUse", "PostToolUseFailure")
# The events lanes are held on, and those a call is kept on, each with its own script in lane's
# code, named after it.
EVENTS = ("PreToolUse", "SubagentStop", *KEPT)
# What a hook says where lane's code cannot run.
INSTALL = "{plugin}: install Python 3.9 or later, run as python3, for its hooks to run"
# Each hook's command first checks that lane's code can run. Where it cannot, a hook of an event
# lanes are held on, on an event of its subagent, read from the event's text by the shell alone, as
# Claude Code writes it, with or without a blank after the colon, answers as `missing` gives it; it
# lets any other event through, as its lanes act in their subagent alone. A hook of an event a call
# is kept on lets every event through.
PYTHON = 'python3 -c "import sys; sys.exit(sys.version_info < (3, 9))" 2>/dev/null'
CHECK = (
    PYTHON + ' || {{ e=; while IFS= read -r l || [ -n "$l" ]; do e="$e$l"; l=; done;'
    """ case "$e" in *'"agent_type":"{agent}"'*|*'"agent_type": "{agent}"'*)"""
    " echo {answer};; esac; exit 0; }}"
)


def missing(plugin: str, event: str) -> dict[str, Any]:
    """What a hook of the event answers where lane's code cannot run: on a tool call the call
    denied, telling the subagent what to install, as letting it through would leave it unkept with
    no one told; at the subagent's end the user told so, letting it end, as it cannot install
    Python and kept going it would only be asked again; as a call comes back nothing, as the call
    has run and the hook on the next call says what to install."""
    said = INSTALL.format(plugin=plugin)
    if event in KEPT:
        return {}
    on_call = event == "PreToolUse"  # pragma: no mutate
    return hook.answer(event, said if on_call else "", "" if on_call else said)


def script(event: str) -> str:
    """What a hook's command runs for the event: its script in lane's code."""
    return f'exec python3 "${{CLAUDE_PLUGIN_ROOT}}/hooks/lane/{event.lower()}.py"'


def command(plugin: str, agent: str, event: str) -> str:
    """The hook's command running lane's code on the lanes laid in the subagent, held on the
    event."""
    answer = shlex.quote(json.dumps(missing(plugin, event)))
    check = f"{PYTHON} || exit 0" if event in KEPT else CHECK.format(agent=agent, answer=answer)
    return f"{check}; {script(event)} {agent}"


def words(command: Any, event: str) -> list[str]:
    """The words a hook's command gives the event's script in lane's code, the first the subagent
    as `<plugin>:<subagent>`, each after it a lane laid, where an older lane wrote them; none for a
    command that runs no script of lane's, names no subagent so, or gives words the shell cannot
    read."""
    found = re.search(rf'/hooks/lane/{event.lower()}\.py"?(.*)', str(command))
    try:
        given = shlex.split(found[1]) if found else []
    except ValueError:
        return []
    return given if given and AGENT.fullmatch(given[0]) else []


def read(root: str) -> dict[str, Any]:
    """The hooks.json of the plugin at root, an empty one where there is none; stops with
    ValueError saying so where it holds no JSON or is not in Claude Code's shape, an object whose
    hooks hold, for each event lanes are held on, a list of entries whose hooks are a list of
    objects."""
    path = os.path.join(root, "hooks", "hooks.json")
    if not os.path.exists(path):
        return {"hooks": {}}
    try:
        with open(path, encoding="utf-8") as f:
            hooks = json.load(f)
    except ValueError:
        raise ValueError("is not in the shape Claude Code reads") from None
    events = hooks.get("hooks", {}) if isinstance(hooks, dict) else None
    each = [events.get(e, []) for e in EVENTS] if isinstance(events, dict) else None
    if each is None or not all(isinstance(e, list) and all(map(shaped, e)) for e in each):
        raise ValueError("is not in the shape Claude Code reads")
    return hooks


def shaped(entry: Any) -> bool:
    """Whether an entry of hooks.json is an object whose hooks are a list of objects."""
    each = entry.get("hooks", []) if isinstance(entry, dict) else None
    return isinstance(each, list) and all(isinstance(h, dict) for h in each)


def commands(hooks: dict[str, Any], event: str) -> list[Any]:
    """The command of each hook of the event's entries, as the hooks read hold it."""
    return [h.get("command") for e in hooks["hooks"].get(event, []) for h in e.get("hooks", [])]


def laid(root: str) -> dict[str, Any]:
    """The lanes laid in the plugin at root, as its hooks/lanes.json holds them; stops with
    ValueError saying what is wrong where it is not there, holds no JSON, is not in the shape LAID
    gives, or lays a lane taking an empty thing, or another count of things than the lane holds."""
    path = os.path.join(root, "hooks", "lanes.json")
    try:
        with open(path, encoding="utf-8") as f:
            given = json.load(f)
    except OSError:
        raise ValueError("hooks/lanes.json is not there") from None
    except ValueError:
        raise ValueError("hooks/lanes.json holds no JSON") from None
    out = schema.held(LAID, given)
    if out is not None:
        raise ValueError(f"hooks/lanes.json is out of its shape at {out.told()}")
    for agent in given["subagents"]:
        for s in agent["steps"]:
            for lane in s["lanes"]:
                if not all(lane["takes"]) or not lanes.fits(lane["lane"], lane["takes"]):
                    raise ValueError(
                        f"hooks/lanes.json gives {lane['lane']} on step {s['step']} of"
                        f" {agent['name']} takes of another count than it holds, or one empty"
                    )
    return given


def laid_in(root: str, name: str) -> list[tuple[int, str, list[str]]]:
    """Each lane laid in the subagent of the name, its step, the lane and what it takes, as the
    plugin at root's hooks/lanes.json holds them; stops with ValueError, as `laid` does, or where
    the file lays no lanes in the subagent."""
    found = [a for a in laid(root)["subagents"] if a["name"] == name]
    if not found:
        raise ValueError(f"hooks/lanes.json lays no lanes in {name}")
    return [(int(s["step"]), g["lane"], g["takes"]) for s in found[0]["steps"] for g in s["lanes"]]


def taken(root: str, name: str, lane: str) -> list[list[str]]:
    """What each lane of the kind laid in the subagent of the name takes, read from the lanes the
    plugin at root lays; none where its hooks/lanes.json cannot be read so. Read there, as a lane
    may be held on an event apart from the one asking, such as one held at the subagent's end apart
    from start_with's."""
    try:
        each = laid_in(root, name)
    except ValueError:
        return []
    return [takes for _, kind, takes in each if kind == lane]
