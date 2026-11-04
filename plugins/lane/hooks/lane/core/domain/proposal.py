"""The proposal the developer AI writes for lay.py, a JSON file at a path it gives: read and held to
its JSON Schema, PROPOSAL, which docs/lanes.md shows, then checked for what no schema can say: the
plugin and each subagent's file found, each name one a hook's command can carry, each subagent and
step given once, each step in its file, and each lane taking at least one thing, none empty; and
the routes held to their JSON Schema, which docs/routes.md shows, and checked as it says, against
the files of the subagents they name. What this version of lane does not lay yet, such as an
adapter or a lane other than run_only and write_only, is refused, so nothing is laid that no check
would hold."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import lanes
import ports
import routes
import rules
import schema
import step
import template
from lanes import run_only

# What the proposal is told to be, when it is not: in the shape docs/lanes.md gives, named by its
# whole path, as the developer AI may run lay.py from any folder.
# Lane's folder, as lay.py runs this module from Lane: four above its own, core/domain/ in
# hooks/lane/.
LANE = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 4))
LANES_MD = os.path.join(LANE, "docs", "lanes.md")
AGAIN = f"write the proposal again in the shape {LANES_MD} gives"
ROUTES_MD = os.path.join(LANE, "docs", "routes.md")
ROUTES_AGAIN = f"write the routes again as {ROUTES_MD} says"
# The proposal's JSON Schema, as docs/lanes.md gives it.
NAMED = list(lanes.LANES)
TAKES = {"type": "array", "items": {"type": "string"}}
PROPOSAL = {
    **rules.shape(
        ["plugin"],
        {
            "plugin": {"type": "string", "description": "your plugin's folder"},
            "routes": {
                "type": "object",
                "description": "your subagents' routes, as docs/routes.md gives them",
            },
            "subagents": rules.subagents(NAMED, TAKES, 1, True),
        },
    ),
    "anyOf": [{"required": ["subagents"]}, {"required": ["routes"]}],
}


# The lane that reads a port, by its name, with the port; the values port is read by the subagent.
PORTS = {"every_item": "items"}
# How a proposal names an adapter, by its path in the plugin.
ADAPTER = re.compile(r"hooks/adapters/(?P<port>[a-z]+)-[A-Za-z0-9_-]+\.py")


class Stop(Exception):
    """What was wrong, and what to do, where lay.py cannot go on."""


def wrong(what: str, again: str = AGAIN) -> Stop:
    """The stop saying what is wrong with the proposal, and how to write it again."""
    return Stop(f"lay.py: the proposal {what}; {again}.")


def proposal(path: str) -> dict[str, Any]:
    """The proposal at the path, held to its schema and checked: the plugin's folder, its name, and
    each subagent with its file, its lines, and each step with where it is among them."""
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
    name = plugin_name(root)
    # Where the developer AI keeps the proposal's adapters, beside it.
    beside = os.path.join(os.path.dirname(path), name, "adapters")
    checked: list[dict[str, Any]] = []
    for each in given.get("subagents", []):
        agent = subagent(root, each, beside)
        # A subagent given twice would be written twice, the second time from the second's lanes
        # alone, and the first's lost though the developer AI approved them.
        if agent["name"] in [a["name"] for a in checked]:
            raise wrong(f"gives {agent['name']} twice, where each subagent comes once")
        checked.append(agent)
    routed = routes_checked(root, given["routes"]) if "routes" in given else None
    for agent in checked:
        if "results" in agent and routed is not None and routes.ons(routed, agent["name"]):
            raise wrong(
                f"gives {agent['name']} its own results, though routes are from it; give its"
                " results in the routes alone"
            )
    return {"plugin": root, "name": name, "subagents": checked, "routes": routed}


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
    if not isinstance(name, str) or not re.fullmatch(rules.NAME, name):
        raise Stop(
            f"lay.py: {manifest} names the plugin by no name of letters, digits and -._; fix it"
            " and run again."
        )
    return name


def agent_lines(root: str, name: str, again: str = AGAIN) -> tuple[str, list[str]]:
    """The file the steps of the subagent of the name are in, its entry or its part, and its lines;
    stops where the name is none a hook's command can carry, no file in the plugin's agents/ gives
    it, or the part its entry names is not there."""
    if not re.fullmatch(rules.NAME, name):
        raise wrong("gives a subagent no name", again)
    file = step.steps_file(root, name)
    if file is None:
        raise wrong(f"gives {name}, which no file in agents/ names", again)
    if not os.path.isfile(file):
        shown = os.path.relpath(file, root)
        raise wrong(f"gives {name}, whose entry names its part {shown}, which is not there", again)
    with open(file, encoding="utf-8") as f:
        return file, f.read().splitlines(keepends=True)


def entry_lines(root: str, name: str) -> list[str]:
    """The lines of the entry of the subagent of the name, which `agent_lines` has found."""
    with open(str(step.agent_file(root, name)), encoding="utf-8") as f:
        return f.read().splitlines()


def routes_checked(root: str, given: dict[str, Any]) -> dict[str, Any]:
    """The routes, held to their schema, checked as `routes.refused` says, and then against the
    files of the subagents they name: the orchestrator's step in its file, its tools, where named,
    with Agent; no subagent they name set to run in the foreground; and each subagent giving a
    result with a last step; a dependency's subagent as `dependency_checked` says."""
    out = schema.held(rules.ROUTES, given)
    if out is not None:
        raise wrong(f"is out of its shape at $.routes{out.told()[1:]}", ROUTES_AGAIN)
    why = routes.refused(given)
    if why and why == routes.unordered(given):
        raise wrong(why, f"order them there, as {ROUTES_MD} says, and run again")
    if why:
        raise wrong(why, ROUTES_AGAIN)
    lead = given["orchestrator"]
    froms = routes.giving(given)
    for name in routes.named(given):
        if ":" in name:
            dependency_checked(root, name)
            continue
        _, lines = agent_lines(root, name, ROUTES_AGAIN)
        bare = [line.rstrip("\n") for line in lines]
        # routes.named gives the orchestrator as the routes give it, so `is` finds it as `==`.
        orchestrating = name == lead  # pragma: no mutate
        if orchestrating and step.span(bare, given["step"]) is None:
            raise wrong(
                f"gives step {given['step']}, which the Steps of {lead} do not have", ROUTES_AGAIN
            )
        entry = entry_lines(root, name)
        tools = template.value(entry, "tools")
        named = [t.strip() for t in tools.split(",")] if tools is not None else ["Agent"]
        if orchestrating and not ("Agent" in named or any(t.startswith("Agent(") for t in named)):
            raise wrong(
                f"gives {lead} as the orchestrator, whose file names its tools without Agent,"
                " which it starts each subagent with",
                ROUTES_AGAIN,
            )
        if name in froms and step.last(bare) is None:
            raise wrong(f"gives {name}, whose file has no step to end by its result", ROUTES_AGAIN)
        in_background(root, name, ROUTES_MD)
    return given


