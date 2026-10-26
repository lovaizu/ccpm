"""The entries the layer writes in a plugin's hooks/hooks.json, one for each subagent and each event
its lanes are held on, and each event a call is kept on, every other entry left as it was, and that
file read; and the lanes laid, read back from hooks/lanes.json or, where an older lane laid them,
from the words of its hooks' commands.

A command first checks that lane's code can run, then runs its event's script in lane's code with
the subagent as `<plugin>:<name>`, as Claude Code gives it in the event's agent_type; the guard
reads that subagent's lanes from hooks/lanes.json."""

from __future__ import annotations

import json
import os
import re
import shlex
from typing import Any

import hook
import lanes
import lanes_json
import placed
import step
from proposal import Stop

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
    return given if given and hook.AGENT.fullmatch(given[0]) else []


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


# A lane as an older lane's hook command gave it, `<step>:<lane>:<what it takes>`, the things taken
# joined by commas; read here alone, as lane's hooks give the guard the subagent alone now.
WORD = re.compile(r"(?P<step>[0-9]+):(?P<lane>[a-z_]+):(?P<takes>.*)")


def entry(plugin: str, agent: dict[str, Any], event: str) -> dict[str, Any] | None:
    """The subagent's entry of hooks.json for the event, None where none of its lanes is held on
    it: its matcher the tools its lanes watch, or for SubagentStop the subagent, as its matcher
    tells agents apart; for an event a call is kept on, where it has any lane, an entry matching
    every tool; each command giving the subagent alone, whose lanes the guard reads from
    hooks/lanes.json."""
    every = [(s["step"], g) for s in agent["steps"] for g in s["lanes"]]
    kept = event in KEPT
    on_it = [(n, g) for n, g in every if event in lanes.held_on(g["lane"])]
    if not (every if kept else on_it):
        return None
    name = f"{plugin}:{agent['name']}"
    each = [t for _, g in on_it for t in getattr(lanes.LANES[g["lane"]], "TOOLS", ())]
    ending = event == "SubagentStop"  # pragma: no mutate
    tools = [name] if ending else [".*"] if kept else each
    run_it = command(plugin, name, event)
    return {
        "matcher": "|".join(dict.fromkeys(tools)),
        "hooks": [{"type": "command", "timeout": hook.TIMEOUT, "command": run_it}],
    }


def hooks_read(root: str) -> dict[str, Any]:
    """The plugin's hooks.json, an empty one where there is none; stops where it is not in Claude
    Code's shape."""
    try:
        return read(root)
    except ValueError as why:
        path = os.path.join(root, "hooks", "hooks.json")
        raise Stop(f"lay.py: {path} {why}; fix it and run again.") from None


def hooks_with(hooks: dict[str, Any], plugin: str, agent: dict[str, Any]) -> None:
    """Puts the subagent's entry of each event its lanes are held on into the hooks: where the layer
    wrote one for it before, in the place of the first, after every other entry otherwise; and
    takes out those the layer wrote for it before on an event none of its lanes is held on now."""
    events = hooks.setdefault("hooks", {})
    for event in EVENTS:
        entries = events.get(event, [])
        mark = [f"{plugin}:{agent['name']}"]
        ours = [
            any(words(h.get("command"), event)[:1] == mark for h in e.get("hooks", []))
            for e in entries
        ]
        place = ours.index(True) if True in ours else len(entries)
        others = [e for e, our in zip(entries, ours) if not our]
        new = entry(plugin, agent, event)
        kept = [*others[:place], *([new] if new else []), *others[place:]]
        # An event the hooks hold no entry of is left out, not written as an empty list.
        if kept or entries:
            events[event] = kept


