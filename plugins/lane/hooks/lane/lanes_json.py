"""The lanes laid in a plugin, kept in its hooks/lanes.json in the shape of the proposal: written
by the layer, and read by the guard and the layer, so what was approved is what is read, and a thing
taken holds any text, a comma among the rest."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import hook
import lanes
import schema


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
    return {
        "type": "object",
        "required": ["subagents"],
        "additionalProperties": False,
        "properties": {"subagents": listed(subagent)},
    }


LAID = lanes_shape(0)


def laid(root: str) -> dict[str, Any]:
    """The lanes laid in the plugin at root, as its hooks/lanes.json holds them; stops with
    ValueError saying what is wrong where it is not there, holds no JSON, is not in the shape LAID
    gives, lays a lane taking an empty thing, or another count of things than the lane holds, or
    names an adapter that cannot be its port's, as `adapter_wrong` says."""
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
                port = getattr(lanes.LANES[lane["lane"]], "PORT", None)
                wrong = adapter_wrong(lane.get("adapter"), port)
                if wrong:
                    raise ValueError(f"hooks/lanes.json names an adapter for {on} {wrong}")
    return given


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


def subagent(root: str, name: str) -> dict[str, Any]:
    """The lanes laid in the subagent of the name, as the plugin at root's hooks/lanes.json holds
    them; stops with ValueError, as `laid` does, or where the file lays no lanes in the subagent."""
    found = next((a for a in laid(root)["subagents"] if a["name"] == name), None)
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
    root: str, agents: dict[str, list[dict[str, Any]]], values: dict[str, str | None]
) -> None:
    """Writes the lanes laid in each subagent, by `<plugin>:<name>`, as steps of a proposal, with
    the adapter of the values port values names for it, where it names one, into the plugin's
    hooks/lanes.json, in the shape of the proposal, indented by two."""
    subagents = [
        {"name": a.split(":")[1], **({"adapter": values[a]} if values.get(a) else {}), "steps": s}
        for a, s in agents.items()
    ]
    os.makedirs(os.path.join(root, "hooks"), exist_ok=True)
    with open(os.path.join(root, "hooks", "lanes.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"subagents": subagents}, indent=2, ensure_ascii=False) + "\n")