def dependency_checked(root: str, name: str) -> None:
    """Stops where the name of a dependency's subagent the routes give, `<dependency>:<name>`,
    names no subagent, or a dependency the plugin's manifest does not declare. Its file lies in the
    dependency, whose own proposal lays it, so lay.py reads none of it."""
    if not re.fullmatch(f"{rules.NAME}:{rules.NAME}", name):
        raise wrong(f"gives {name}, which names no subagent", ROUTES_AGAIN)
    dependency = name.split(":")[0]
    if dependency not in run_only.dependencies(root):
        raise wrong(
            f"gives {name}, a subagent of {dependency}, which .claude-plugin/plugin.json does not"
            " declare among its dependencies",
            f"declare it there, as {ROUTES_MD} says, and run again",
        )


def in_background(root: str, name: str, told: str = LANES_MD) -> None:
    """Stops where the file of the subagent of the name, which `agent_lines` has found, does not
    set `background: true`, telling to set it as the document `told` says: lane tells each run of
    the subagent from the others by the ID its start gives back, which a start in the background
    gives at once."""
    entry = str(step.agent_file(root, name))
    if not step.background(entry):
        shown = os.path.relpath(entry, root)
        raise wrong(
            f"gives {name}, whose file {shown} does not set `background: true`, which lane needs"
            " to tell each of its runs from the others",
            f"set `background: true` in its frontmatter, as {told} says, and run again",
        )


