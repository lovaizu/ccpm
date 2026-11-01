"""The lanes laid in a plugin, kept in its hooks/lanes.json in the shape of the proposal, with the
flow where one is laid: written by the layer, and read by the guard and the layer, so what was
approved is what is read, and a thing taken holds any text, a comma among the rest."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import hook
import lanes
import schema

# The flow's JSON Schema, as lane's docs/flow.md gives it: the orchestrator, its step the flow is
# laid on, the subagents in the order they start, one named again where it starts again, and the
# answers that send the work back, each subagent of a back named by its position in the order.
FLOW = {
    "type": "object",
    "required": ["orchestrator", "step", "order"],
    "additionalProperties": False,
    "properties": {
        "orchestrator": {
            "type": "string",
            "description": "the subagent that starts the others, as its file's name: field",
        },
        "step": {
            "type": "integer",
            "minimum": 1,
            "description": "the orchestrator's step the flow is laid on",
        },
        "order": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string"},
            "description": "the subagents in the order they start, each as its file's name: field",
        },
        "back": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["from", "to", "while"],
                "additionalProperties": False,
                "properties": {
                    "from": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "the position in order, from 1, whose answer sends the work"
                        " back",
                    },
                    "to": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "the position in order, from 1, the work goes back to",
                    },
                    "while": {
                        "type": "string",
                        "minLength": 1,
                        "description": "the answer that sends it back",
                    },
                },
            },
        },
    },
}
# The flow held whole, as hooks/lanes.json or a proposal holds it under `flow`.
FLOWED = {"type": "object", "properties": {"flow": FLOW}}
# The lane the flow is laid as, on the orchestrator's step, which the layer alone lays.
FLOW_LANE = {"lane": "follow_flow", "takes": []}


def lanes_shape(least: int) -> dict[str, Any]:
    """The JSON Schema of the lanes laid in a plugin, as hooks/lanes.json holds them and a proposal
    gives them: each subagent by its name, with each step its lanes are laid on, by its number, and
    each lane, its name and what it takes; a lane that reads a port may name the plugin's adapter of
    it, and a subagent its adapter of the values port, as every lane of the subagent reads them,
    each by its path in the plugin. Each list of subagents, steps and lanes holds at least `least`:
    0 in hooks/lanes.json, which holds none once every subagent laid in is gone, 1 in a
    proposal."""

    def listed(each: dict[str, Any]) -> dict[str, Any]:
        return {"type": "array", "items": each, "minItems": least}

    def adapter(port: str) -> dict[str, Any]:
        return {"type": "string", "description": f"hooks/adapters/{port}-<name>.py"}

    lane = {
        "type": "object",
        "required": ["lane", "takes"],
        "additionalProperties": False,
        "properties": {
            "lane": {"enum": list(lanes.LANES)},
            "takes": {"type": "array", "items": {"type": "string"}},
            "adapter": adapter("<port>"),
        },
    }
    step = {
        "type": "object",
        "required": ["step", "lanes"],
        "additionalProperties": False,
        "properties": {
            "step": {"type": "integer", "description": "its number in the subagent's Steps"},
            "lanes": listed(lane),
        },
    }
    subagent = {
        "type": "object",
        "required": ["name", "steps"],
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string", "description": "the subagent, as its file's name: field"},
            "adapter": adapter("values"),
            "steps": listed(step),
        },
    }
    flow = {"type": "object", "description": "your subagents' order, as docs/flow.md gives it"}
    return {
        "type": "object",
        "required": ["subagents"],
        "additionalProperties": False,
        "properties": {"flow": flow, "subagents": listed(subagent)},
    }


LAID = lanes_shape(0)


def laid(root: str) -> dict[str, Any]:
    """The lanes laid in the plugin at root, as its hooks/lanes.json holds them; stops with
    ValueError saying what is wrong where it is not there, holds no JSON, is not in the shape LAID
    gives, gives a flow that cannot be laid, as `flow_wrong` says, lays a lane taking an empty
    thing, or another count of things than the lane holds, lays the flow's lane on a step the flow
    is not laid on, or names an adapter that cannot be its port's, as `adapter_wrong` says."""
    path = os.path.join(root, "hooks", "lanes.json")
    try:
        with open(path, encoding="utf-8") as f:
            given = json.load(f)
    except OSError:
        raise ValueError("hooks/lanes.json is not there") from None
    except ValueError:
        raise ValueError("hooks/lanes.json holds no JSON") from None
    out = schema.held(LAID, given) or schema.held(FLOWED, given)
    if out is not None:
        raise ValueError(f"hooks/lanes.json is out of its shape at {out.told()}")
    flow = given.get("flow")
    why = flow_wrong(flow)
    if why:
        raise ValueError(f"hooks/lanes.json gives a flow {why}")
    flowed = (flow["orchestrator"], flow["step"]) if flow else None
    for agent in given["subagents"]:
        wrong = adapter_wrong(agent.get("adapter"), "values")
        if wrong:
            raise ValueError(f"hooks/lanes.json names an adapter for {agent['name']} {wrong}")
        for s in agent["steps"]:
            for lane in s["lanes"]:
                on = f"{lane['lane']} on step {s['step']} of {agent['name']}"
                if not all(lane["takes"]) or not lanes.fits(lane["lane"], lane["takes"]):
                    raise ValueError(
                        f"hooks/lanes.json gives {on} takes of another count than it holds, or"
                        " one empty"
                    )
                if lane["lane"] == FLOW_LANE["lane"] and (agent["name"], s["step"]) != flowed:
                    raise ValueError(f"hooks/lanes.json lays {on}, where no flow is laid")
                port = getattr(lanes.LANES[lane["lane"]], "PORT", None)
                wrong = adapter_wrong(lane.get("adapter"), port)
                if wrong:
                    raise ValueError(f"hooks/lanes.json names an adapter for {on} {wrong}")
    return given


