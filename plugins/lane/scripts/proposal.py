"""The proposal the building AI writes for the layer, a JSON file at a path it gives lay.py, read
and held to its JSON Schema, PROPOSAL, which lane's docs/lanes.md shows, with its flow held to the
one docs/flow.md shows, then checked for what no schema can say: the plugin and each subagent's file
found, each name one a hook's command can carry, each subagent and step given once, each step in its
file, what each lane takes fitting it, and the flow one that can be laid, its lane laid by the layer
alone; and each adapter it names found beside it, in `<plugin>/adapters/` of the folder it is in, or
laid before in the plugin's hooks/adapters/, and run on each of its cases before the proposal is
printed or written. The flow's follow_next lane is put among the orchestrator's lanes, from the flow
the proposal gives or, where it gives none, the one laid before."""

from __future__ import annotations

import copy
import json
import os
import re
from typing import Any

import call
import hook
import lanes
import lanes_json
import placed
import ports
import schema
import shell
import step
import template

# What the proposal is told to be, when it is not: in the shape lane's docs/lanes.md gives, named by
# its whole path, as the building AI may run lay.py from any folder.
LANES_MD = os.path.join(placed.LANE, "docs", "lanes.md")
AGAIN = f"write the proposal again in the shape {LANES_MD} gives"
# The proposal's JSON Schema: the lanes laid, as hooks/lanes.json holds them, with the plugin's
# folder, and at least one subagent, one step in each and one lane on each, as a proposal lays them,
# or a flow, or both.
SHAPE = lanes_json.lanes_shape(1)
PROPOSAL = {
    **SHAPE,
    "required": ["plugin"],
    "anyOf": [{"required": ["subagents"]}, {"required": ["flow"]}],
    "properties": {
        "plugin": {"type": "string", "description": "your plugin's folder"},
        **SHAPE["properties"],
    },
}


# The tool the orchestrator starts each subagent of the flow with.
AGENT = "Agent"


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
    out = schema.held(PROPOSAL, given) or schema.held(lanes_json.FLOWED, given)
    if out is not None:
        raise wrong(f"is out of its shape at {out.told()}")
    root = given["plugin"]
    name, checked = plugin_name(root), []
    flow = given.get("flow")
    if flow is not None:
        flow_check(root, flow)
    for given_agent in given.get("subagents", []):
        agent = subagent(root, given_agent)
        # A subagent given twice would be written twice, its file and its hook the second time from
        # the second's lanes alone, and the first's lost though the building AI approved them.
        if agent["name"] in [a["name"] for a in checked]:
            raise wrong(f"gives {agent['name']} twice, where each subagent comes once")
        laid_by_hand(root, agent)
        checked.append(agent)
    # A flow laid before is kept where the proposal gives none, so a subagent of it the proposal
    # gives keeps its lane among those given.
    kept = laid(root).get("flow") if flow is None else flow
    if kept is not None:
        checked = with_flow(root, kept, checked, flow is not None)
    parts_shared(root, checked)
    folder = os.path.join(os.path.dirname(os.path.abspath(path)), name, "adapters")
    named = adapters_named(checked)
    found = [adapter_found(root, folder, a, port, by) for a, (port, by) in named.items()]
    return {
        "plugin": root,
        "name": name,
        "subagents": checked,
        "adapters": found,
        "flow": kept,
        "flow_given": flow is not None,
    }


def laid(root: str) -> dict[str, Any]:
    """The lanes laid in the plugin at root, with the flow where one is laid, as its
    hooks/lanes.json holds them; none where it is not there. Stops where it is there and cannot be
    read, as the lanes approved would be lost."""
    if not os.path.exists(os.path.join(root, "hooks", "lanes.json")):
        return {"subagents": []}
    try:
        return lanes_json.laid(root)
    except ValueError as why:
        raise Stop(f"lay.py: {root}/{why}; fix it and run again.") from None