def subagent(root: str, given: dict[str, Any], beside: str = "") -> dict[str, Any]:
    """A subagent of the proposal, held to its schema, checked, with the file its steps are in and
    its lines, each step with where it is among them, and each adapter it names, as `adapter`
    finds it in the folder beside the proposal."""
    name = given["name"]
    adapters = []
    if "adapter" in given:
        adapters.append(adapter(given["adapter"], "values", root, beside, f"{name}"))
    file, lines = agent_lines(root, name)
    in_background(root, name)
    numbers: list[int] = []
    for s in given["steps"]:
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
            on = f"step {number} of {name}"
            lane_check(lane, on, root)
            if "adapter" in lane:
                if lane["lane"] not in PORTS:
                    raise wrong(f"gives {lane['lane']} on {on} an adapter, though it reads no port")
                adapters.append(adapter(lane["adapter"], PORTS[lane["lane"]], root, beside, on))
        s["span"] = where
    found = {"name": name, "file": file, "lines": lines, "steps": given["steps"]}
    named = {k: given[k] for k in ("adapter", "results") if k in given}
    return {**found, **named, "adapters": adapters}


def lane_check(lane: dict[str, Any], on: str, root: str) -> None:
    """Stops where the lane, held to its schema, on the step `on` names, is one lanes/ refuses, as
    `lanes.refused` says."""
    kind = lane["lane"]
    why = lanes.refused(kind, lane["takes"], root)
    if why.declare:
        raise wrong(
            f"gives {kind} on {on} {why.said}",
            f"declare it there, as {LANES_MD} says, and run again",
        )
    if why.said:
        space = "" if why.said.startswith(",") else " "
        raise wrong(f"gives {kind} on {on}{space}{why.said}")


def adapter(named: str, port: str, root: str, beside: str, on: str) -> dict[str, Any]:
    """The adapter of the port named on `on`, as `hooks/adapters/<port>-<name>.py`, found in the
    folder beside the proposal with its cases, `<port>-<name>.json`, and run on each of them, the
    plugin at root: its path in the plugin, its source and its cases' source, and how many cases
    it gave as they say. Stops where it is named otherwise, is not there, its cases are not there
    or not in their shape, none gives nothing, or it gives a case otherwise than it says."""
    found = ADAPTER.fullmatch(named)
    if found is None or found["port"] != port:
        raise wrong(f"names the adapter {named} on {on}, not as hooks/adapters/{port}-<name>.py")
    source = os.path.join(beside, os.path.basename(named))
    cases_source = os.path.splitext(source)[0] + ".json"
    if not os.path.isfile(source):
        raise wrong(f"names the adapter {named}, which is not at {source}")
    try:
        with open(cases_source, encoding="utf-8") as f:
            cases = json.load(f)
    except OSError:
        raise wrong(f"names the adapter {named}, whose cases are not at {cases_source}") from None
    except ValueError:
        raise wrong(f"names the adapter {named}, whose cases {cases_source} hold no JSON") from None
    shape = {
        "type": "array",
        "minItems": 1,
        "items": rules.shape(
            ["given", "gives"],
            {"given": ports.PORTS[port]["in"], "gives": ports.PORTS[port]["out"]},
        ),
    }
    out = schema.held(shape, cases)
    if out is not None:
        raise wrong(
            f"names the adapter {named}, whose cases are out of their shape at {out.told()}"
        )
    if not any(not next(iter(c["gives"].values())) for c in cases):
        raise wrong(f"names the adapter {named}, whose cases have none that gives nothing")
    for number, case in enumerate(cases, 1):
        try:
            gave = ports.run(source, port, case["given"], root, ports.TIME)
        except ports.Failed as why:
            raise wrong(f"names the adapter {named}, which on its case {number} {why}") from None
        if gave != case["gives"]:
            raise wrong(
                f"names the adapter {named}, which on its case {number} gave"
                f" {json.dumps(gave)}, not {json.dumps(case['gives'])}"
            )
    return {"path": named, "source": source, "cases": cases_source, "count": len(cases)}
