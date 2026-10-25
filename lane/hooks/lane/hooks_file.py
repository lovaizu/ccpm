"""How lanes are laid in a plugin's hooks/hooks.json, the layer writing it and the guard and the
layer reading it: the command of each entry lane:up writes, and the file itself.

A command first checks that lane's code can run, then runs its event's script in lane's code with
the subagent as `<plugin>:<name>`, as Claude Code gives it in the event's agent_type, and each lane
laid in it as `<step>:<lane>:<what it takes>`, the things taken joined by commas."""

from __future__ import annotations

import json
import os
import re
import shlex
from typing import Any

import hook
import lanes

# A plugin's or a subagent's name, as a hook's command carries it unquoted.
NAME = r"[A-Za-z0-9._-]+"
AGENT = re.compile(rf"{NAME}:{NAME}")
LANE = re.compile(r"(?P<step>[0-9]+):(?P<lane>[a-z_]+):(?P<takes>.*)")
# The events a call is kept on as it comes back, for every subagent lanes are laid in, as called.py
# says.
KEPT = ("PostToolUse", "PostToolUseFailure")
# The events lanes are held on, and those a call is kept on, each with its own script in lane's
# code, named after it, and what its hook exits with where lane's code cannot run: on a tool call
# STOPPED, which stops the call; at the subagent's end UNREAD, which tells the user and lets the
# subagent end, as it cannot install Python and kept going it would only be asked again; as a call
# comes back 0, as the call has run and the hook on the next call says what to install.
EVENTS = {"PreToolUse": hook.STOPPED, "SubagentStop": hook.UNREAD, **dict.fromkeys(KEPT, 0)}
# Each hook's command first checks that lane's code can run, and where it cannot, on an event of
# its subagent, read from the event's text by the shell alone, as Claude Code writes it, with or
# without a blank after the colon, says what to install and exits with its event's code; it lets
# any other event through, as its lanes act in their subagent alone.
CHECK = (
    'python3 -c "import sys; sys.exit(sys.version_info < (3, 9))" 2>/dev/null'
    ' || {{ e=; while IFS= read -r l || [ -n "$l" ]; do e="$e$l"; l=; done;'
    """ case "$e" in *'"agent_type":"{agent}"'*|*'"agent_type": "{agent}"'*)"""
    ' echo "{plugin}: install Python 3.9 or later, run as python3, for its hooks to run" >&2;'
    " exit {code};; esac; exit 0; }}"
)


def word(number: int, lane: str, takes: list[str]) -> str:
    """The lane as a hook's command gives it."""
    return f"{number}:{lane}:{','.join(takes)}"


def lane_of(w: str) -> tuple[int, str, list[str]] | None:
    """The step, the lane and what it takes, of a lane as a hook's command gives it; None where it
    is no lane of these as `word` writes it."""
    m = LANE.fullmatch(w)
    takes = m["takes"].split(",") if m else []
    if not m or m["lane"] not in lanes.LANES or not all(takes) or not lanes.fits(m["lane"], takes):
        return None
    return int(m["step"]), m["lane"], takes


def script(event: str) -> str:
    """What a hook's command runs for the event: its script in lane's code."""
    return f'exec python3 "${{CLAUDE_PLUGIN_ROOT}}/hooks/lane/{event.lower()}.py"'


def command(plugin: str, agent: str, laid: list[str], event: str) -> str:
    """The hook's command running lane's code on the lanes laid in the subagent, held on the
    event."""
    words = " ".join(shlex.quote(w) for w in [agent, *laid])
    return (
        f"{CHECK.format(plugin=plugin, agent=agent, code=EVENTS[event])}; {script(event)} {words}"
    )


def words(command: Any, event: str) -> list[str]:
    """The words a hook's command gives the event's script in lane's code, the first the subagent
    as `<plugin>:<subagent>`, each after it a lane laid; none for a command that runs no script of
    lane's, names no subagent so, or gives words the shell cannot read."""
    found = re.search(rf'/hooks/lane/{event.lower()}\.py"?(.*)', str(command))
    try:
        given = shlex.split(found[1]) if found else []
    except ValueError:
        return []
    return given if given and AGENT.fullmatch(given[0]) else []


def parsed(words: list[str], held: str) -> tuple[str, list[tuple[int, str, list[str]]]]:
    """The subagent a hook's command names and the lanes it lays in it, each held on the event
    given; stops with ValueError saying which word is not as lane:up writes it."""
    if not words or not AGENT.fullmatch(words[0]):
        raise ValueError("gives no subagent as <plugin>:<name>")
    found = []
    for w in words[1:]:
        given = lane_of(w)
        if given is None:
            raise ValueError(f"gives `{w}`, no lane as <step>:<lane>:<what it takes>")
        if held not in lanes.held_on(given[1]):
            raise ValueError(f"gives `{w}`, no lane held on {held}")
        found.append(given)
    return words[0], found


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


def taken(root: str, agent: str, lane: str) -> list[list[str]]:
    """What each lane of the kind laid in the subagent, as `<plugin>:<name>`, on a tool call takes,
    read from the hooks the plugin at root lays; none where its hooks.json is not there or not in
    Claude Code's shape. Read there, as a lane may be given in a hook apart from the one asking,
    such as one held at the subagent's end apart from start_with's."""
    try:
        hooks = read(root)
    except ValueError:
        return []
    found = []
    for c in commands(hooks, "PreToolUse"):
        try:
            named, laid_in = parsed(words(c, "PreToolUse"), "PreToolUse")
        except ValueError:
            continue
        if named == agent:
            found += [takes for _, kind, takes in laid_in if kind == lane]
    return found