def flow_check(root: str, flow: dict[str, Any]) -> None:
    """Stops where the flow, held to its schema, cannot be laid in the plugin at root: where
    lanes_json.flow_wrong says why, where it names a subagent no file in the plugin's agents/ names,
    by a name a hook's command can carry, where the orchestrator's file names its tools without
    Agent, which it starts the others with, or where that file says `flow.py` stands for anything
    but lane's script, which the flow's lane takes by that name."""
    why = lanes_json.flow_wrong(flow)
    if why:
        raise wrong(f"gives a flow {why}")
    for named in [flow["orchestrator"], *flow["order"]]:
        if not re.fullmatch(hook.NAME, named) or step.agent_file(root, named) is None:
            raise wrong(f"gives a flow naming {named}, which no file in agents/ names")
    orchestrator = flow["orchestrator"]
    entry = str(step.agent_file(root, orchestrator))
    with open(entry, encoding="utf-8") as f:
        tools = template.value(f.read().splitlines(), "tools")
    # A file naming no tools has them all, Agent among them, as Claude Code gives a subagent.
    if tools and AGENT not in [t.strip() for t in tools.split(",")]:
        raise Stop(
            f"lay.py: {entry} names the tools of {orchestrator}, `{tools}`, without {AGENT}, with"
            f" which it starts the subagents of the flow; add {AGENT} to them, and run again."
        )
    lies = step.bindings(root, orchestrator).get(lanes_json.FLOW_PY, lanes_json.FLOW_RUN)
    if lies != lanes_json.FLOW_RUN:
        raise Stop(
            f"lay.py: {entry} says `{lanes_json.FLOW_PY}` below is"
            f" `{lies}`, where the flow's lane takes lane's, `{lanes_json.FLOW_RUN}`; name the"
            " script of its own otherwise, and run again."
        )


def parts_shared(root: str, checked: list[dict[str, Any]]) -> None:
    """Stops where two subagents whose entries name one part lay different lanes on a step of it,
    of the subagents checked, each with the lanes the proposal gives it, and each other subagent
    the plugin at root lays lanes in and its agents/ still has, with the lanes laid before in it:
    the part carries one set of sentences, which the layer writes and the guard reads for each."""
    given = {a["name"]: (a["file"], a["steps"]) for a in checked}
    for agent in laid(root)["subagents"]:
        name = agent["name"]
        file = step.steps_file(root, name)
        if name not in given and file is not None:
            given[name] = (file, agent["steps"])
    first: dict[str, tuple[str, dict[int, Any]]] = {}
    for name, (file, steps) in given.items():
        on = {s["step"]: s["lanes"] for s in steps}
        before, other = first.setdefault(file, (name, on))
        differ = sorted(n for n in {*on, *other} if on.get(n) != other.get(n))
        if differ:
            raise Stop(
                f"lay.py: {before} and {name} share the part {file}, which carries one set of"
                f" sentences, and lay different lanes on step {differ[0]} of it; give each the"
                " same lanes on each step of it, and run again."
            )


def laid_by_hand(root: str, agent: dict[str, Any]) -> None:
    """Stops where the subagent of the proposal, checked, lays follow_next taking lane's flow.py,
    by the name the flow's lane takes it by or as the subagent's entry says it stands for, as the
    layer lays that lane from the flow alone."""
    bindings = step.bindings(root, agent["name"])
    for s in agent["steps"]:
        for lane in s["lanes"]:
            if lane["lane"] != lanes_json.FLOW_LANE["lane"]:
                continue
            said = [shell.words(t) for t in step.bound(lane["takes"], bindings)]
            if any(
                w[:1] == [lanes_json.FLOW_PY] or call.starts(w, lanes_json.FLOW_RUN) for w in said
            ):
                raise wrong(
                    f"lays follow_next taking {lanes_json.FLOW_PY} on step {s['step']} of"
                    f" {agent['name']}, which lay.py lays from the flow"
                )


