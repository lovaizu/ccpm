"""The proposal lane:up writes for the layer, read and checked to be as lane:up's steps give it, a
JSON file lane:up keeps in lane's data folder, `${CLAUDE_PLUGIN_DATA}/<plugin>.json`:

    {"plugin": "<the plugin's folder>",
     "subagents": [{"name": "<subagent>",
                    "steps": [{"step": <number>,
                               "lanes": [{"lane": "<lane>", "takes": ["<thing>", ...]}]}]}]}
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import hooks_file
import lanes
import step

# What the proposal is told to be, when it is not.
AGAIN = "write the proposal again as lane:up's steps give it"


class Stop(Exception):
    """What was wrong, and what to do, where lay.py cannot go on."""


def wrong(what: str) -> Stop:
    """The stop saying what is wrong with the proposal."""
    return Stop(f"lay.py: the proposal {what}; {AGAIN}.")


def proposal(path: str) -> dict[str, Any]:
    """The proposal at the path, checked to be as lane:up writes it, with the plugin's name, and
    each subagent with its file and its lines, and each step with where it is among them."""
    try:
        with open(path, encoding="utf-8") as f:
            given = json.load(f)
    except OSError:
        raise Stop(f"lay.py: there is no file {path}; {AGAIN}.") from None
    except ValueError:
        raise Stop(f"lay.py: {path} holds no JSON; {AGAIN}.") from None
    root = given.get("plugin") if isinstance(given, dict) else None
    if not isinstance(root, str):
        raise wrong("names no plugin")
    subagents = given.get("subagents")
    if not isinstance(subagents, list) or not subagents:
        raise wrong("gives no subagents")
    return {
        "plugin": root,
        "name": plugin_name(root),
        "subagents": [subagent(root, s) for s in subagents],
    }


def plugin_name(root: str) -> str:
    """The plugin's name, from its manifest, as a hook's command can carry it unquoted."""
    manifest = os.path.join(root, ".claude-plugin", "plugin.json")
    try:
        with open(manifest, encoding="utf-8") as f:
            given = json.load(f)
    except OSError:
        raise wrong(f"names {root} as the plugin, which has no {manifest}") from None
    except ValueError:
        raise Stop(f"lay.py: {manifest} holds no JSON; fix it and run again.") from None
    name = given.get("name") if isinstance(given, dict) else None
    if not isinstance(name, str) or not re.fullmatch(hooks_file.NAME, name):
        raise Stop(
            f"lay.py: {manifest} names the plugin by no name of letters, digits and -._; fix it"
            " and run again."
        )
    return name


def subagent(root: str, given: Any) -> dict[str, Any]:
    """A subagent of the proposal, checked, with its file and its lines, and each step with where
    it is among them."""
    name = given.get("name") if isinstance(given, dict) else None
    if not isinstance(name, str) or not re.fullmatch(hooks_file.NAME, name):
        raise wrong("gives a subagent no name")
    file = step.agent_file(root, name)
    if file is None:
        raise wrong(f"gives {name}, which no file in agents/ names")
    with open(file, encoding="utf-8") as f:
        lines = f.read().splitlines(keepends=True)
    steps = given.get("steps")
    if not isinstance(steps, list) or not steps:
        raise wrong(f"gives {name} no steps")
    for s in steps:
        number = s.get("step") if isinstance(s, dict) else None
        if not isinstance(number, int):
            raise wrong(f"gives a step of {name} no number")
        where = step.span([line.rstrip("\n") for line in lines], number)
        if where is None:
            raise wrong(f"gives step {number}, which the Steps of {name} do not have")
        laid = s.get("lanes")
        if not isinstance(laid, list) or not laid:
            raise wrong(f"gives step {number} of {name} no lanes")
        for lane in laid:
            lane_check(lane, f"step {number} of {name}", root)
        s["span"] = where
    return {"name": name, "file": file, "lines": lines, "steps": steps}


def lane_check(lane: Any, on: str, root: str) -> None:
    """Stops where the lane is not one lane lays, taking a text with no comma for each thing it
    shows; or where its module refuses what it takes in the plugin at root, as in_form a form lane
    does not read."""
    known = lane.get("lane") if isinstance(lane, dict) else None
    if known not in lanes.LANES:
        raise wrong(f"gives {known}, which is no lane, on {on}")
    takes = lane.get("takes")
    if not isinstance(takes, list):
        raise wrong(f"gives {known} on {on} no takes")
    if not all(isinstance(t, str) and t and "," not in t for t in takes):
        raise wrong(f"gives {known} on {on} takes that are not each a text with no comma")
    if not lanes.fits(known, takes):
        raise wrong(
            f"gives {known} on {on} takes of another count than its wording and its hook hold"
        )
    refused = getattr(lanes.LANES[known], "refused", None)
    why = refused(takes, root) if refused is not None else ""
    if why:
        raise Stop(f"lay.py: {known} on {on} {why}; fix it or the proposal and run again.")
