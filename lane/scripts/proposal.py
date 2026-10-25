"""The proposal the building AI writes for the layer, a JSON file at a path it gives lay.py, read
and held to its JSON Schema, PROPOSAL, which lane's docs/lanes.md shows, then checked for what no
schema can say: the plugin and each subagent's file found, each name one a hook's command can carry,
each subagent and step given once, each step in its file, and what each lane takes fitting it; and
each adapter it names found beside it, in `<plugin>/adapters/` of the folder it is in, or laid
before in the plugin's hooks/adapters/, and run on each of its cases before the proposal is printed
or written."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import hooks_file
import lanes
import placed
import ports
import schema
import step

# What the proposal is told to be, when it is not: in the shape lane's docs/lanes.md gives, named by
# its whole path, as the building AI may run lay.py from any folder.
LANES_MD = os.path.join(placed.LANE, "docs", "lanes.md")
AGAIN = f"write the proposal again in the shape {LANES_MD} gives"
# The proposal's JSON Schema: the lanes laid, as hooks/lanes.json holds them, with the plugin's
# folder, and at least one subagent, one step in each and one lane on each, as a proposal lays them.
SHAPE = hooks_file.lanes_shape(1)
PROPOSAL = {
    **SHAPE,
    "required": ["plugin", *SHAPE["required"]],
    "properties": {
        "plugin": {"type": "string", "description": "your plugin's folder"},
        **SHAPE["properties"],
    },
}


class Stop(Exception):
    """What was wrong, and what to do, where lay.py cannot go on."""


def wrong(what: str) -> Stop:
    """The stop saying what is wrong with the proposal."""
    return Stop(f"lay.py: the proposal {what}; {AGAIN}.")


def proposal(path: str) -> dict[str, Any]:
    """The proposal at the path, held to its schema and checked, each subagent given once, with
    the plugin's name, each subagent with its file and its lines, each step with where it is among
    them, and each adapter it names found and checked on its cases, as `adapter_found` gives it."""
    try:
        with open(path, encoding="utf-8") as f:
            given = json.load(f)
    except OSError:
        raise Stop(f"lay.py: there is no file {path}; {AGAIN}.") from None
    except ValueError:
        raise Stop(f"lay.py: {path} holds no JSON; {AGAIN}.") from None
    out = schema.held(PROPOSAL, given)
    if out is not None:
        raise wrong(f"is out of its shape at {out.told()}")
    root = given["plugin"]
    name, checked = plugin_name(root), []
    for given_agent in given["subagents"]:
        agent = subagent(root, given_agent)
        # A subagent given twice would be written twice, its file and its hook the second time from
        # the second's lanes alone, and the first's lost though the building AI approved them.
        if agent["name"] in [a["name"] for a in checked]:
            raise wrong(f"gives {agent['name']} twice, where each subagent comes once")
        checked.append(agent)
    folder = os.path.join(os.path.dirname(os.path.abspath(path)), name, "adapters")
    named = adapters_named(checked)
    found = [adapter_found(root, folder, a, port, by) for a, (port, by) in named.items()]
    return {"plugin": root, "name": name, "subagents": checked, "adapters": found}


def adapters_named(agents: list[dict[str, Any]]) -> dict[str, tuple[str, str]]:
    """Each adapter the subagents name, by its path in the plugin, with the port it is of and what
    names it, the first of those that do."""
    named: dict[str, tuple[str, str]] = {}
    for agent in agents:
        if "adapter" in agent:
            named.setdefault(agent["adapter"], ("values", f"the values of {agent['name']}"))
        for s in agent["steps"]:
            for lane in s["lanes"]:
                if "adapter" in lane:
                    on = f"{lane['lane']} on step {s['step']} of {agent['name']}"
                    # A lane naming an adapter reads a port, as the lane's check before has it.
                    kind: Any = lanes.LANES[lane["lane"]]
                    named.setdefault(lane["adapter"], (kind.PORT, on))
    return named


def adapter_found(root: str, folder: str, path: str, port: str, by: str) -> dict[str, Any]:
    """The adapter of the path in the plugin, of the port, named by what is said, found beside the
    proposal in the adapters' folder given, or laid before in the plugin, and checked on each of its
    cases: its path, its port, what names it, the file it is read from and is written from, its
    text, its cases, and whether it is beside the proposal, to be written into the plugin. Stops
    where it is in neither, where its cases are not a list of at least one
    `{"given": ..., "gives": ...}` whose given holds to its port's JSON in, or where it gives on
    any case other than the case gives, saying the case and what it gave."""
    base = os.path.basename(path)
    beside = os.path.join(folder, base)
    kept_beside = os.path.isfile(beside)
    source = beside if kept_beside else os.path.join(root, path)
    if not os.path.isfile(source):
        raise Stop(
            f"lay.py: the proposal names the adapter {path}, for {by}, which is neither {beside}"
            f" nor in {root}; write it there with its cases, and run again."
        )
    cases_file = os.path.splitext(source)[0] + ".json"
    cases = adapter_cases(cases_file, port)
    for number, case in enumerate(cases, 1):
        try:
            gave: Any = ports.run(source, port, case["given"], ports.TIME)
        except ports.Failed as failed:
            gave = str(failed)
        if gave != case["gives"]:
            shown = gave if isinstance(gave, str) else f"gave {json.dumps(gave)}"
            raise Stop(
                f"lay.py: the adapter {path}, for {by}, given case {number} of {cases_file},"
                f" {json.dumps(case['given'])}, {shown}, where the case gives"
                f" {json.dumps(case['gives'])}; fix the adapter or its case, and run again."
            )
    with open(source, encoding="utf-8") as f:
        text = f.read()
    found = {"path": path, "port": port, "by": by, "source": source, "text": text, "cases": cases}
    return {**found, "beside": kept_beside}


def adapter_cases(path: str, port: str) -> list[dict[str, Any]]:
    """The cases at the path an adapter of the port must give; stops where they are not a list of
    at least one case, each `{"given": <the port's JSON in>, "gives": <the port's JSON out>}`."""
    case = ports.shape(given=ports.PORTS[port]["in"], gives=ports.PORTS[port]["out"])
    try:
        with open(path, encoding="utf-8") as f:
            given = json.load(f)
    except (OSError, ValueError):
        given = None
    if not isinstance(given, list) or not given:
        raise Stop(
            f"lay.py: {path} gives the adapter no cases; write there a list of at least one"
            ' `{"given": ..., "gives": ...}` of the port, and run again.'
        )
    for number, each in enumerate(given, 1):
        out = schema.held(case, each)
        if out is not None:
            raise Stop(
                f"lay.py: case {number} of {path} is out of the {port} port at {out.told()};"
                " fix it, and run again."
            )
    return given


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


def subagent(root: str, given: dict[str, Any]) -> dict[str, Any]:
    """A subagent of the proposal, held to its schema, checked, each of its steps given once, with
    its file and its lines, and each step with where it is among them."""
    name = given["name"]
    if not re.fullmatch(hooks_file.NAME, name):
        raise wrong("gives a subagent no name")
    why = hooks_file.adapter_wrong(given.get("adapter"), "values")
    if why:
        raise wrong(f"names an adapter for the values of {name} {why}")
    file = step.agent_file(root, name)
    if file is None:
        raise wrong(f"gives {name}, which no file in agents/ names")
    with open(file, encoding="utf-8") as f:
        lines = f.read().splitlines(keepends=True)
    steps = given["steps"]
    numbers = []
    for s in steps:
        number = s["step"]
        # A step given twice would be printed as two readings of it and written with the sentences
        # of one, so the step would say what no print showed.
        if number in numbers:
            raise wrong(f"gives step {number} of {name} twice, where each step comes once")
        numbers.append(number)
        where = step.span([line.rstrip("\n") for line in lines], number)
        if where is None:
            raise wrong(f"gives step {number}, which the Steps of {name} do not have")
        for lane in s["lanes"]:
            lane_check(lane, f"step {number} of {name}", root)
        s["span"] = where
    named = {"adapter": given["adapter"]} if "adapter" in given else {}
    return {"name": name, **named, "file": file, "lines": lines, "steps": steps}


def lane_check(lane: dict[str, Any], on: str, root: str) -> None:
    """Stops where the lane, held to its schema, takes an empty thing, or another count of things
    than its wording and its hook hold, or names an adapter that cannot be its port's; or where its
    module refuses what it takes in the plugin at root, as in_form a form lane does not read."""
    known, takes = lane["lane"], lane["takes"]
    if not all(takes):
        raise wrong(f"gives {known} on {on} a take that is empty")
    if not lanes.fits(known, takes):
        raise wrong(
            f"gives {known} on {on} takes of another count than its wording and its hook hold"
        )
    port = getattr(lanes.LANES[known], "PORT", None)
    why = hooks_file.adapter_wrong(lane.get("adapter"), port)
    if why:
        raise wrong(f"names an adapter for {known} on {on} {why}")
    refused = getattr(lanes.LANES[known], "refused", None)
    why = refused(takes, root) if refused is not None else ""
    if why:
        raise Stop(f"lay.py: {known} on {on} {why}; fix it or the proposal and run again.")