def gone_out(hooks: dict[str, Any], plugin: str, root: str) -> list[str]:
    """Takes out of the hooks the entries the layer wrote for a subagent the plugin's agents/ no
    longer has, as there is no subagent left for its lanes to act in; gives each subagent taken
    out, said."""
    ours = f"{plugin}:"
    gone = []
    for event in EVENTS:
        entries = hooks["hooks"].get(event, [])
        kept = []
        for e in entries:
            firsts = [words(h.get("command"), event)[:1] for h in e.get("hooks", [])]
            names = [w[len(ours) :] for [w] in filter(None, firsts) if w.startswith(ours)]
            lost = [n for n in names if step.agent_file(root, n) is None]
            gone += lost
            if not lost:
                kept.append(e)
        if entries:
            hooks["hooks"][event] = kept
    return [
        f"Took out the hooks of {n}, which agents/ no longer has.\n" for n in dict.fromkeys(gone)
    ]


def hooks_written(root: str, hooks: dict[str, Any]) -> None:
    """Writes the hooks into the plugin's hooks/hooks.json, indented by two, as Claude Code reads
    them."""
    os.makedirs(os.path.join(root, "hooks"), exist_ok=True)
    with open(os.path.join(root, "hooks", "hooks.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(hooks, indent=2, ensure_ascii=False) + "\n")


def values_before(root: str, plugin: str) -> dict[str, str | None]:
    """The adapter of the values port each subagent of the plugin at root names, by
    `<plugin>:<name>`, as its hooks/lanes.json holds it; none where it is not there or cannot be
    read, as laid_before then stops."""
    try:
        found = lanes_json.laid(root)["subagents"]
    except ValueError:
        return {}
    return {f"{plugin}:{a['name']}": a.get("adapter") for a in found}


def word_of(w: str) -> tuple[int, str, list[str]] | None:
    """The step, the lane and what it takes, of a lane as an older lane's hook command gave it;
    None where it is no lane of these as lane lays them now."""
    m = WORD.fullmatch(w)
    takes = m["takes"].split(",") if m else []
    if not m or m["lane"] not in lanes.LANES or not all(takes) or not lanes.fits(m["lane"], takes):
        return None
    return int(m["step"]), m["lane"], takes


def laid_before(
    root: str, plugin: str, hooks: dict[str, Any]
) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    """Each subagent the plugin at root lays lanes in, as `<plugin>:<subagent>`, with its lanes as
    steps of a proposal, each step and each lane once: those its hooks/lanes.json holds, and those
    an older lane gave in the words of its hooks' commands, though held on both events; and each
    lane laid so that lane does not lay now, as said for the building AI to weigh. Stops where
    hooks/lanes.json is there and cannot be read, as the lanes approved would be lost."""
    agents: dict[str, list[dict[str, Any]]] = {}
    if os.path.exists(os.path.join(root, "hooks", "lanes.json")):
        try:
            found = lanes_json.laid(root)
        except ValueError as why:
            raise Stop(f"lay.py: {root}/{why}; fix it and run again.") from None
        for a in found["subagents"]:
            agents[f"{plugin}:{a['name']}"] = a["steps"]
    left = []
    for event in EVENTS:
        for e in hooks.get("hooks", {}).get(event, []):
            for h in e.get("hooks", []):
                given = words(h.get("command"), event)
                steps = agents.setdefault(given[0], []) if given[1:] else []
                for w in given[1:]:
                    lane = word_of(w)
                    if lane is None:
                        name = given[0].split(":")[1]
                        version = placed.lane_version()
                        left.append(
                            f"Left out `{w}` from the hook of {name}, as lane {version} lays no"
                            " such lane; propose a lane of docs/lanes.md that keeps its step, or"
                            " leave it out.\n"
                        )
                        continue
                    number, kind, takes = lane
                    put(steps, number, {"lane": kind, "takes": takes})
    return agents, list(dict.fromkeys(left))


def put(steps: list[dict[str, Any]], number: int, lane: dict[str, Any]) -> None:
    """Puts the lane on the step of the number among the steps, once, the step put after the others
    where it is not among them."""
    by_number = {s["step"]: s for s in steps}
    if number not in by_number:
        steps.append({"step": number, "lanes": [lane]})
    elif lane not in by_number[number]["lanes"]:
        by_number[number]["lanes"].append(lane)