def flow_wrong(flow: dict[str, Any] | None) -> str:
    """Why the flow, held to its schema, None for none, cannot be laid, as docs/flow.md says, so
    each answer leads to one move: its order names its orchestrator; a back names a position its
    order has not, goes to one not before its from, or answers a while of more than one line; or
    two backs are from one position; "" where it can."""
    if flow is None:
        return ""
    order = flow["order"]
    if flow["orchestrator"] in order:
        return f"whose order names its orchestrator {flow['orchestrator']}"
    froms: list[int] = []
    for back in flow.get("back", []):
        source, to = back["from"], back["to"]
        past = [n for n in (source, to) if n > len(order)]
        if past:
            n = len(order)
            return f"whose back names position {past[0]}, which its order of {n} does not have"
        if to >= source:
            return (
                f"whose back from position {source} goes to position {to}, which does not come"
                " before it"
            )
        if source in froms:
            return f"with two backs from position {source}"
        froms.append(source)
        # A line break of any kind ends a line as moves.py reads the answer's lines.
        if back["while"] not in back["while"].splitlines():
            return f"whose back from position {source} answers a while of more than one line"
    return ""


def froms(flow: dict[str, Any] | None) -> list[str]:
    """Each subagent at the from of a back of the flow, once each, whose answer sends the work
    back; none where there is no flow."""
    order = (flow or {}).get("order", [])
    return list(dict.fromkeys(order[b["from"] - 1] for b in (flow or {}).get("back", [])))


def adapter_wrong(path: str | None, port: str | None) -> str:
    """Why the adapter named by the path, None for none, cannot be the port's, the port a lane
    reads, None for none; "" where none is named or it can, being `hooks/adapters/<port>-<name>.py`
    in the plugin."""
    if path is None:
        return ""
    if port is None:
        return f"`{path}`, which reads no port"
    if not re.fullmatch(rf"hooks/adapters/{port}-{hook.NAME}\.py", path):
        return f"`{path}`, not hooks/adapters/{port}-<name>.py"
    return ""


def subagent(given: dict[str, Any], name: str) -> dict[str, Any]:
    """The lanes laid in the subagent of the name, of the lanes laid as `laid` reads them; stops
    with ValueError where they lay no lanes in the subagent."""
    found = next((a for a in given["subagents"] if a["name"] == name), None)
    if found is None:
        raise ValueError(f"hooks/lanes.json lays no lanes in {name}")
    return found


def lanes_of(agent: dict[str, Any]) -> list[tuple[int, str, list[str], str | None]]:
    """Each lane laid in the subagent, as `subagent` reads it: its step, the lane, what it takes
    and the adapter it names, None for none."""
    return [
        (int(s["step"]), g["lane"], g["takes"], g.get("adapter"))
        for s in agent["steps"]
        for g in s["lanes"]
    ]


def lanes_written(
    root: str,
    agents: dict[str, list[dict[str, Any]]],
    values: dict[str, str | None],
    flow: dict[str, Any] | None,
) -> None:
    """Writes the flow, where one is given, and the lanes laid in each subagent, by
    `<plugin>:<name>`, as steps of a proposal, with the adapter of the values port values names for
    it, where it names one, into the plugin's hooks/lanes.json, in the shape of the proposal,
    indented by two."""
    subagents = [
        {"name": a.split(":")[1], **({"adapter": values[a]} if values.get(a) else {}), "steps": s}
        for a, s in agents.items()
    ]
    laid = {**({"flow": flow} if flow else {}), "subagents": subagents}
    os.makedirs(os.path.join(root, "hooks"), exist_ok=True)
    with open(os.path.join(root, "hooks", "lanes.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(laid, indent=2, ensure_ascii=False) + "\n")
