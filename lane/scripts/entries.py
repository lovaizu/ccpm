"""The entries lane:up writes in a plugin's hooks/hooks.json, one for each subagent and each event
its lanes are held on, every other entry left as it was."""

from __future__ import annotations

import json
import os
from typing import Any

import hooks_file
import lanes
import placed
import step
from proposal import Stop


def entry(plugin: str, agent: dict[str, Any], event: str) -> dict[str, Any] | None:
    """The subagent's entry of hooks.json for the event, None where none of its lanes is held on
    it: its matcher the tools its lanes watch, or for SubagentStop the subagent, as its matcher
    tells agents apart, and its command giving each lane laid."""
    every = [(s["step"], g) for s in agent["steps"] for g in s["lanes"]]
    on_it = [(n, g) for n, g in every if event in lanes.held_on(g["lane"])]
    if not on_it:
        return None
    name = f"{plugin}:{agent['name']}"
    laid = [hooks_file.word(n, g["lane"], g["takes"]) for n, g in on_it]
    each = [t for _, g in on_it for t in getattr(lanes.LANES[g["lane"]], "TOOLS", ())]
    tools = [name] if event == "SubagentStop" else each  # pragma: no mutate
    run_it = hooks_file.command(plugin, name, laid, event)
    return {
        "matcher": "|".join(dict.fromkeys(tools)),
        "hooks": [{"type": "command", "timeout": 10, "command": run_it}],
    }


def hooks_read(root: str) -> dict[str, Any]:
    """The plugin's hooks.json, an empty one where there is none; stops where it is not in Claude
    Code's shape."""
    try:
        return hooks_file.read(root)
    except ValueError as why:
        path = os.path.join(root, "hooks", "hooks.json")
        raise Stop(f"lay.py: {path} {why}; fix it and run again.") from None


def hooks_with(hooks: dict[str, Any], plugin: str, agent: dict[str, Any]) -> None:
    """Puts the subagent's entry of each event its lanes are held on into the hooks: where lane:up
    wrote one for it before, in the place of the first, after every other entry otherwise; and
    takes out those lane:up wrote for it before on an event none of its lanes is held on now."""
    events = hooks.setdefault("hooks", {})
    for event in hooks_file.EVENTS:
        entries = events.get(event, [])
        mark = [f"{plugin}:{agent['name']}"]
        ours = [
            any(hooks_file.words(h.get("command"), event)[:1] == mark for h in e.get("hooks", []))
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
    """Takes out of the hooks the entries lane:up wrote for a subagent the plugin's agents/ no
    longer has, as there is no subagent left for its lanes to act in; gives each subagent taken
    out, said."""
    ours = f"{plugin}:"
    gone = []
    for event in hooks_file.EVENTS:
        entries = hooks["hooks"].get(event, [])
        kept = []
        for e in entries:
            firsts = [hooks_file.words(h.get("command"), event)[:1] for h in e.get("hooks", [])]
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


def laid_before(hooks: dict[str, Any]) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    """Each subagent the hooks lay lanes in, as `<plugin>:<subagent>`, with its lanes as steps of a
    proposal, each lane once, though held on both events; and each lane laid that lane does not lay
    now, as said for lane:up to put to the building AI."""
    agents: dict[str, list[dict[str, Any]]] = {}
    left = []
    for event in hooks_file.EVENTS:
        for e in hooks.get("hooks", {}).get(event, []):
            for h in e.get("hooks", []):
                given = hooks_file.words(h.get("command"), event)
                steps = agents.setdefault(given[0], []) if given else []
                for w in given[1:]:
                    lane = hooks_file.lane_of(w)
                    if lane is None:
                        name = given[0].split(":")[1]
                        left.append(
                            f"Left out `{w}` from the hook of {name}, as lane {placed.lane_version()} lays"
                            " no such lane; ask the building AI whether to lay it again or leave it"
                            " out.\n"
                        )
                        continue
                    number, kind, takes = lane
                    s = {"step": number, "lanes": [{"lane": kind, "takes": takes}]}
                    if s not in steps:
                        steps.append(s)
    return agents, list(dict.fromkeys(left))