def with_flow(
    root: str, flow: dict[str, Any], checked: list[dict[str, Any]], given: bool
) -> list[dict[str, Any]]:
    """The subagents checked with the flow's follow_next lane put among the orchestrator's lanes,
    on the flow's step, after any lane the step has: the orchestrator's as the proposal gives it,
    in its place; or, where the proposal does not give it, its lanes laid before, that lane of a
    flow laid before left out, first, where the proposal gives the flow, as the subagents given
    then; the subagents checked alone where it gives neither."""
    name = flow["orchestrator"]
    at = next((n for n, a in enumerate(checked) if a["name"] == name), None)
    if at is None and not given:
        return checked
    if at is None:
        before = next((a for a in laid(root)["subagents"] if a["name"] == name), {"steps": []})
        raw = copy.deepcopy({**before, "name": name})
        for s in raw["steps"]:
            s["lanes"] = [g for g in s["lanes"] if g != lanes_json.FLOW_LANE]
        raw["steps"] = [s for s in raw["steps"] if s["lanes"]]
    else:
        raw = {k: v for k, v in checked[at].items() if k in ("name", "adapter")}
        raw["steps"] = [{"step": s["step"], "lanes": s["lanes"]} for s in checked[at]["steps"]]
    on = next((s for s in raw["steps"] if s["step"] == flow["step"]), None)  # pragma: no mutate
    if on is None:
        on = {"step": flow["step"], "lanes": []}
        raw["steps"].append(on)
    on["lanes"] = [*on["lanes"], copy.deepcopy(lanes_json.FLOW_LANE)]
    agent = subagent(root, raw)
    return [agent, *checked] if at is None else [*checked[:at], agent, *checked[at + 1 :]]


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
            gave: Any = ports.run(source, port, case["given"], root, ports.TIME)
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
    if not isinstance(name, str) or not re.fullmatch(hook.NAME, name):
        raise Stop(
            f"lay.py: {manifest} names the plugin by no name of letters, digits and -._; fix it"
            " and run again."
        )
    return name


def subagent(root: str, given: dict[str, Any]) -> dict[str, Any]:
    """A subagent of the proposal, held to its schema, checked, each of its steps given once, with
    the file its steps are in, as step.steps_file finds it, and its lines, and each step with where
    it is among them."""
    name = given["name"]
    if not re.fullmatch(hook.NAME, name):
        raise wrong("gives a subagent no name")
    why = lanes_json.adapter_wrong(given.get("adapter"), "values")
    if why:
        raise wrong(f"names an adapter for the values of {name} {why}")
    entry = step.agent_file(root, name)
    if entry is None:
        raise wrong(f"gives {name}, which no file in agents/ names")
    file = step.steps_file(root, name) or entry
    if not os.path.isfile(file):
        raise Stop(
            f"lay.py: the entry of {name}, {entry}, names its part {file}, which is not there;"
            " write it, or name the part there is, and run again."
        )
    with open(file, encoding="utf-8") as f:
        lines = f.read().splitlines(keepends=True)
    steps = given["steps"]
    # A name the subagent's part uses is read as its entry says it stands for.
    bindings = step.bindings(root, name)
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
            lane_check(lane, f"step {number} of {name}", root, bindings)
        s["span"] = where
    named = {"adapter": given["adapter"]} if "adapter" in given else {}
    return {"name": name, **named, "file": file, "lines": lines, "steps": steps}


def lane_check(lane: dict[str, Any], on: str, root: str, bindings: dict[str, str]) -> None:
    """Stops where the lane, held to its schema, takes an empty thing, or another count of things
    than its wording and its hook hold, or names an adapter that cannot be its port's; or where its
    module refuses what it takes in the plugin at root, read through the bindings of its
    subagent's entry, as in_form a form lane does not read."""
    known, takes = lane["lane"], lane["takes"]
    if not all(takes):
        raise wrong(f"gives {known} on {on} a take that is empty")
    if not lanes.fits(known, takes):
        raise wrong(
            f"gives {known} on {on} takes of another count than its wording and its hook hold"
        )
    port = getattr(lanes.LANES[known], "PORT", None)
    why = lanes_json.adapter_wrong(lane.get("adapter"), port)
    if why:
        raise wrong(f"names an adapter for {known} on {on} {why}")
    refused = getattr(lanes.LANES[known], "refused", None)
    why = refused(step.bound(takes, bindings), root) if refused is not None else ""
    if why:
        raise Stop(f"lay.py: {known} on {on} {why}; fix it or the proposal and run again.")
